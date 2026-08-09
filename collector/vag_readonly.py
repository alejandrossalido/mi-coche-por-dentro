"""Lectura Volkswagen UDS estrictamente de solo lectura.

La capa separa el transporte de las definiciones de cada software de ECU.  Solo
se permite el servicio UDS 0x22 (ReadDataByIdentifier); no existen rutas para
codificacion, adaptaciones, rutinas, borrado de averias ni escritura.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from app_paths import ensure_user_directories

try:
    import obd
    from obd import ECU, OBDCommand
except ImportError:  # pragma: no cover - la aplicacion declara python-OBD
    obd = None
    ECU = None
    OBDCommand = None

logger = logging.getLogger(__name__)

ENGINE_REQUEST_HEADER = b"7E0"
READ_DATA_BY_IDENTIFIER = 0x22

# Identificadores normalizados de identidad. No alteran estado persistente.
IDENTITY_DIDS = {
    "VW_SPARE_PART_NUMBER": (0xF187, "Referencia de la centralita"),
    "VW_ECU_SOFTWARE_VERSION": (0xF189, "Versión de software de la centralita"),
    "VW_ECU_SERIAL_NUMBER": (0xF18C, "Número de serie de la centralita"),
    "VW_ECU_HARDWARE_NUMBER": (0xF191, "Referencia de hardware de la centralita"),
}

NEGATIVE_RESPONSE_REASONS = {
    0x11: "SERVICIO_NO_ADMITIDO",
    0x12: "SUBFUNCION_NO_ADMITIDA",
    0x13: "FORMATO_INCORRECTO",
    0x21: "ECU_OCUPADA",
    0x22: "CONDICIONES_NO_CORRECTAS",
    0x31: "IDENTIFICADOR_FUERA_DE_RANGO",
    0x33: "ACCESO_DENEGADO",
    0x78: "RESPUESTA_PENDIENTE",
}


@dataclass(frozen=True)
class VagSignalDefinition:
    """Definicion verificable de un valor contenido en un DID UDS."""

    pid_name: str
    label: str
    unit: str
    did: int
    byte_offset: int
    byte_length: int
    scale: float = 1.0
    value_offset: float = 0.0
    signed: bool = False
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    ecu_part_numbers: tuple[str, ...] = ()
    source: str = "verified_vehicle_map"


# Objetivos que la interfaz conoce aunque aun no exista una definicion binaria
# confirmada para el software concreto de la ECU.
VAG_SIGNAL_TARGETS: tuple[Dict[str, str], ...] = (
    {"pid_name": "VAG_OIL_TEMP", "label": "Temperatura del aceite", "unit": "°C"},
    {"pid_name": "VAG_AMBIENT_TEMP", "label": "Temperatura ambiente", "unit": "°C"},
    {"pid_name": "VAG_EXHAUST_TEMP_1", "label": "Temperatura de escape 1", "unit": "°C"},
    {"pid_name": "VAG_EXHAUST_TEMP_2", "label": "Temperatura de escape 2", "unit": "°C"},
    {"pid_name": "VAG_BAROMETRIC_PRESSURE", "label": "Presión barométrica", "unit": "kPa"},
    {"pid_name": "VAG_ACCELERATOR_POSITION", "label": "Posición del pedal", "unit": "%"},
    {"pid_name": "VAG_EGR_COMMAND", "label": "EGR ordenada", "unit": "%"},
    {"pid_name": "VAG_EGR_ACTUAL", "label": "EGR real", "unit": "%"},
    {"pid_name": "VAG_EGR_DUTY_CYCLE", "label": "Mando de la EGR", "unit": "%"},
    {"pid_name": "VAG_AIR_MASS_ACTUAL", "label": "Masa de aire real", "unit": "mg/str"},
    {"pid_name": "VAG_RAIL_PRESSURE_REQUESTED", "label": "Presión del rail solicitada", "unit": "bar"},
    {"pid_name": "VAG_RAIL_PRESSURE_ACTUAL", "label": "Presión del rail real", "unit": "bar"},
    {"pid_name": "VAG_BOOST_PRESSURE_REQUESTED", "label": "Presión de turbo solicitada", "unit": "kPa"},
    {"pid_name": "VAG_BOOST_PRESSURE_ACTUAL", "label": "Presión de turbo real", "unit": "kPa"},
    {"pid_name": "VAG_INJECTION_TIMING", "label": "Avance de inyección", "unit": "°"},
    {"pid_name": "VAG_FUEL_RATE", "label": "Consumo de combustible", "unit": "L/h"},
    {"pid_name": "VAG_INJECTION_QUANTITY", "label": "Cantidad de inyección", "unit": "mg/str"},
    {"pid_name": "VAG_INJECTOR_DEVIATION_1", "label": "Corrección del inyector 1", "unit": "mg/str"},
    {"pid_name": "VAG_INJECTOR_DEVIATION_2", "label": "Corrección del inyector 2", "unit": "mg/str"},
    {"pid_name": "VAG_INJECTOR_DEVIATION_3", "label": "Corrección del inyector 3", "unit": "mg/str"},
    {"pid_name": "VAG_INJECTOR_DEVIATION_4", "label": "Corrección del inyector 4", "unit": "mg/str"},
    {"pid_name": "VAG_DPF_SOOT_CALCULATED", "label": "Hollín calculado del DPF", "unit": "g"},
    {"pid_name": "VAG_DPF_SOOT_MEASURED", "label": "Hollín medido del DPF", "unit": "g"},
    {"pid_name": "VAG_DPF_SOOT_PERCENT", "label": "Carga de hollín del DPF", "unit": "%"},
    {"pid_name": "VAG_DPF_ASH_MASS", "label": "Masa de ceniza del DPF", "unit": "g"},
    {"pid_name": "VAG_DPF_DIFFERENTIAL_PRESSURE", "label": "Presión diferencial del DPF", "unit": "mbar"},
    {"pid_name": "VAG_DPF_DISTANCE_SINCE_REGEN", "label": "Distancia desde la última regeneración", "unit": "km"},
    {"pid_name": "VAG_DPF_TIME_SINCE_REGEN", "label": "Tiempo desde la última regeneración", "unit": "s"},
    {"pid_name": "VAG_DPF_REGEN_STATUS", "label": "Estado de regeneración del DPF", "unit": "state_code"},
    {"pid_name": "VAG_ECU_VOLTAGE", "label": "Tensión medida por la ECU", "unit": "V"},
)


def _raw_decoder(messages: Iterable[Any]) -> List[Dict[str, Any]]:
    return [
        {
            "tx_id": getattr(message, "tx_id", None),
            "data": bytes(getattr(message, "data", b"")).hex().upper(),
            "raw": message.raw() if hasattr(message, "raw") else "",
        }
        for message in messages
    ]


def vag_definition_path() -> Path:
    return ensure_user_directories()["config"] / "vag_cbab_readonly.json"


def load_signal_definitions(path: Optional[Path] = None) -> List[VagSignalDefinition]:
    """Carga un mapa local revisable; los DIDs vacios nunca se consultan."""
    definition_file = path or vag_definition_path()
    if not definition_file.exists():
        return []
    try:
        payload = json.loads(definition_file.read_text(encoding="utf-8"))
        rows = payload.get("signals", []) if isinstance(payload, dict) else []
        definitions: List[VagSignalDefinition] = []
        allowed_names = {item["pid_name"] for item in VAG_SIGNAL_TARGETS}
        for row in rows:
            if row.get("pid_name") not in allowed_names or row.get("did") in (None, ""):
                continue
            did_value = row["did"]
            did = int(did_value, 16) if isinstance(did_value, str) else int(did_value)
            if not 0 <= did <= 0xFFFF:
                continue
            definitions.append(
                VagSignalDefinition(
                    pid_name=row["pid_name"],
                    label=str(row.get("label") or row["pid_name"]),
                    unit=str(row.get("unit") or ""),
                    did=did,
                    byte_offset=max(0, int(row.get("byte_offset", 0))),
                    byte_length=max(1, int(row.get("byte_length", 1))),
                    scale=float(row.get("scale", 1.0)),
                    value_offset=float(row.get("value_offset", 0.0)),
                    signed=bool(row.get("signed", False)),
                    minimum=float(row["minimum"]) if row.get("minimum") is not None else None,
                    maximum=float(row["maximum"]) if row.get("maximum") is not None else None,
                    ecu_part_numbers=tuple(str(value).strip() for value in row.get("ecu_part_numbers", []) if str(value).strip()),
                    source=str(row.get("source") or "verified_vehicle_map"),
                )
            )
        return definitions
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        logger.exception("El mapa Volkswagen %s no es válido y se ignorará.", definition_file)
        return []


def build_definition_template() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "safety": "Solo servicio UDS 0x22. No introducir identificadores sin verificar para la referencia exacta de ECU.",
        "signals": [
            {**target, "did": None, "byte_offset": 0, "byte_length": 1, "scale": 1.0, "value_offset": 0.0}
            for target in VAG_SIGNAL_TARGETS
        ],
    }


def ensure_definition_template(path: Optional[Path] = None) -> Path:
    """Crea una plantilla persistente sin reemplazar configuraciones del usuario."""
    definition_file = path or vag_definition_path()
    if definition_file.exists():
        return definition_file
    definition_file.parent.mkdir(parents=True, exist_ok=True)
    temporary = definition_file.with_suffix(".json.partial")
    temporary.write_text(
        json.dumps(build_definition_template(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(definition_file)
    return definition_file


class VagReadOnlyClient:
    """Cliente UDS limitado por construccion a lecturas 0x22 en la ECU motor."""

    def __init__(self, connection: Any, definitions: Optional[List[VagSignalDefinition]] = None):
        self.connection = connection
        self.definitions = definitions if definitions is not None else load_signal_definitions()
        self.definition_by_name = {item.pid_name: item for item in self.definitions}
        self.ecu_part_number = ""

    @property
    def signal_names(self) -> set[str]:
        return set(self.definition_by_name)

    def _read_did(self, did: int) -> Dict[str, Any]:
        started = time.monotonic()
        if obd is None or OBDCommand is None or not self.connection:
            return {"success": False, "status": "not_connected", "reason": "SIN_CONEXION", "latency_ms": 0.0}
        # python-OBD espera el texto hexadecimal que se enviará al ELM, no los
        # octetos ya convertidos (por ejemplo b"22F187").
        command_bytes = f"22{did:04X}".encode("ascii")
        command = OBDCommand(
            name=f"VAG_UDS_{did:04X}",
            desc=f"Lectura UDS segura DID {did:04X}",
            command=command_bytes,
            _bytes=0,
            decoder=_raw_decoder,
            ecu=ECU.ALL,
            fast=False,
            header=ENGINE_REQUEST_HEADER,
        )
        try:
            response = self.connection.query(command, force=True)
            latency = round((time.monotonic() - started) * 1000.0, 2)
        except Exception as exc:
            return {"success": False, "status": "transport_error", "reason": str(exc), "latency_ms": round((time.monotonic() - started) * 1000.0, 2)}
        if response is None or response.is_null() or not isinstance(response.value, list):
            return {"success": False, "status": "no_data", "reason": "SIN_RESPUESTA", "latency_ms": latency}
        raw_messages: List[str] = []
        for message in response.value:
            raw_messages.append(str(message.get("raw", "")))
            try:
                data = bytes.fromhex(message.get("data", ""))
            except ValueError:
                continue
            if len(data) >= 3 and data[0] == 0x7F and data[1] == READ_DATA_BY_IDENTIFIER:
                nrc = data[2]
                return {
                    "success": False,
                    "status": "negative_response",
                    "reason": NEGATIVE_RESPONSE_REASONS.get(nrc, f"RESPUESTA_NEGATIVA_{nrc:02X}"),
                    "negative_response_code": f"{nrc:02X}",
                    "latency_ms": latency,
                    "raw_response": message.get("raw", ""),
                }
            if len(data) >= 3 and data[0] == 0x62 and int.from_bytes(data[1:3], "big") == did:
                return {
                    "success": True,
                    "status": "compatible",
                    "payload": data[3:],
                    "latency_ms": latency,
                    "raw_response": message.get("raw", ""),
                }
        return {
            "success": False,
            "status": "unexpected_response",
            "reason": "RESPUESTA_NO_RECONOCIDA",
            "latency_ms": latency,
            "raw_response": "\n".join(value for value in raw_messages if value),
        }

    @staticmethod
    def _decode_text(payload: bytes) -> str:
        return payload.replace(b"\x00", b"").replace(b"\xff", b"").decode("ascii", errors="replace").strip()

    def identify_standard_obd(self) -> Dict[str, Any]:
        """Obtiene identidad OBD normalizada; el VIN se devuelve enmascarado."""
        if obd is None or not self.connection:
            return {}
        result: Dict[str, Any] = {}
        for name in ("ELM_VERSION", "CALIBRATION_ID", "CVN", "VIN"):
            command = getattr(obd.commands, name, None)
            if command is None:
                continue
            try:
                response = self.connection.query(command, force=True)
                if response is None or response.is_null():
                    continue
                value = response.value
                if isinstance(value, (bytes, bytearray)):
                    value = bytes(value).decode("ascii", errors="replace").strip(" \x00\xff")
                elif isinstance(value, (list, tuple)):
                    value = [
                        bytes(item).decode("ascii", errors="replace").strip(" \x00\xff")
                        if isinstance(item, (bytes, bytearray)) else str(item)
                        for item in value
                    ]
                else:
                    value = str(value)
                if name == "VIN":
                    vin = "".join(value) if isinstance(value, list) else value
                    value = f"***{vin[-4:]}" if vin else ""
                result[name] = value
            except Exception:
                logger.debug("La lectura de identidad OBD %s no respondió.", name, exc_info=True)
        return result

    def identify_ecu(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for name, (did, label) in IDENTITY_DIDS.items():
            response = self._read_did(did)
            value = self._decode_text(response.get("payload", b"")) if response.get("success") else None
            if name == "VW_SPARE_PART_NUMBER" and value:
                self.ecu_part_number = value
            results.append({
                "pid_name": name,
                "label": label,
                "mode": "UDS_22",
                "pid": f"{did:04X}",
                "unit": "text",
                "value": value,
                "supported_reported": bool(response.get("success")),
                "supported_verified": bool(response.get("success")),
                "status": response.get("status", "unknown"),
                "reason": response.get("reason", ""),
                "avg_latency_ms": response.get("latency_ms", 0.0),
                "success_rate": 1.0 if response.get("success") else 0.0,
                "source": "vag_uds_identity",
                "ecu_address": "7E0/7E8",
                "raw_response": response.get("raw_response", ""),
            })
        return results

    def _definition_applies(self, definition: VagSignalDefinition) -> bool:
        if not definition.ecu_part_numbers:
            return True
        normalized = self.ecu_part_number.replace(" ", "").upper()
        return any(value.replace(" ", "").upper() in normalized for value in definition.ecu_part_numbers)

    def read_signal(self, pid_name: str) -> Dict[str, Any]:
        definition = self.definition_by_name.get(pid_name)
        if definition is None:
            return {"pid": pid_name, "success": False, "status": "mapping_required", "reason": "MAPA_ECU_NO_VERIFICADO"}
        if not self._definition_applies(definition):
            return {"pid": pid_name, "success": False, "status": "ecu_mismatch", "reason": "REFERENCIA_ECU_NO_COINCIDE"}
        response = self._read_did(definition.did)
        if not response.get("success"):
            return {"pid": pid_name, "unit": definition.unit, **response}
        payload = response["payload"]
        end = definition.byte_offset + definition.byte_length
        if end > len(payload):
            return {"pid": pid_name, "unit": definition.unit, "success": False, "status": "decode_error", "reason": "RESPUESTA_DEMASIADO_CORTA", "latency_ms": response.get("latency_ms", 0.0)}
        raw_value = int.from_bytes(payload[definition.byte_offset:end], "big", signed=definition.signed)
        value = raw_value * definition.scale + definition.value_offset
        if (
            definition.minimum is not None and value < definition.minimum
        ) or (
            definition.maximum is not None and value > definition.maximum
        ):
            return {"pid": pid_name, "unit": definition.unit, "success": False, "status": "implausible", "reason": "VALOR_FUERA_DE_RANGO", "value": value, "latency_ms": response.get("latency_ms", 0.0)}
        return {
            "pid": pid_name,
            "value": round(float(value), 4),
            "unit": definition.unit,
            "success": True,
            "status": "compatible",
            "latency_ms": response.get("latency_ms", 0.0),
            "raw_response": response.get("raw_response", ""),
            "data_source": "measured_vag_uds",
        }

    def probe_live_signals(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        targets = {item["pid_name"]: item for item in VAG_SIGNAL_TARGETS}
        for pid_name, target in targets.items():
            definition = self.definition_by_name.get(pid_name)
            if definition is None:
                results.append({
                    **target,
                    "mode": "UDS_22",
                    "pid": "",
                    "supported_reported": False,
                    "supported_verified": False,
                    "status": "mapping_required",
                    "reason": "FALTA_MAPA_PARA_ESTA_REFERENCIA_ECU",
                    "avg_latency_ms": 0.0,
                    "success_rate": 0.0,
                    "source": "vag_uds_pending",
                    "ecu_address": "7E0/7E8",
                })
                continue
            reading = self.read_signal(pid_name)
            capability_source = definition.source
            if not capability_source.startswith("vag_"):
                capability_source = f"vag_uds_{capability_source}"
            results.append({
                **target,
                "mode": "UDS_22",
                "pid": f"{definition.did:04X}",
                "supported_reported": bool(reading.get("success")),
                "supported_verified": bool(reading.get("success")),
                "status": reading.get("status", "unknown"),
                "reason": reading.get("reason", ""),
                "avg_latency_ms": reading.get("latency_ms", 0.0),
                "success_rate": 1.0 if reading.get("success") else 0.0,
                "source": capability_source,
                "ecu_address": "7E0/7E8",
                "sample_value": reading.get("value"),
            })
        return results

    def probe(self, standard_identity: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        standard_identity = standard_identity or self.identify_standard_obd()
        identity = self.identify_ecu()
        live_signals = self.probe_live_signals()
        identified = any(item["supported_verified"] for item in identity)
        verified = [item for item in live_signals if item["supported_verified"]]
        return {
            "protocol": "UDS ReadDataByIdentifier (0x22), solo lectura",
            "ecu_address": "7E0/7E8",
            "identified": identified,
            "ecu_part_number": self.ecu_part_number,
            "standard_obd_identity": standard_identity,
            "identity": identity,
            "live_signals": live_signals,
            "verified_live_signal_count": len(verified),
            "mapping_required_count": sum(item["status"] == "mapping_required" for item in live_signals),
            "definition_file": str(vag_definition_path()),
            "safety": "No se envían servicios de escritura, codificación, adaptación, rutinas ni borrado.",
        }


def capability_rows(probe_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    return list(probe_result.get("identity", [])) + list(probe_result.get("live_signals", []))


__all__ = [
    "VAG_SIGNAL_TARGETS",
    "VagReadOnlyClient",
    "VagSignalDefinition",
    "build_definition_template",
    "capability_rows",
    "ensure_definition_template",
    "load_signal_definitions",
    "vag_definition_path",
]
