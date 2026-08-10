"""
Servicio API Backend FastAPI para 'Mi Coche por Dentro'.
Expone endpoints REST y WebSocket para control de captura, adaptador, sesiones, DTCs y análisis.
"""
import asyncio
import hashlib
import logging
import os
import threading
import polars as pl
from collections import deque
from datetime import datetime
from typing import List, Dict, Any, Literal, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from starlette.middleware.trustedhost import TrustedHostMiddleware
from urllib.parse import urlsplit

from app_paths import APP_VERSION, backups_path, load_environment, resource_path

load_environment()

from database.db import DatabaseManager
from database.parquet_store import TelemetryStore
from database.exporter import VehicleBackupExporter
from collector.adapter_manager import AdapterManager, AdapterState
from collector.pid_discovery import PIDDiscovery
from collector.metric_catalog import metric_catalog_for_vehicle
from collector.poller import TelemetryPoller
from collector.capture_profiles import CaptureProfileManager
from collector.vag_bkp_catalog import DOCUMENTED_GROUPS, category_for_group
from collector.simulator import FailureSimulator
from collector.mode06 import Mode06Analyzer
from collector.adapter_compatibility import build_adapter_compatibility
from collector.vag_readonly import VagReadOnlyClient, capability_rows, ensure_definition_template
from collector.vag_kwp2000 import (
    ALL_KWP_SIGNALS,
    KWP_SIGNALS,
    RUNTIME_KWP_SIGNALS,
    VagKwp2000Client,
    is_legacy_kwp_calibration,
    normalize_vag_part_number,
)
from analysis.statistics import SignalStatistics
from analysis.event_analyzer import EventWindowAnalyzer
from analysis.rules_engine import RuleEngine
from analysis.protocols import ProtocolManager
from analysis.ai_service import AIService
from analysis.comparator import SessionComparator
from analysis.report_generator import ReportGenerator
from analysis.session_quality import SessionQualityCalculator
from analysis.diagnostic_summary import DiagnosticSummary
from analysis.dtc_translations import describe_dtc_in_spanish
from analysis.historical_baseline import HistoricalBaselineService
from analysis.trip_metrics import TripMetrics

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mi Coche por Dentro — API Local OBD-II & IA",
    version=APP_VERSION,
    description="API local para monitorización de telemetría OBD-II, gestión de garaje y análisis determinista."
)


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["127.0.0.1", "localhost", "testserver"],
)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(?:127\.0\.0\.1|localhost)(?::\d{1,5})?$",
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


def _is_allowed_browser_origin(origin: Optional[str]) -> bool:
    """Accept only the local dashboard as a browser/WebSocket origin."""
    if not origin:
        return True  # Native clients and the automated test client omit Origin.
    try:
        parsed = urlsplit(origin)
        if parsed.scheme not in {"http", "https"}:
            return False
        if parsed.hostname not in {"127.0.0.1", "localhost"}:
            return False
        return parsed.port is None or 1 <= parsed.port <= 65535
    except ValueError:
        return False


@app.middleware("http")
async def add_local_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
        "connect-src 'self' ws://127.0.0.1:* ws://localhost:*; "
        "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
    )
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response

# Instancias globales del sistema
db = DatabaseManager()
telemetry_store = TelemetryStore()
adapter = AdapterManager()
rule_engine = RuleEngine()
historical_baselines = HistoricalBaselineService(
    db,
    telemetry_store,
    lambda frame, powertrain: rule_engine.evaluate_session(
        frame,
        powertrain_type=powertrain,
    ),
)
recovered_session_count = db.recover_interrupted_sessions()
if recovered_session_count:
    logger.warning(
        "Se recuperaron %s sesiones que habían quedado abiertas.",
        recovered_session_count,
    )

active_poller: Optional[TelemetryPoller] = None
active_session_id: Optional[str] = None
connected_websockets: List[WebSocket] = []
live_samples = deque(maxlen=1200)
live_samples_lock = threading.Lock()
last_capture_error: Optional[Dict[str, Any]] = None
manufacturer_probe_cache: Dict[str, Dict[str, Any]] = {}


def _is_vag_vehicle(vehicle: Dict[str, Any]) -> bool:
    make = str(vehicle.get("make", "")).strip().lower()
    return make in {"volkswagen", "vw", "audi", "seat", "skoda", "škoda"}


def _save_capability(vehicle_id: str, item: Dict[str, Any]) -> None:
    incoming_source = str(item.get("source", "obd_generic"))
    if incoming_source == "obd_generic":
        existing = next(
            (
                row for row in db.list_vehicle_capabilities(vehicle_id)
                if row.get("pid_name") == item.get("pid_name")
            ),
            None,
        )
        # RPM, velocidad y refrigerante también existen en los bloques VAG.
        # Una prevalidación OBD genérica no debe borrar ese mapeo ya verificado.
        if existing and existing.get("supported_verified") and str(existing.get("source", "")).startswith("vag_kwp2000"):
            return
    db.upsert_vehicle_capability(
        vehicle_id=vehicle_id,
        pid_name=item["pid_name"],
        mode=item.get("mode", ""),
        pid=item.get("pid", ""),
        supported_reported=item.get("supported_reported", False),
        supported_verified=item.get("supported_verified", False),
        unit=item.get("unit", ""),
        avg_latency_ms=item.get("avg_latency_ms", 0.0),
        success_rate=item.get("success_rate", 0.0),
        source=item.get("source", "obd_generic"),
        status=item.get("status", ""),
        reason=item.get("reason", ""),
        ecu_address=item.get("ecu_address", ""),
        label=item.get("label", ""),
        category=item.get("category", ""),
        group_title=item.get("group_title", ""),
        group_number=item.get("group_number"),
        position=item.get("position"),
        type_id=item.get("type_id", ""),
        sample_value=item.get("sample_value"),
        raw_response=item.get("raw_response", ""),
    )


def _promote_kwp_capabilities(vehicle_id: str, df: Any) -> None:
    """Conserva como verificadas las señales que el coche entregó al capturar."""
    if df is None or df.is_empty() or not {"pid", "value", "data_source"}.issubset(df.columns):
        return
    definitions = {definition.pid_name: definition for definition in RUNTIME_KWP_SIGNALS}
    valid = df.filter(
        pl.col("value").is_not_null()
        & pl.col("data_source").cast(pl.String).str.starts_with("measured_vag_kwp2000")
    )
    if valid.is_empty():
        return
    for pid_name in valid["pid"].unique().to_list():
        definition = definitions.get(str(pid_name))
        if definition is None:
            continue
        rows = valid.filter(valid["pid"] == pid_name)
        latency = float(rows["latency_ms"].mean()) if "latency_ms" in rows.columns else 0.0
        _save_capability(vehicle_id, {
            "pid_name": definition.pid_name,
            "mode": "KWP_21",
            "pid": f"{definition.group:03d}.{definition.position + 1}",
            "unit": definition.unit,
            "supported_reported": True,
            "supported_verified": True,
            "avg_latency_ms": latency,
            "success_rate": 1.0,
            "source": "vag_kwp2000_capture",
            "status": "compatible",
            "reason": "VERIFICADA_DURANTE_CAPTURA_REAL",
            "ecu_address": "01/TP2.0",
        })


def _reconnect_adapter_on_same_port() -> bool:
    """Restaura OBD-II normal tras usar el transporte Volkswagen TP2.0."""
    port = adapter.active_port
    if not port:
        return False
    adapter.disconnect()
    return adapter.connect(port)


