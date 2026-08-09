"""
Batería de pruebas unitarias para la Etapa 0 y Etapa 1:
- Máquina de estados de conexión.
- Transportes de telemetría (Serie, Simulador y Playback).
- Escrituras atómicas Parquet (.partial -> .parquet).
- Calculador de Calidad de Sesión (0-100).
- Catálogo cerrado de evidencias.
- Constructor de Líneas Base por Vehículo.
"""
import os
import tempfile
import polars as pl

from collector.connection_state_machine import ConnectionStateMachine, ConnectionState
from collector.transports.simulator_transport import SimulatorTransport
from database.parquet_store import TelemetryStore
from analysis.session_quality import SessionQualityCalculator
from analysis.evidence_catalog import EvidenceCatalog
from analysis.baseline_builder import VehicleBaselineBuilder

def test_connection_state_machine():
    sm = ConnectionStateMachine()
    assert sm.state == ConnectionState.DISCONNECTED

    assert sm.transition_to(ConnectionState.DISCOVERING_ADAPTER, "Buscando puerto COM") is True
    assert sm.state == ConnectionState.DISCOVERING_ADAPTER

    assert sm.transition_to(ConnectionState.ADAPTER_FOUND, "Adaptador encontrado") is True
    assert sm.transition_to(ConnectionState.CONNECTING_ADAPTER, "Conectando serie") is True
    assert sm.transition_to(ConnectionState.ADAPTER_CONNECTED, "Serie conectado") is True
    assert sm.transition_to(ConnectionState.INITIALIZING_PROTOCOL, "Iniciando protocolo") is True
    assert sm.transition_to(ConnectionState.VEHICLE_CONNECTED, "Vehiculo respondiendo") is True
    assert sm.transition_to(ConnectionState.CAPABILITY_DISCOVERY, "Descubriendo PIDs") is True
    assert sm.transition_to(ConnectionState.READY, "Listo para capturar") is True
    assert sm.transition_to(ConnectionState.CAPTURING, "Iniciando captura") is True
    assert sm.state == ConnectionState.CAPTURING
    assert sm.get_status()["is_capturing"] is True


def test_simulator_transport():
    transport = SimulatorTransport()
    assert transport.connect() is True
    res = transport.query_pid("RPM")
    assert res["success"] is True
    assert res["value"] > 0.0
    assert "rpm" in res["unit"].lower()
    metrics = transport.get_transport_metrics()
    assert metrics["successful_queries"] == 1
    assert transport.disconnect() is True

def test_atomic_parquet_store():
    with tempfile.TemporaryDirectory() as tmp_dir:
        store = TelemetryStore(base_dir=tmp_dir)
        session_id = "test_session_123"

        samples = [
            {"session_id": session_id, "timestamp_monotonic": 0.1, "timestamp_utc": "2026-07-28T16:00:00Z", "pid": "RPM", "value": 850.0, "unit": "rpm", "ecu": "ENGINE", "quality": 1.0, "latency_ms": 5.2, "raw_response": "41 0C 03 52"},
            {"session_id": session_id, "timestamp_monotonic": 0.2, "timestamp_utc": "2026-07-28T16:00:01Z", "pid": "SPEED", "value": 0.0, "unit": "kph", "ecu": "ENGINE", "quality": 1.0, "latency_ms": 4.8, "raw_response": "41 0D 00"}
        ]

        file_path = store.save_samples(session_id, samples)
        assert os.path.exists(file_path)
        assert not os.path.exists(f"{file_path}.partial")

        df = store.load_session_dataframe(session_id)
        assert df is not None
        assert len(df) == 2
        assert "RPM" in df["pid"].to_list()

def test_session_quality_calculator():
    calc = SessionQualityCalculator()
    data = {
        "session_id": ["s1", "s1", "s1", "s1"],
        "timestamp_monotonic": [0.1, 0.2, 0.3, 0.4],
        "timestamp_utc": ["", "", "", ""],
        "pid": ["RPM", "SPEED", "ENGINE_LOAD", "COOLANT_TEMP"],
        "value": [850.0, 0.0, 20.0, 88.0],
        "unit": ["rpm", "kph", "%", "C"],
        "ecu": ["ENGINE", "ENGINE", "ENGINE", "ENGINE"],
        "quality": [1.0, 1.0, 1.0, 1.0],
        "latency_ms": [10.0, 12.0, 11.0, 15.0],
        "raw_response": ["", "", "", ""]
    }
    df = pl.DataFrame(data)
    quality = calc.calculate_quality(df)
    assert quality["overall_score"] > 80.0
    assert quality["signal_completeness"] == 100.0

def test_evidence_catalog():
    catalog = EvidenceCatalog(session_id="s1")
    ev_id = catalog.add_evidence(10.0, 15.0, ["MAP", "MAF"], "Caída de MAP detectada", {"drop_percent": 18.5})
    assert ev_id == "EV-001"
    assert catalog.validate_citation("EV-001") is True
    assert catalog.validate_citation("EV-999") is False

def test_baseline_builder():
    builder = VehicleBaselineBuilder(vehicle_id="v1")
    data = {
        "pid": ["RPM", "RPM", "RPM", "COOLANT_TEMP", "COOLANT_TEMP"],
        "value": [800.0, 810.0, 805.0, 85.0, 86.0]
    }
    df = pl.DataFrame(data)
    baseline = builder.build_baseline([df], context_name="idle_warm")
    assert baseline["status"] == "VALID"
    assert "RPM" in baseline["signals"]
    assert baseline["signals"]["RPM"]["p50"] == 805.0
