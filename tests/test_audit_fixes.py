r"""
Batería de pruebas unitarias y de integración para verificar todos los bloques P0, P1 y P2 de la auditoría:
- Uso de InMemoryStore en poller (sin dejar basura en data/telemetry).
- Re-inserción de muestras en buffer si save_samples falla.
- Rechazo de Path Traversal (..\..) en TelemetryStore.
- Manejo de CorruptSessionFile si Parquet está dañado.
- Rechazo de PIDs fuera de la lista blanca de solo lectura en ElmStnSerialTransport.
- Estado not_tested sin vehículo en PIDDiscovery.
- Validación de saltos ilegales en ConnectionStateMachine.
- PRAGMA foreign_keys y sqlite3.Row en DatabaseManager.
- Filtrado de powertrain_type='bev' en RuleEngine para EVs.
- Rechazo de PIDs desconocidos con UNKNOWN_PID en SimulatorTransport.
"""

import pytest
import time
import os
import uuid
from collector.poller import TelemetryPoller
from collector.transports.elm_stn_serial import ElmStnSerialTransport
from collector.transports.simulator_transport import SimulatorTransport
from collector.pid_discovery import PIDDiscovery
from collector.connection_state_machine import ConnectionStateMachine, ConnectionState
from database.db import DatabaseManager
from database.parquet_store import TelemetryStore, CorruptSessionFile
from analysis.rules_engine import RuleEngine
from analysis.report_generator import ReportGenerator

class InMemoryStore:
    def __init__(self):
        self.batches = []

    def save_samples(self, session_id: str, samples: list):
        self.batches.append(list(samples))
        return "in_memory"

    def get_session_file_path(self, session_id: str) -> str:
        return f"memory_{session_id}"

def test_poller_no_deadlock_with_in_memory_store():
    store = InMemoryStore()
    os.environ["APP_MODE"] = "demo"
    poller = TelemetryPoller(session_id="test_in_memory", telemetry_store=store)
    poller.start(poll_interval_ms=5)

    deadline = time.monotonic() + 1.5
    while poller.sample_count < 60 and time.monotonic() < deadline:
        time.sleep(0.01)

    poller.stop()
    assert poller.is_running is False
    assert poller.sample_count >= 50
    assert len(store.batches) > 0
    total_flushed = sum(len(b) for b in store.batches)
    assert total_flushed == poller.sample_count

def test_poller_buffer_reinsertion_on_store_failure():
    class FailingStore:
        def __init__(self):
            self.attempts = 0

        def save_samples(self, session_id, samples):
            self.attempts += 1
            if self.attempts == 1:
                raise RuntimeError("Disk full simulation")
            return "ok"

    store = FailingStore()
    poller = TelemetryPoller(session_id="test_fail", telemetry_store=store)
    with poller._buffer_lock:
        poller._samples_buffer = [{"pid": "RPM", "value": 1000}] * 50

    with pytest.raises(RuntimeError):
        poller.flush_buffer()

    # Verificar que el búfer re-insertó las muestras fallidas
    assert len(poller._samples_buffer) == 50

def test_parquet_store_path_traversal_protection(tmp_path):
    store = TelemetryStore(base_dir=str(tmp_path))
    with pytest.raises(ValueError):
        store.validate_session_id("../../../etc/passwd")

    with pytest.raises(ValueError):
        store.validate_session_id("session_id/with/slashes")

    valid_id = str(uuid.uuid4())
    assert store.validate_session_id(valid_id) == valid_id

def test_parquet_store_corrupt_file_handling(tmp_path):
    store = TelemetryStore(base_dir=str(tmp_path))
    session_id = str(uuid.uuid4())
    file_path = store.get_session_file_path(session_id)

    # Crear un archivo de texto corrupto imitando un Parquet dañado
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("CORRUPTED_PARQUET_HEADER_DATA")

    with pytest.raises(CorruptSessionFile):
        store.save_samples(session_id, [{"pid": "RPM", "value": 800}])

def test_serial_transport_readonly_whitelist():
    transport = ElmStnSerialTransport()
    res = transport.query_pid("CLEAR_DTC")
    assert res["success"] is False
    assert res["error"] == "COMMAND_NOT_ALLOWED"

def test_simulator_transport_unknown_pid():
    sim = SimulatorTransport()
    sim.connect()
    res = sim.query_pid("UNKNOWN_INVALID_PID")
    assert res["success"] is False
    assert res["error"] == "UNKNOWN_PID"

def test_pid_discovery_not_tested_without_vehicle():
    discovery = PIDDiscovery(adapter_connection=None)
    pids = discovery.discover_supported_pids()
    assert len(pids) > 0
    for p in pids:
        assert p["status"] == "not_tested"
        assert p["supported_verified"] is False

def test_connection_state_machine_illegal_transition():
    sm = ConnectionStateMachine()
    assert sm.state == ConnectionState.DISCONNECTED
    success = sm.transition_to(ConnectionState.CAPTURING, "Salto ilegal de prueba")
    assert success is False
    assert sm.state == ConnectionState.DISCONNECTED

def test_sqlite_foreign_keys_and_row_factory(tmp_path):
    db_file = os.path.join(tmp_path, "test_db.db")
    db = DatabaseManager(db_path=db_file)
    with db.get_connection() as conn:
        cursor = conn.execute("PRAGMA foreign_keys")
        assert cursor.fetchone()[0] == 1

        v = db.create_vehicle(display_name="Passat B6", make="VW", model="Passat", powertrain_type="diesel")
        assert v["powertrain_type"] == "diesel"

def test_rule_engine_ev_filtering():
    engine = RuleEngine()
    import polars as pl
    df = pl.DataFrame({
        "pid": ["COOLANT_TEMP", "LONG_FUEL_TRIM_1"],
        "value": [50.0, 15.0],
        "timestamp_monotonic": [10.0, 20.0]
    })
    findings = engine.evaluate_session(df, powertrain_type="bev")
    assert len(findings) == 0


def test_analysis_ignores_null_obd_readings():
    import polars as pl
    from analysis.statistics import SignalStatistics

    engine = RuleEngine()
    df = pl.DataFrame(
        {
            "pid": ["COOLANT_TEMP", "RPM", "SPEED"],
            "value": [None, None, None],
            "timestamp_monotonic": [0.0, 0.1, 0.2],
        },
        schema={"pid": pl.String, "value": pl.Float64, "timestamp_monotonic": pl.Float64},
    )

    stats = SignalStatistics.analyze_full_session(df)

    assert engine.evaluate_session(df) == []
    assert stats["valid_samples"] == 0
    assert stats["invalid_samples"] == 3
    assert all(not signal["has_data"] for signal in stats["signals"].values())

def test_report_generator_user_vs_technical_mode():
    vehicle = {"display_name": "Tesla Model 3", "make": "Tesla", "model": "3", "engine": "Electric", "fuel_type": "BEV"}
    session = {"id": "test_sess_id", "capture_quality_score": 95.0}
    stats = {"signals": {"RPM": {"has_data": True, "min": 0, "max": 5000, "mean": 1500, "std": 200, "unit": "rpm"}}}
    findings = [{"rule_id": "test_rule", "message": "Test Message"}]

    html_user = ReportGenerator.generate_html_report(vehicle, session, stats, findings, mode="user")
    html_tech = ReportGenerator.generate_html_report(vehicle, session, stats, findings, mode="technical")

    assert "Resumen de Diagnóstico para el Conductor" in html_user
    assert "Informe Técnico de Diagnóstico OBD-II" in html_tech
    assert "<script>" not in html_user