def _finalize_aborted_capture() -> None:
    global active_poller, active_session_id, last_capture_error
    if not active_poller or active_poller.is_running or not active_poller.abort_reason:
        return
    session_id = active_session_id
    transport_requires_reconnect = bool(
        active_poller.oem_reader
        and getattr(active_poller.oem_reader, "transport_requires_reconnect", False)
    )
    active_poller.stop()
    capture_metrics = active_poller.get_metrics()
    if session_id:
        session = db.get_session(session_id) or {}
        captured = telemetry_store.load_session_dataframe(session_id)
        _promote_kwp_capabilities(str(session.get("vehicle_id", "")), captured)
        data_lost = active_poller.abort_reason == "OBD_DATA_LOST"
        reason = (
            "Captura detenida: se perdió la comunicación con la ECU durante la ruta y no pudo recuperarse."
            if data_lost
            else "Captura detenida automáticamente: la ECU no entregó lecturas OBD válidas."
        )
        db.fail_session(
            session_id,
            reason,
            data_file=telemetry_store.get_session_file_path(session_id),
            requested_signal_count=int(capture_metrics.get("requested_signal_count", 0)),
            captured_signal_count=int(capture_metrics.get("captured_signal_count", 0)),
            capture_coverage_percent=float(capture_metrics.get("capture_coverage_percent", 0.0)),
        )
    last_capture_error = {
        "code": active_poller.abort_reason,
        "message": (
            "La captura se detuvo tras 20 segundos sin completar ninguna lectura válida. Revisa el contacto y el adaptador."
            if active_poller.abort_reason == "OBD_DATA_LOST"
            else "La captura se detuvo porque no llegó ninguna lectura OBD válida."
        ),
        "technical_detail": active_poller.last_read_error,
        "session_id": session_id,
    }
    active_poller = None
    active_session_id = None
    if transport_requires_reconnect:
        _reconnect_adapter_on_same_port()
    adapter.set_state(AdapterState.VEHICLE_CONNECTED if adapter.connection else AdapterState.ERROR)


def _preserve_active_capture_on_shutdown() -> None:
    """Vuelca los datos pendientes y deja constancia de un cierre durante la captura."""
    global active_poller, active_session_id
    if not active_poller or not active_session_id:
        return
    session_id = active_session_id
    try:
        active_poller.stop()
        db.interrupt_session(
            session_id,
            "Captura conservada al cerrar la aplicación antes de finalizarla",
        )
        logger.info("Captura %s conservada como interrumpida.", session_id)
    except Exception:
        logger.exception("No se pudo conservar completamente la captura activa.")
    finally:
        active_poller = None
        active_session_id = None


app.router.add_event_handler("shutdown", _preserve_active_capture_on_shutdown)

# --- MODELOS PYDANTIC ---
class VehicleCreate(BaseModel):
    display_name: Optional[str] = Field(default="", max_length=100)
    make: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=1886, le=datetime.now().year + 1)
    generation: Optional[str] = Field(default="", max_length=60)
    variant: Optional[str] = Field(default="", max_length=100)
    engine: Optional[str] = Field(default="", max_length=100)
    engine_code: Optional[str] = Field(default="", max_length=50)
    fuel_type: Optional[str] = Field(default="", max_length=40)
    powertrain_type: Literal["gasoline", "diesel", "hybrid", "phev", "bev"] = "gasoline"
    market: str = Field(default="EU", min_length=2, max_length=20)

    @field_validator(
        "display_name", "make", "model", "generation", "variant",
        "engine", "engine_code", "fuel_type", "market", mode="before"
    )
    @classmethod
    def strip_vehicle_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("engine_code")
    @classmethod
    def normalize_engine_code(cls, value):
        return value.upper() if value else value

class SessionStart(BaseModel):
    vehicle_id: str = Field(min_length=1, max_length=100)
    profile_id: Optional[str] = Field(default=None, max_length=100)
    engine_condition: Literal["cold", "warm", "hot"] = "warm"
    notes: str = Field(default="", max_length=500)
    title: str = Field(default="", max_length=100)
    symptom: str = Field(default="", max_length=500)
    odometer_km: Optional[float] = Field(default=None, ge=0, le=5_000_000)

class SessionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)
    symptom: Optional[str] = Field(default=None, max_length=500)
    odometer_km: Optional[float] = Field(default=None, ge=0, le=5_000_000)
    engine_condition: Optional[Literal["cold", "warm", "hot"]] = None

    @field_validator("title", "notes", "symptom", mode="before")
    @classmethod
    def strip_session_text(cls, value):
        return value.strip() if isinstance(value, str) else value

class ConnectRequest(BaseModel):
    com_port: Optional[str] = Field(default=None, max_length=120)

class EventMarkerCreate(BaseModel):
    timestamp_offset_ms: int = Field(ge=0, le=86_400_000)
    event_type: str = Field(min_length=1, max_length=50)
    note: Optional[str] = Field(default="", max_length=500)

# --- ENDPOINTS ---

@app.get("/health")
def health_check():
    dashboard_available = bool(getattr(app.state, "dashboard_available", False))
    if not dashboard_available:
        raise HTTPException(status_code=503, detail="Dashboard estático no disponible.")
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "dashboard": "available",
    }


@app.get("/api/status")
def get_system_status():
    _finalize_aborted_capture()
    return {
        "status": "online",
        "adapter": adapter.get_status(),
        "active_session_id": active_session_id,
        "is_recording": active_poller is not None and active_poller.is_running,
        "capture_metrics": active_poller.get_metrics() if active_poller else None,
        "capture_error": last_capture_error,
    }

@app.get("/api/adapter/ports")
def list_ports():
    return {"ports": adapter.list_available_ports()}

@app.get("/api/adapter/status")
def get_adapter_status():
    return adapter.get_status()


@app.get("/api/adapter/compatibility")
def get_adapter_compatibility():
    return build_adapter_compatibility(adapter.get_status())

@app.post("/api/adapter/connect")
def connect_adapter(req: ConnectRequest):
    success = adapter.connect(com_port=req.com_port)
    status = adapter.get_status()
    return {
        "success": success,
        "status": status,
        "message": (
            "Adaptador conectado y ECU detectada."
            if success
            else status.get("last_error") or "No se pudo conectar con la ECU."
        ),
    }

@app.post("/api/adapter/disconnect")
def disconnect_adapter():
    adapter.disconnect()
    return {"success": True, "status": adapter.get_status()}

# --- VEHÍCULOS ---
@app.get("/api/vehicles")
def list_vehicles():
    return db.list_vehicles()

@app.post("/api/vehicles")
def create_vehicle(v: VehicleCreate):
    fuel_labels = {
        "gasoline": "Gasolina",
        "diesel": "Diésel",
        "hybrid": "Híbrido",
        "phev": "Híbrido enchufable",
        "bev": "Eléctrico",
    }
    display_name = v.display_name or f"{v.make} {v.model} {v.year}"
    return db.create_vehicle(
        display_name=display_name,
        make=v.make,
        model=v.model,
        year=v.year,
        engine=v.engine or "",
        engine_code=v.engine_code or "",
        generation=v.generation or "",
        variant=v.variant or "",
        fuel_type=v.fuel_type or fuel_labels[v.powertrain_type],
        powertrain_type=v.powertrain_type,
        market=v.market.upper(),
    )


@app.get("/api/vehicles/{vehicle_id}/baseline")
def get_vehicle_baseline(
    vehicle_id: str,
    session_id: Optional[str] = None,
):
    if not db.get_vehicle(vehicle_id):
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    if session_id:
        session = db.get_session(session_id)
        if not session or session.get("vehicle_id") != vehicle_id:
            raise HTTPException(
                status_code=404,
                detail="La sesión no pertenece al vehículo seleccionado.",
            )
        return historical_baselines.compare_session(session_id)
    return historical_baselines.build(vehicle_id)

@app.get("/api/vehicles/{vehicle_id}/supported-pids")
def discover_pids(vehicle_id: str):
    discovery = PIDDiscovery(adapter_connection=adapter.connection)
    pids = discovery.discover_supported_pids()
    verified = [pid for pid in pids if pid.get("supported_verified")]
    # Una pérdida transitoria de comunicación no debe borrar capacidades que
    # ya se habían verificado en una captura real anterior.
    for pid in pids if verified else []:
        _save_capability(vehicle_id, {**pid, "source": "obd_generic"})
    manufacturer = [
        item for item in db.list_vehicle_capabilities(vehicle_id)
        if str(item.get("source", "")).startswith("vag_")
    ]
    return {"vehicle_id": vehicle_id, "supported_pids": pids + manufacturer}


@app.post("/api/vehicles/{vehicle_id}/manufacturer-probe")
def probe_manufacturer_data(vehicle_id: str):
    """Detecta UDS o KWP2000 y prueba exclusivamente servicios de lectura."""
    vehicle = db.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    if not _is_vag_vehicle(vehicle):
        raise HTTPException(status_code=400, detail="La prueba del fabricante solo está disponible para vehículos del Grupo Volkswagen.")
    if not adapter.get_status()["is_connected"] or adapter.connection is None:
        raise HTTPException(status_code=409, detail="Conecta el Vgate al coche y da el contacto antes de identificar la centralita.")
    if active_poller and active_poller.is_running:
        raise HTTPException(status_code=409, detail="Finaliza la captura antes de ejecutar la identificación Volkswagen.")

    ensure_definition_template()
    uds_client = VagReadOnlyClient(adapter.connection)
    standard_identity = uds_client.identify_standard_obd()
    calibration_id = standard_identity.get("CALIBRATION_ID", "")
    used_tp20 = is_legacy_kwp_calibration(calibration_id)
    if used_tp20:
        client = VagKwp2000Client(adapter.connection)
        try:
            result = client.probe(standard_identity=standard_identity)
        except Exception as exc:
            logger.exception("Falló la identificación VAG KWP2000/TP2.0")
            result = {
                "protocol": "VAG KWP2000 sobre TP2.0, solo lectura",
                "ecu_address": "01/TP2.0",
                "identified": True,
                "ecu_part_number": str(calibration_id),
                "standard_obd_identity": standard_identity,
                "identity": [],
                "live_signals": [],
                "verified_live_signal_count": 0,
                "mapping_required_count": len(KWP_SIGNALS),
                "probe_error": str(exc),
                "safety": "No se enviaron servicios de escritura, codificación, adaptación, rutinas ni borrado.",
                "transcript": client.transport.transcript,
            }
        finally:
            restored = _reconnect_adapter_on_same_port()
        result["standard_obd_restored"] = restored
    else:
        result = uds_client.probe(standard_identity=standard_identity)
    result.update({
        "vehicle_id": vehicle_id,
        "vehicle": vehicle.get("display_name", ""),
        "adapter_protocol": adapter.get_status().get("protocol"),
    })
    configured_engine = str(vehicle.get("engine_code", "") or "").upper()
    normalized_calibration = normalize_vag_part_number(calibration_id)
    if used_tp20 and (
        "03G906018FG" in normalized_calibration
        or normalized_calibration.startswith("3G906018FG")
    ):
        corrected = db.update_vehicle_identification(
            vehicle_id,
            engine="BKP 2.0 TDI 103 kW (inyector-bomba)",
            engine_code="BKP",
        )
        result["detected_engine_code"] = "BKP"
        result["vehicle_record_corrected"] = bool(corrected)
    if used_tp20 and configured_engine and configured_engine not in {"BKP", "BMP", "BMN", "BMR", "BUY", "BUZ"}:
        result["vehicle_configuration_warning"] = (
            f"La ficha indica motor {configured_engine}, pero la identificación OBD "
            f"{calibration_id} pertenece a la familia 03G-906-018 con KWP2000. "
            "Comprueba el código de motor de la pegatina o documentación del vehículo."
        )
    manufacturer_probe_cache[vehicle_id] = result
    if result.get("live_signals"):
        for capability in capability_rows(result):
            _save_capability(vehicle_id, capability)
    return result


@app.get("/api/vehicles/{vehicle_id}/manufacturer-probe")
def get_manufacturer_probe(vehicle_id: str):
    vehicle = db.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    cached = manufacturer_probe_cache.get(vehicle_id)
    capabilities = [
        item for item in db.list_vehicle_capabilities(vehicle_id)
        if str(item.get("source", "")).startswith("vag_")
    ]
    if str(vehicle.get("engine_code", "")).upper() in {"BKP", "BMP", "BMN", "BMR", "BUY", "BUZ"}:
        known_names = {item.get("pid_name") for item in capabilities}
        capabilities.extend(
            {
                "pid_name": definition.pid_name,
                "label": definition.label,
                "category": category_for_group(definition.group),
                "group_title": "",
                "group_number": definition.group,
                "position": definition.position + 1,
                "mode": "KWP_21",
                "pid": f"{definition.group:03d}.{definition.position + 1}",
                "unit": definition.unit,
                "supported_reported": False,
                "supported_verified": False,
                "status": "not_tested",
                "reason": "SE_COMPROBARA_EN_LA_PROXIMA_IDENTIFICACION",
                "source": "vag_kwp2000_pending",
                "ecu_address": "01/TP2.0",
            }
            for definition in ALL_KWP_SIGNALS
            if definition.pid_name not in known_names
        )
    if cached is None and capabilities:
        verified_count = sum(bool(item.get("supported_verified")) for item in capabilities)
        tested_groups = {
            item.get("group_number") for item in capabilities
            if item.get("group_number") is not None and item.get("status") != "not_tested"
        }
        responding_groups = {
            item.get("group_number") for item in capabilities
            if item.get("supported_reported") and item.get("group_number") is not None
        }
        category_summary: Dict[str, Dict[str, int]] = {}
        for item in capabilities:
            category = item.get("category") or "Sin clasificar"
            summary = category_summary.setdefault(category, {"total": 0, "verified": 0, "unavailable": 0})
            summary["total"] += 1
            if item.get("supported_verified"):
                summary["verified"] += 1
            else:
                summary["unavailable"] += 1
        cached = {
            "protocol": "VAG KWP2000 sobre TP2.0, solo lectura",
            "identified": verified_count > 0,
            "verified_live_signal_count": verified_count,
            "mapping_required_count": sum(item.get("status") == "not_tested" for item in capabilities),
            "tested_group_count": len(tested_groups),
            "documented_group_count": len(DOCUMENTED_GROUPS),
            "responding_group_count": len(responding_groups),
            "tested_field_count": len(capabilities),
            "coverage_percent": round(100.0 * verified_count / len(capabilities), 1) if capabilities else 0.0,
            "category_summary": category_summary,
            "live_signals": capabilities,
        }
    return {
        "vehicle_id": vehicle_id,
        "applicable": _is_vag_vehicle(vehicle),
        "last_probe": cached,
        "capabilities": capabilities,
    }


@app.get("/api/vehicles/{vehicle_id}/metric-catalog")
def get_vehicle_metric_catalog(vehicle_id: str):
    """Devuelve todos los candidatos conocidos, también los aún no resueltos."""
    vehicle = db.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    metrics = metric_catalog_for_vehicle(
        vehicle,
        db.list_vehicle_capabilities(vehicle_id),
    )
    confirmed = sum(bool(item.get("supported_verified")) for item in metrics)
    pending_statuses = {"not_tested", "mapping_required", "undecoded", "conditional"}
    pending = sum(str(item.get("status", "")) in pending_statuses for item in metrics)
    unavailable = len(metrics) - confirmed - pending
    return {
        "vehicle_id": vehicle_id,
        "metrics": metrics,
        "summary": {
            "catalogued": len(metrics),
            "confirmed": confirmed,
            "pending": pending,
            "unavailable": max(0, unavailable),
        },
    }


@app.get("/api/metric-catalog")
def get_base_metric_catalog():
    """Devuelve el catálogo universal incluso si el garaje todavía está vacío."""
    metrics = metric_catalog_for_vehicle({})
    pending_statuses = {"not_tested", "mapping_required", "undecoded", "conditional"}
    pending = sum(str(item.get("status", "")) in pending_statuses for item in metrics)
    return {
        "vehicle_id": None,
        "metrics": metrics,
        "summary": {
            "catalogued": len(metrics),
            "confirmed": 0,
            "pending": pending,
            "unavailable": max(0, len(metrics) - pending),
        },
    }


@app.get("/api/diagnostics/preflight")
def diagnostic_preflight(vehicle_id: str):
    vehicle = db.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")

    status = adapter.get_status()
    demo_mode = os.getenv("APP_MODE", "production").lower() in {"demo", "simulated"}
    if not demo_mode and (not status["is_connected"] or adapter.connection is None):
        return {
            "ready": False,
            "vehicle_id": vehicle_id,
            "checks": [
                {"id": "vehicle", "ok": True, "label": "Vehículo seleccionado"},
                {"id": "adapter", "ok": status["is_connected"], "label": "Adaptador OBD conectado"},
                {"id": "ecu", "ok": False, "label": "ECU respondiendo con datos reales"},
            ],
            "supported_pids": [],
            "message": "Conecta el adaptador al coche, da el contacto y repite la comprobación.",
        }

    pids = PIDDiscovery(adapter_connection=adapter.connection).discover_supported_pids()
    verified = [pid for pid in pids if pid.get("supported_verified")]
    # No degradar el historial completo si el contacto se quitó o la conexión
    # se quedó obsoleta durante esta comprobación.
    for pid in pids if verified else []:
        _save_capability(vehicle_id, {**pid, "source": "obd_generic"})
    manufacturer_capabilities = [
        item for item in db.list_vehicle_capabilities(vehicle_id)
        if str(item.get("source", "")).startswith("vag_")
    ]
    combined_pids = pids + manufacturer_capabilities
    ready = demo_mode or bool(verified)
    return {
        "ready": ready,
        "vehicle_id": vehicle_id,
        "checks": [
            {"id": "vehicle", "ok": True, "label": "Vehículo seleccionado"},
            {"id": "adapter", "ok": status["is_connected"] or demo_mode, "label": "Adaptador OBD conectado"},
            {"id": "ecu", "ok": ready, "label": "ECU respondiendo con datos válidos"},
        ],
        "supported_pids": combined_pids,
        "verified_pid_count": len(verified),
        "manufacturer_verified_count": sum(bool(item.get("supported_verified")) for item in manufacturer_capabilities),
        "message": (
            f"Prevalidación superada: {len(verified)} señales verificadas."
            if ready
            else "La ECU no respondió con ninguna señal válida. No se iniciará una captura vacía."
        ),
    }

# --- DTCs ---
def _quantity_as_number(value: Any):
    magnitude = getattr(value, "magnitude", value)
    unit = str(getattr(value, "units", "") or "")
    try:
        return round(float(magnitude), 4), unit
    except (TypeError, ValueError):
        return None, unit


def _read_freeze_frame(connection: Any) -> Dict[str, Any]:
    """Lee Modo 02 real y conserva solo parámetros numéricos decodificados."""
    import obd

    trigger_code = None
    parameters = []
    trigger_command = getattr(obd.commands, "DTC_FREEZE_DTC", None)
    if trigger_command is not None:
        response = connection.query(trigger_command)
        if response and not response.is_null():
            trigger_code = str(response.value)

    names = (
        "DTC_RPM",
        "DTC_SPEED",
        "DTC_ENGINE_LOAD",
        "DTC_COOLANT_TEMP",
        "DTC_INTAKE_TEMP",
        "DTC_INTAKE_PRESSURE",
        "DTC_MAF",
        "DTC_THROTTLE_POS",
        "DTC_SHORT_FUEL_TRIM_1",
        "DTC_LONG_FUEL_TRIM_1",
        "DTC_FUEL_PRESSURE",
        "DTC_FUEL_RAIL_PRESSURE_DIRECT",
        "DTC_CONTROL_MODULE_VOLTAGE",
    )
    for name in names:
        command = getattr(obd.commands, name, None)
        if command is None:
            continue
        try:
            if hasattr(connection, "supports") and not connection.supports(command):
                continue
            response = connection.query(command)
            if not response or response.is_null():
                continue
            value, unit = _quantity_as_number(response.value)
            if value is not None:
                parameters.append(
                    {
                        "parameter": name.removeprefix("DTC_"),
                        "value": value,
                        "unit": unit,
                        "source": "ECU_MODE_02",
                    }
                )
        except Exception:
            logger.debug("La ECU no respondió al parámetro freeze frame %s.", name)
    return {"trigger_code": trigger_code, "parameters": parameters}


def _perform_dtc_scan(
    vehicle_id: str,
    scan_type: str,
    *,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    if adapter.connection is None:
        raise RuntimeError("No hay una ECU conectada.")
    import obd

    by_code: Dict[str, Dict[str, Any]] = {}
    commands = (
        (obd.commands.GET_DTC, "confirmed"),
        (getattr(obd.commands, "GET_CURRENT_DTC", None), "pending"),
    )
    for command, status in commands:
        if command is None:
            continue
        response = adapter.connection.query(command)
        if not response or response.is_null():
            continue
        for code, description in response.value:
            code_text = str(code)
            by_code.setdefault(
                code_text,
                {
                    "code": code_text,
                    "status": status,
                    "description": describe_dtc_in_spanish(
                        code_text,
                        str(description),
                    ),
                    "raw_payload": "",
                },
            )
    dtcs = list(by_code.values())
    mil_status = bool(dtcs)
    try:
        status_response = adapter.connection.query(obd.commands.STATUS)
        if status_response and not status_response.is_null():
            mil_status = bool(getattr(status_response.value, "MIL", mil_status))
    except Exception:
        logger.debug("No se pudo leer el estado MIL; se conserva el estado derivado de DTC.")

    scan = db.record_dtc_scan(
        vehicle_id,
        scan_type,
        mil_status=mil_status,
        dtcs=dtcs,
        session_id=session_id,
    )
    freeze = {"trigger_code": None, "parameters": []}
    if dtcs:
        try:
            freeze = _read_freeze_frame(adapter.connection)
        except Exception:
            logger.exception("No se pudo leer el freeze frame de la ECU.")
        trigger = str(freeze.get("trigger_code") or "")
        record = next(
            (
                item
                for item in scan["records"]
                if str(item.get("code")) == trigger
            ),
            None,
        )
        if record:
            record["freeze_frame"] = []
            for parameter in freeze["parameters"]:
                saved_parameter = db.add_freeze_frame(
                    record["id"],
                    parameter["parameter"],
                    parameter["value"],
                    parameter.get("unit", ""),
                )
                record["freeze_frame"].append(saved_parameter)
    scan["dtcs"] = scan.pop("records")
    scan["freeze_frame"] = freeze
    scan["message"] = (
        "Escaneo leído directamente de la ECU y vinculado a la sesión."
        if session_id
        else "Escaneo leído directamente de la ECU."
    )
    return scan


@app.get("/api/dtc/scan")
def scan_dtc(vehicle_id: str, scan_type: str = "manual"):
    if not db.get_vehicle(vehicle_id):
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    if adapter.connection is None:
        raise HTTPException(status_code=409, detail="No hay una ECU conectada; no se generarán DTC simulados.")
    try:
        return _perform_dtc_scan(
            vehicle_id,
            scan_type,
            session_id=active_session_id if scan_type != "manual" else None,
        )
    except Exception as exc:
        logger.exception("No se pudieron leer los DTC de la ECU.")
        raise HTTPException(
            status_code=502,
            detail="No se pudieron leer los códigos de avería de la ECU.",
        ) from exc

# --- SESIONES Y CAPTURA ---
@app.get("/api/sessions")
def list_sessions(vehicle_id: Optional[str] = None):
    return db.list_sessions(vehicle_id=vehicle_id)


@app.get("/api/sessions/library")
def list_session_library(vehicle_id: Optional[str] = None):
    """Devuelve metadatos verificables para la biblioteca sin inventar resultados."""
    library = []
    for session in db.list_sessions(vehicle_id=vehicle_id):
        item = dict(session)
        item.update(
            {
                "sample_count": 0,
                "signal_count": 0,
                "duration_sec": 0.0,
                "data_sources": [],
                "alert_count": 0,
                "result_label": "Sin telemetría",
            }
        )
        try:
            df = telemetry_store.load_session_dataframe(session["id"])
            if df is not None and not df.is_empty():
                valid_df = df.filter(df["value"].is_not_null())
                item["sample_count"] = valid_df.height
                item["signal_count"] = (
                    valid_df["pid"].n_unique() if "pid" in valid_df.columns else 0
                )
                if "timestamp_monotonic" in valid_df.columns and valid_df.height:
                    timestamps = valid_df["timestamp_monotonic"]
                    item["duration_sec"] = round(
                        float(timestamps.max() or 0) - float(timestamps.min() or 0),
                        1,
                    )
                if "data_source" in valid_df.columns:
                    item["data_sources"] = sorted(
                        str(value)
                        for value in valid_df["data_source"].drop_nulls().unique().to_list()
                    )
                vehicle = db.get_vehicle(session["vehicle_id"]) or {}
                findings = rule_engine.evaluate_session(
                    valid_df,
                    powertrain_type=vehicle.get("powertrain_type", "gasoline"),
                )
                item["alert_count"] = sum(
                    1
                    for finding in findings
                    if finding.get("severity") in {"warning", "critical"}
                )
                quality = float(session.get("capture_quality_score") or 0)
                item["result_label"] = (
                    "Requiere revisión"
                    if item["alert_count"]
                    else "Datos fiables"
                    if quality >= 75
                    else "Calidad limitada"
                )
        except Exception:
            logger.exception(
                "No se pudo resumir la sesión %s para la biblioteca.",
                session["id"],
            )
            item["result_label"] = "Datos no disponibles"
        if session.get("status") == "interrupted":
            item["result_label"] = "Captura interrumpida"
        elif session.get("status") == "error":
            item["result_label"] = "Captura con error"
        library.append(item)
    return library

@app.post("/api/sessions/start")
def start_session(s: SessionStart):
    global active_poller, active_session_id, last_capture_error
    if active_poller and active_poller.is_running:
        raise HTTPException(status_code=400, detail="Ya hay una sesión de captura en ejecución.")
    demo_mode = os.getenv("APP_MODE", "production").lower() in {"demo", "simulated"}
    if not demo_mode and (not adapter.get_status()["is_connected"] or adapter.connection is None):
        raise HTTPException(
            status_code=409,
            detail="No se puede iniciar: conecta el adaptador y verifica que la ECU responde.",
        )

    profile = CaptureProfileManager.get_profile(s.profile_id or "COMPLETE_DIAGNOSTIC")
    vehicle = db.get_vehicle(s.vehicle_id) or {}
    capability_records = db.list_vehicle_capabilities(s.vehicle_id)
    verified_capabilities = {
        item["pid_name"]
        for item in capability_records
        if item.get("supported_verified")
    }
    requested_pids = list(profile["pids"])
    # Una integración avanzada no debe perder una métrica porque el perfil se
    # diseñó antes que su catálogo. Toda capacidad verificada, estándar u OEM,
    # se incorpora; el planificador conserva frecuencias distintas para no
    # convertir más cobertura en más carga innecesaria del bus.
    for item in capability_records:
        if item.get("supported_verified"):
            requested_pids.append(str(item["pid_name"]))
    requested_pids = list(dict.fromkeys(requested_pids))
    if str(vehicle.get("engine_code", "")).upper() == "BKP":
        # La documentación de esta variante identifica catalizador de
        # oxidación, no DPF. Evitar estos bloques reduce tiempo de barrido y
        # elimina huecos que nunca podrán convertirse en datos reales.
        bkp_not_applicable = {
            "VAG_EXHAUST_TEMP_1", "VAG_EXHAUST_TEMP_2",
            "VAG_DPF_SOOT_CALCULATED", "VAG_DPF_SOOT_MEASURED",
            "VAG_DPF_SOOT_PERCENT", "VAG_DPF_ASH_MASS",
            "VAG_DPF_DIFFERENTIAL_PRESSURE", "VAG_DPF_DISTANCE_SINCE_REGEN",
            "VAG_DPF_TIME_SINCE_REGEN", "VAG_DPF_REGEN_STATUS",
        }
        requested_pids = [pid for pid in requested_pids if pid not in bkp_not_applicable]
    capture_pids = (
        [pid for pid in requested_pids if pid in verified_capabilities]
        if verified_capabilities
        else requested_pids
    )
    if not capture_pids:
        raise HTTPException(status_code=409, detail="Ninguna señal del perfil está verificada para este vehículo.")

    session_rec = db.create_session(
        vehicle_id=s.vehicle_id,
        profile_id=profile["id"],
        engine_condition=s.engine_condition,
        notes=s.notes or profile["name"],
        title=s.title or profile["name"],
        symptom=s.symptom,
        odometer_km=s.odometer_km,
    )
    initial_scan = None
    if adapter.connection is not None and not demo_mode:
        try:
            initial_scan = _perform_dtc_scan(
                s.vehicle_id,
                "initial",
                session_id=session_rec["id"],
            )
        except Exception:
            logger.exception(
                "La captura continuará, pero falló el escaneo DTC inicial de %s.",
                session_rec["id"],
            )
    active_session_id = session_rec["id"]
    last_capture_error = None
    with live_samples_lock:
        live_samples.clear()
    oem_reader = None
    verified_vag_names = {
        item["pid_name"]
        for item in db.list_vehicle_capabilities(s.vehicle_id)
        if item.get("supported_verified") and str(item.get("source", "")).startswith("vag_")
    }
    verified_kwp_names = {
        item["pid_name"]
        for item in db.list_vehicle_capabilities(s.vehicle_id)
        if item.get("supported_verified") and str(item.get("source", "")).startswith("vag_kwp2000")
    }
    known_kwp_engine = str(vehicle.get("engine_code", "")).upper() in {"BKP", "BMP", "BMN", "BMR", "BUY", "BUZ"}
    kwp_requested_names = set(requested_pids).intersection(
        definition.pid_name for definition in RUNTIME_KWP_SIGNALS
    )
    if adapter.connection is not None and _is_vag_vehicle(vehicle) and (verified_vag_names or known_kwp_engine):
        if verified_kwp_names or known_kwp_engine:
            # En una ECU ya identificada no se limitan las capturas a lo que
            # verificó una prueba anterior: cada señal solicitada se comprueba
            # en la conducción real y queda promovida si devuelve datos.
            enabled_kwp_names = kwp_requested_names | verified_kwp_names
            candidate = VagKwp2000Client(adapter.connection, enabled_signal_names=enabled_kwp_names)
            try:
                candidate.open()
                oem_reader = candidate
                # TP2.0 y OBD-II genérico requieren configuraciones distintas
                # del adaptador. Los bloques VAG incluyen también las señales
                # esenciales (RPM, velocidad y temperaturas).
                capture_pids = [pid for pid in requested_pids if pid in candidate.signal_names]
            except Exception as exc:
                db.fail_session(session_rec["id"], f"No se pudo abrir el canal Volkswagen TP2.0: {exc}")
                _reconnect_adapter_on_same_port()
                active_session_id = None
                raise HTTPException(status_code=409, detail=f"No se pudo abrir el canal Volkswagen de solo lectura: {exc}")
        else:
            candidate = VagReadOnlyClient(adapter.connection)
            cached_probe = manufacturer_probe_cache.get(s.vehicle_id, {})
            candidate.ecu_part_number = str(cached_probe.get("ecu_part_number", ""))
            if not candidate.ecu_part_number:
                # La caché se pierde al reiniciar la aplicación; repetir únicamente
                # las lecturas de identidad mantiene la validación ligada a la ECU.
                candidate.identify_ecu()
            if candidate.signal_names & set(capture_pids):
                oem_reader = candidate
    if not capture_pids:
        db.fail_session(session_rec["id"], "No hay señales compatibles con el transporte Volkswagen identificado.")
        active_session_id = None
        raise HTTPException(status_code=409, detail="No hay señales verificadas para el protocolo Volkswagen identificado.")
    active_poller = TelemetryPoller(
        session_id=active_session_id,
        adapter_connection=adapter.connection,
        telemetry_store=telemetry_store,
        pids=capture_pids,
        oem_reader=oem_reader,
    )

    def broadcast_sample(sample: Dict[str, Any]):
        if sample.get("value") is not None:
            with live_samples_lock:
                live_samples.append(sample)
        # Notificar a los clientes WebSocket en tiempo real
        for ws in list(connected_websockets):
            try:
                asyncio.run_coroutine_threadsafe(ws.send_json(sample), asyncio.get_event_loop())
            except Exception:
                pass

    active_poller.register_sample_callback(broadcast_sample)
    active_poller.start(poll_interval_ms=100)
    adapter.set_state(AdapterState.CAPTURING)

    return {
        **session_rec,
        "automatic_dtc_scan": {
            "initial": initial_scan,
            "final": None,
        },
    }

@app.post("/api/sessions/{session_id}/stop")
def stop_session(session_id: str):
    global active_poller, active_session_id
    if active_session_id != session_id or not active_poller:
        raise HTTPException(status_code=404, detail="La sesión indicada no está activa.")

    transport_requires_reconnect = bool(
        active_poller.oem_reader
        and getattr(active_poller.oem_reader, "transport_requires_reconnect", False)
    )
    active_poller.stop()
    capture_metrics = active_poller.get_metrics()
    parquet_path = telemetry_store.get_session_file_path(session_id)
    df = telemetry_store.load_session_dataframe(session_id)
    session_before_stop = db.get_session(session_id) or {}
    _promote_kwp_capabilities(str(session_before_stop.get("vehicle_id", "")), df)
    quality = SessionQualityCalculator().calculate_quality(df)
    session_rec = db.stop_session(
        session_id,
        quality_score=quality["overall_score"],
        data_file=parquet_path,
        requested_signal_count=int(capture_metrics.get("requested_signal_count", 0)),
        captured_signal_count=int(capture_metrics.get("captured_signal_count", 0)),
        capture_coverage_percent=float(capture_metrics.get("capture_coverage_percent", 0.0)),
    )
    if transport_requires_reconnect:
        _reconnect_adapter_on_same_port()
    final_scan = None
    if adapter.connection is not None:
        try:
            final_scan = _perform_dtc_scan(
                session_before_stop.get("vehicle_id", session_rec["vehicle_id"]),
                "final",
                session_id=session_id,
            )
        except Exception:
            logger.exception(
                "La sesión se guardó, pero falló el escaneo DTC final de %s.",
                session_id,
            )
    
    active_poller = None
    active_session_id = None
    adapter.set_state(AdapterState.VEHICLE_CONNECTED if adapter.connection else AdapterState.ADAPTER_NOT_FOUND)

    return {
        **session_rec,
        "automatic_dtc_scan": {
            "initial": next(
                (
                    scan
                    for scan in db.list_dtc_scans(session_rec["vehicle_id"])
                    if scan.get("session_id") == session_id
                    and scan.get("scan_type") == "initial"
                ),
                None,
            ),
            "final": final_scan,
        },
        "capture_summary": capture_metrics,
    }

@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")
    return sess


@app.patch("/api/sessions/{session_id}")
def update_session(session_id: str, update: SessionUpdate):
    if not db.get_session(session_id):
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")
    updated = db.update_session(
        session_id,
        title=update.title,
        notes=update.notes,
        symptom=update.symptom,
        odometer_km=update.odometer_km,
        engine_condition=update.engine_condition,
    )
    return updated

@app.get("/api/sessions/{session_id}/signals")
def get_session_signals(session_id: str):
    df = telemetry_store.load_session_dataframe(session_id)
    if df is None or df.is_empty():
        return {"session_id": session_id, "samples": []}
    return {"session_id": session_id, "count": len(df), "samples": df.to_dicts()}


@app.get("/api/live/snapshot")
def get_live_snapshot():
    _finalize_aborted_capture()
    with live_samples_lock:
        samples = list(live_samples)
    latest: Dict[str, Dict[str, Any]] = {}
    for sample in samples:
        latest[sample["pid"]] = sample
    metrics = active_poller.get_metrics() if active_poller else None
    last_valid_age_sec = metrics.get("last_valid_age_sec") if metrics else None
    poll_in_progress = bool(metrics and metrics.get("poll_in_progress"))
    poll_age_sec = float(metrics.get("poll_age_sec", 0.0)) if metrics else 0.0
    data_stale = bool(
        last_valid_age_sec is not None
        and float(last_valid_age_sec) > 15.0
        and (not poll_in_progress or poll_age_sec > 30.0)
    )
    trip_metrics = TripMetrics.calculate(pl.DataFrame(samples)) if samples else TripMetrics.calculate(None)
    return {
        "session_id": active_session_id,
        "samples": samples,
        "latest": latest,
        "capture_metrics": metrics,
        "last_valid_age_sec": last_valid_age_sec,
        "data_stale": data_stale,
        "trip_metrics": trip_metrics,
        "capture_error": last_capture_error,
    }

# --- MARCADORES Y ANÁLISIS ---
@app.post("/api/sessions/{session_id}/markers")
def add_marker(session_id: str, m: EventMarkerCreate):
    return db.add_event_marker(session_id, m.timestamp_offset_ms, m.event_type, m.note or "")

@app.get("/api/sessions/{session_id}/markers")
def list_markers(session_id: str):
    return db.list_event_markers(session_id)

@app.get("/api/sessions/{session_id}/analysis")
def analyze_session(session_id: str):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")
    vehicle = db.get_vehicle(session["vehicle_id"]) or {}
    df = telemetry_store.load_session_dataframe(session_id)
    if df is None or df.is_empty():
        quality = SessionQualityCalculator().calculate_quality(df)
        summary = DiagnosticSummary.build(
            df, {}, [], [], quality, vehicle.get("powertrain_type", "gasoline")
        )
        return {"session_id": session_id, "findings": [], "event_impacts": [], **summary}

    stats = SignalStatistics.analyze_full_session(df)
    findings = rule_engine.evaluate_session(
        df, powertrain_type=vehicle.get("powertrain_type", "gasoline")
    )
    markers = db.list_event_markers(session_id)

    event_analyzer = EventWindowAnalyzer()
    event_impacts = []
    for mk in markers:
        impact = event_analyzer.analyze_event_impact(df, mk["timestamp_offset_ms"])
        impact["marker_note"] = mk["note"]
        impact["event_type"] = mk["event_type"]
        event_impacts.append(impact)

    quality = SessionQualityCalculator().calculate_quality(df)
    scans = db.list_dtc_scans(session["vehicle_id"])
    dtcs = db.list_dtc_records(scans[0]["id"]) if scans else []
    summary = DiagnosticSummary.build(
        df, stats, findings, dtcs, quality, vehicle.get("powertrain_type", "gasoline")
    )
    return {
        "session_id": session_id,
        "findings": findings,
        "event_impacts": event_impacts,
        **summary,
    }

# --- WEBSOCKET EN TIEMPO REAL ---
failure_simulator = FailureSimulator(adapter)

@app.get("/api/profiles")
def list_profiles():
    return CaptureProfileManager.list_profiles()

@app.get("/api/protocols/{protocol_id}")
def get_protocol(protocol_id: str):
    return ProtocolManager.get_protocol(protocol_id)

class FaultRequest(BaseModel):
    fault_type: Literal["BLUETOOTH_DISCONNECT", "IGNITION_OFF", "CORRUPTED_FRAME", "RECOVER"]

@app.post("/api/simulator/trigger-fault")
def trigger_fault(req: FaultRequest):
    if os.getenv("APP_ENV", "production").strip().lower() not in {"development", "test"}:
        raise HTTPException(status_code=404, detail="Simulador no disponible en producción.")
    return failure_simulator.inject_fault(req.fault_type)

# --- MODE 06, GARAGE E INFORMES ZIP ---

exporter = VehicleBackupExporter(db_manager=db, telemetry_store=telemetry_store)

class RepairCreate(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    notes: Optional[str] = Field(default="", max_length=2000)

@app.get("/api/vehicles/{vehicle_id}/mode06")
def get_mode06(vehicle_id: str):
    if adapter.connection is None:
        return {
            "vehicle_id": vehicle_id,
            "available": False,
            "monitors": [],
            "message": (
                "Conecta el adaptador y da el contacto para consultar los "
                "monitores reales de la ECU. No se muestran datos de demostración."
            ),
        }
    monitors = Mode06Analyzer.get_mode06_monitors(
        vehicle_id,
        adapter_connection=adapter.connection,
    )
    return {
        "vehicle_id": vehicle_id,
        "available": bool(monitors),
        "monitors": monitors,
        "message": (
            f"Se han leído {len(monitors)} resultados directamente de la ECU."
            if monitors
            else (
                "La ECU o el protocolo activo no ha ofrecido resultados Modo 06 "
                "decodificables. No se muestran valores estimados."
            )
        ),
    }


@app.get("/api/vehicles/{vehicle_id}/readiness")
def get_readiness(vehicle_id: str):
    if not db.get_vehicle(vehicle_id):
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    if adapter.connection is None:
        return {
            "available": False,
            "mil": None,
            "dtc_count": None,
            "monitors": [],
            "message": "Conecta la ECU para leer el estado I/M real. No se muestran datos simulados.",
        }
    try:
        import obd
        response = adapter.connection.query(obd.commands.STATUS)
        if not response or response.is_null():
            return {
                "available": False,
                "mil": None,
                "dtc_count": None,
                "monitors": [],
                "message": "La ECU no respondió a la consulta I/M Readiness.",
            }
        status = response.value
        monitors = []
        for test in getattr(status, "tests", []) or []:
            monitors.append(
                {
                    "name": str(getattr(test, "name", test)),
                    "available": bool(getattr(test, "available", True)),
                    "complete": bool(getattr(test, "complete", False)),
                }
            )
        return {
            "available": True,
            "mil": bool(getattr(status, "MIL", False)),
            "dtc_count": int(getattr(status, "DTC_count", 0)),
            "monitors": monitors,
            "message": "Estado I/M leído directamente de la ECU.",
        }
    except Exception as exc:
        logger.exception("No se pudieron leer los monitores de preparación de la ECU.")
        raise HTTPException(
            status_code=502,
            detail="No se pudieron leer los monitores de preparación de la ECU.",
        ) from exc

@app.get("/api/vehicles/{vehicle_id}/repairs")
def list_repairs(vehicle_id: str):
    return db.list_repair_actions(vehicle_id)

@app.post("/api/vehicles/{vehicle_id}/repairs")
def add_repair(vehicle_id: str, r: RepairCreate):
    return db.create_repair_action(vehicle_id, r.description, r.notes or "")

@app.get("/api/vehicles/{vehicle_id}/export")
def export_vehicle(vehicle_id: str):
    safe_id = hashlib.sha256(vehicle_id.encode("utf-8")).hexdigest()[:20]
    zip_path = backups_path() / f"backup_{safe_id}.zip"
    exporter.export_vehicle_zip(vehicle_id, str(zip_path))
    return FileResponse(str(zip_path), filename=f"backup_vehiculo_{safe_id}.zip", media_type="application/zip")

ai_service = AIService()


def _session_symptom_context(session: Dict[str, Any]) -> str:
    parts = []
    if session.get("symptom"):
        parts.append(f"Síntoma declarado: {session['symptom']}")
    if session.get("title"):
        parts.append(f"Nombre de la prueba: {session['title']}")
    if session.get("notes"):
        parts.append(f"Observaciones: {session['notes']}")
    return " · ".join(parts)


def _telemetry_source_counts(df) -> Dict[str, int]:
    if df is None or df.is_empty() or "data_source" not in df.columns:
        return {}
    return {
        str(row["data_source"]): int(row["len"])
        for row in df.group_by("data_source").len().to_dicts()
    }


def _dtc_evidence_for_session(session: Dict[str, Any]):
    scans = db.list_dtc_scans(session["vehicle_id"])
    if not scans:
        return [], "No hay un escaneo DTC guardado para este vehículo.", None
    linked_scan = next(
        (scan for scan in scans if scan.get("session_id") == session["id"]),
        None,
    )
    scan = linked_scan or scans[0]
    records = db.list_dtc_records(scan["id"])
    for record in records:
        record["freeze_frame"] = db.list_freeze_frames(record["id"])
    created_at = scan.get("created_at")
    if linked_scan:
        scope = f"Escaneo DTC vinculado a esta sesión ({created_at})."
    else:
        scope = (
            f"Último escaneo DTC independiente del vehículo ({created_at}); "
            "puede no corresponder al mismo recorrido."
        )
    return records, scope, scan


def _assistant_session_context(
    session: Dict[str, Any],
    vehicle: Dict[str, Any],
    df,
    markers: List[Dict[str, Any]],
    dtc_scope: str,
) -> Dict[str, Any]:
    from analysis.spec_resolver import SpecResolver

    specification = SpecResolver.resolve_spec(
        vehicle_id=vehicle.get("id", ""),
        make=vehicle.get("make", ""),
        model=vehicle.get("model", ""),
        engine_code=vehicle.get("engine_code", ""),
        powertrain_type=vehicle.get("powertrain_type", "gasoline"),
    )
    historical_baseline = historical_baselines.compare_session(session["id"])
    return {
        "id": session["id"],
        "title": session.get("title") or session.get("notes") or "Sesión sin título",
        "symptom": session.get("symptom") or "",
        "profile_id": session.get("profile_id"),
        "engine_condition": session.get("engine_condition"),
        "odometer_km": session.get("odometer_km"),
        "started_at": session.get("started_at"),
        "ended_at": session.get("ended_at"),
        "status": session.get("status"),
        "sample_count": int(len(df)) if df is not None else 0,
        "data_sources": _telemetry_source_counts(df),
        "marker_count": len(markers),
        "dtc_scope": dtc_scope,
        "specification_scope": specification.get("confidence_tier"),
        "historical_baseline": {
            "available": historical_baseline.get("available", False),
            "status": historical_baseline.get("status"),
            "message": historical_baseline.get("message"),
            "source_session_ids": historical_baseline.get("source_session_ids", []),
            "qualifying_session_count": historical_baseline.get(
                "qualifying_session_count",
                0,
            ),
            "remaining_session_count": historical_baseline.get(
                "remaining_session_count",
                0,
            ),
            "deviations": historical_baseline.get("deviations", []),
        },
    }


class CompareRequest(BaseModel):
    session_id_a: str = Field(min_length=1, max_length=100)
    session_id_b: str = Field(min_length=1, max_length=100)
    label_a: Optional[str] = Field(default="Sesión A", max_length=100)
    label_b: Optional[str] = Field(default="Sesión B", max_length=100)

@app.get("/api/sessions/{session_id}/ai-explain")
def explain_session(session_id: str):
    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")
    
    vehicle = db.get_vehicle(sess["vehicle_id"]) or {}
    df = telemetry_store.load_session_dataframe(session_id)
    stats = SignalStatistics.analyze_full_session(df) if df is not None else {}
    findings = (
        rule_engine.evaluate_session(
            df, powertrain_type=vehicle.get("powertrain_type", "gasoline")
        )
        if df is not None
        else []
    )
    
    # Obtener escaneos DTC
    dtcs, _, _ = _dtc_evidence_for_session(sess)

    ai_response = ai_service.analyze_session(
        vehicle_info=vehicle,
        dtcs=dtcs,
        stats=stats,
        rule_findings=findings,
        symptom_note=_session_symptom_context(sess)
    )
    return ai_response.dict()

class AiQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    mode: Literal["simple", "technical", "workshop"] = "simple"
    conversation_history: Optional[List[Dict[str, str]]] = Field(default=None, max_length=12)
    engine: Literal["local", "generative"] = "local"
    allow_remote: bool = False
    language: Literal["es", "en", "it", "de"] = "es"


@app.get("/api/ai/status")
def get_ai_status():
    return ai_service.generative_status()


@app.get("/api/sessions/{session_id}/assistant-context")
def get_assistant_context(session_id: str):
    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")
    vehicle = db.get_vehicle(sess["vehicle_id"]) or {}
    df = telemetry_store.load_session_dataframe(session_id)
    stats = SignalStatistics.analyze_full_session(df) if df is not None else {}
    findings = (
        rule_engine.evaluate_session(
            df, powertrain_type=vehicle.get("powertrain_type", "gasoline")
        )
        if df is not None
        else []
    )
    dtcs, dtc_scope, _ = _dtc_evidence_for_session(sess)
    quality = SessionQualityCalculator().calculate_quality(df)
    source_counts = _telemetry_source_counts(df)
    markers = db.list_event_markers(session_id)
    session_context = _assistant_session_context(
        sess,
        vehicle,
        df,
        markers,
        dtc_scope,
    )
    historical_baseline = session_context["historical_baseline"]
    summary = DiagnosticSummary.build(
        df, stats, findings, dtcs, quality, vehicle.get("powertrain_type", "gasoline")
    )
    return {
        "session": sess,
        "scope": {
            "type": "single_session",
            "message": "La respuesta usa únicamente esta sesión; no mezcla automáticamente otras sesiones.",
            "assistant_engine": "Motor local basado en reglas, estadísticas y evidencias de la sesión.",
            "sample_count": int(len(df)) if df is not None else 0,
            "data_sources": source_counts,
            "dtc_scope": dtc_scope,
            "symptom_scope": (
                "Síntoma guardado al iniciar esta prueba."
                if sess.get("symptom")
                else "Esta sesión no tiene un síntoma inicial guardado."
            ),
            "conversation_scope": "Hasta 12 mensajes recientes de esta conversación y solo de esta sesión.",
            "baseline_scope": (
                f"Comparación separada con {historical_baseline['qualifying_session_count']} "
                "sesiones anteriores válidas del mismo vehículo."
                if historical_baseline.get("available")
                else historical_baseline.get("message")
            ),
        },
        "vehicle": vehicle,
        "dtcs": dtcs,
        "signal_count": sum(
            1 for signal in stats.get("signals", {}).values() if signal.get("has_data")
        ),
        "available_signals": [
            pid for pid, signal in stats.get("signals", {}).items() if signal.get("has_data")
        ],
        "quality": quality,
        "health": summary["health"],
        "conclusion": summary["conclusion"],
        "alerts": summary["alerts"],
        "historical_baseline": historical_baseline,
    }

@app.post("/api/sessions/{session_id}/query")
def query_session_ai(session_id: str, req: AiQueryRequest):
    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    vehicle = db.get_vehicle(sess["vehicle_id"]) or {}
    df = telemetry_store.load_session_dataframe(session_id)
    stats = SignalStatistics.analyze_full_session(df) if df is not None else {}
    findings = (
        rule_engine.evaluate_session(
            df, powertrain_type=vehicle.get("powertrain_type", "gasoline")
        )
        if df is not None
        else []
    )
    markers = db.list_event_markers(session_id)

    event_analyzer = EventWindowAnalyzer()
    event_impacts = []
    if df is not None:
        for mk in markers:
            impact = event_analyzer.analyze_event_impact(df, mk["timestamp_offset_ms"])
            impact["marker_note"] = mk["note"]
            impact["event_type"] = mk["event_type"]
            event_impacts.append(impact)

    # Obtener DTCs
    dtcs, dtc_scope, _ = _dtc_evidence_for_session(sess)
    session_context = _assistant_session_context(
        sess,
        vehicle,
        df,
        markers,
        dtc_scope,
    )

    return ai_service.query_interactive(
        user_question=req.question,
        vehicle_info=vehicle,
        dtcs=dtcs,
        stats=stats,
        rule_findings=findings,
        event_impacts=event_impacts,
        symptom_note=_session_symptom_context(sess),
        session_context=session_context,
        mode=req.mode or "simple",
        conversation_history=req.conversation_history or [],
        engine=req.engine,
        allow_remote=req.allow_remote,
        language=req.language,
    )

@app.get("/api/vehicles/{vehicle_id}/spec")
def get_vehicle_spec(vehicle_id: str):
    v = db.get_vehicle(vehicle_id)
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    from analysis.spec_resolver import SpecResolver
    return SpecResolver.resolve_spec(
        vehicle_id=v["id"],
        make=v.get("make", ""),
        model=v.get("model", ""),
        engine_code=v.get("engine_code", ""),
        powertrain_type=v.get("powertrain_type", "gasoline")
    )


@app.post("/api/sessions/compare")
def compare_sessions(req: CompareRequest):
    session_a = db.get_session(req.session_id_a)
    session_b = db.get_session(req.session_id_b)
    if not session_a or not session_b:
        raise HTTPException(status_code=404, detail="Una de las sesiones no existe.")
    if session_a["vehicle_id"] != session_b["vehicle_id"]:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden comparar sesiones del mismo vehículo.",
        )
    df_a = telemetry_store.load_session_dataframe(req.session_id_a)
    df_b = telemetry_store.load_session_dataframe(req.session_id_b)
    if df_a is None or df_b is None:
        raise HTTPException(status_code=400, detail="Una o ambas sesiones no tienen telemetría disponible.")

    comparison = SessionComparator.compare_sessions(
        df_a, df_b,
        label_a=req.label_a or "Sesión A",
        label_b=req.label_b or "Sesión B"
    )
    warnings = []
    score = 100
    if (
        session_a.get("profile_id")
        and session_b.get("profile_id")
        and session_a["profile_id"] != session_b["profile_id"]
    ):
        warnings.append("Las sesiones usan protocolos de captura diferentes.")
        score -= 30
    if session_a.get("engine_condition") != session_b.get("engine_condition"):
        warnings.append("La temperatura o condición inicial del motor no coincide.")
        score -= 20
    duration_a = float(comparison.get("duration_a_sec") or 0)
    duration_b = float(comparison.get("duration_b_sec") or 0)
    if max(duration_a, duration_b) and min(duration_a, duration_b) / max(duration_a, duration_b) < 0.65:
        warnings.append("La duración de las pruebas es muy diferente.")
        score -= 20
    if min(
        float(session_a.get("capture_quality_score") or 0),
        float(session_b.get("capture_quality_score") or 0),
    ) < 60:
        warnings.append("Al menos una captura tiene calidad limitada.")
        score -= 20
    sources_a = set(df_a["data_source"].drop_nulls().unique().to_list()) if "data_source" in df_a.columns else set()
    sources_b = set(df_b["data_source"].drop_nulls().unique().to_list()) if "data_source" in df_b.columns else set()
    if sources_a != sources_b:
        warnings.append("El origen de los datos no coincide entre ambas sesiones.")
        score -= 30
    comparison["comparability"] = {
        "score": max(0, score),
        "level": "alta" if score >= 80 else "media" if score >= 55 else "baja",
        "warnings": warnings,
        "message": (
            "Las condiciones son suficientemente comparables."
            if not warnings
            else "Interpreta el resultado teniendo en cuenta estas diferencias."
        ),
    }
    return comparison

@app.get("/api/sessions/{session_id}/report", response_class=HTMLResponse)
def get_session_html_report(
    session_id: str,
    mode: str = "user",
    lang: Literal["es", "en", "it", "de"] = "es",
):
    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    vehicle = db.get_vehicle(sess["vehicle_id"]) or {}
    df = telemetry_store.load_session_dataframe(session_id)
    stats = SignalStatistics.analyze_full_session(df) if df is not None else {}
    findings = (
        rule_engine.evaluate_session(
            df,
            powertrain_type=vehicle.get("powertrain_type", "gasoline"),
        )
        if df is not None
        else []
    )

    dtcs, _, _ = _dtc_evidence_for_session(sess)

    ai_resp = ai_service.analyze_session(vehicle_info=vehicle, dtcs=dtcs, stats=stats, rule_findings=findings, symptom_note=sess.get("notes"))
    quality = SessionQualityCalculator().calculate_quality(df)
    diagnostic_summary = DiagnosticSummary.build(
        df, stats, findings, dtcs, quality, vehicle.get("powertrain_type", "gasoline")
    )

    html_content = ReportGenerator.generate_html_report(
        vehicle=vehicle,
        session=sess,
        stats=stats,
        findings=findings,
        ai_analysis=ai_resp.dict(),
        dtcs=dtcs,
        quality_score=quality,
        diagnostic_summary=diagnostic_summary,
        mode="technical" if mode == "technical" else "user",
        language=lang,
    )
    return HTMLResponse(content=html_content)

@app.websocket("/api/live")
async def websocket_live_telemetry(websocket: WebSocket):
    if not _is_allowed_browser_origin(websocket.headers.get("origin")):
        await websocket.close(code=1008, reason="Origen no permitido")
        return
    await websocket.accept()
    connected_websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_websockets.remove(websocket)

static_dir = resource_path("dashboard/out")
app.state.dashboard_available = (static_dir / "index.html").is_file()
app.state.dashboard_path = str(static_dir)
if app.state.dashboard_available:
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
