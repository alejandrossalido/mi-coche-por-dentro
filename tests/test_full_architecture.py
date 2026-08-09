"""
Suite de tests integrales para validar la arquitectura completa de 'Mi Coche por Dentro'.
"""
import pytest
import os
import shutil
import polars as pl
from database.db import DatabaseManager
from database.parquet_store import TelemetryStore
from analysis.statistics import SignalStatistics
from analysis.rules_engine import RuleEngine

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_vehicle_ai.db")
TEST_TELEMETRY_DIR = os.path.join(os.path.dirname(__file__), "test_telemetry")

@pytest.fixture(autouse=True)
def cleanup():
    import gc
    gc.collect()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    if os.path.exists(TEST_TELEMETRY_DIR):
        try:
            shutil.rmtree(TEST_TELEMETRY_DIR)
        except Exception:
            pass
    yield
    gc.collect()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    if os.path.exists(TEST_TELEMETRY_DIR):
        try:
            shutil.rmtree(TEST_TELEMETRY_DIR)
        except Exception:
            pass

def test_database_crud():
    db = DatabaseManager(db_path=TEST_DB_PATH)
    v = db.create_vehicle(display_name="Golf GTI", make="VW", model="Golf", year=2018)
    assert v["id"] is not None
    assert v["display_name"] == "Golf GTI"

    s = db.create_session(vehicle_id=v["id"], engine_condition="cold", notes="Test Session")
    assert s["id"] is not None
    assert s["status"] == "recording"

    m = db.add_event_marker(session_id=s["id"], offset_ms=5000, event_type="jerk", note="Tirón fuerte")
    assert m["id"] is not None
    assert m["event_type"] == "jerk"

    s_stopped = db.stop_session(s["id"], quality_score=1.0)
    assert s_stopped["status"] == "completed"
    db.close()

def test_parquet_store_and_statistics():
    store = TelemetryStore(base_dir=TEST_TELEMETRY_DIR)
    samples = [
        {"session_id": "s1", "timestamp_monotonic": 1.0, "timestamp_utc": "2026-07-23T10:00:00", "pid": "RPM", "value": 800.0, "unit": "rpm"},
        {"session_id": "s1", "timestamp_monotonic": 2.0, "timestamp_utc": "2026-07-23T10:00:01", "pid": "RPM", "value": 1500.0, "unit": "rpm"},
        {"session_id": "s1", "timestamp_monotonic": 3.0, "timestamp_utc": "2026-07-23T10:00:02", "pid": "RPM", "value": 2500.0, "unit": "rpm"},
        {"session_id": "s1", "timestamp_monotonic": 1.0, "timestamp_utc": "2026-07-23T10:00:00", "pid": "COOLANT_TEMP", "value": 65.0, "unit": "°C"},
        {"session_id": "s1", "timestamp_monotonic": 600.0, "timestamp_utc": "2026-07-23T10:10:00", "pid": "COOLANT_TEMP", "value": 68.0, "unit": "°C"},
    ]
    file_path = store.save_samples("s1", samples)
    assert os.path.exists(file_path)

    df = store.load_session_dataframe("s1")
    assert df is not None
    assert len(df) == 5

    stats = SignalStatistics.analyze_full_session(df)
    assert "RPM" in stats["signals"]
    assert stats["signals"]["RPM"]["min"] == 800.0
    assert stats["signals"]["RPM"]["max"] == 2500.0

def test_rule_engine():
    engine = RuleEngine()
    df = pl.DataFrame({
        "session_id": ["s1", "s1"],
        "timestamp_monotonic": [1.0, 700.0],
        "timestamp_utc": ["2026-07-23T10:00:00", "2026-07-23T10:11:40"],
        "pid": ["COOLANT_TEMP", "COOLANT_TEMP"],
        "value": [50.0, 65.0],
        "unit": ["°C", "°C"],
        "ecu": ["ENGINE", "ENGINE"],
        "quality": [1.0, 1.0],
        "latency_ms": [5.0, 5.0],
        "raw_response": ["", ""]
    })
    findings = engine.evaluate_session(df)
    assert len(findings) == 1
    assert findings[0]["rule_id"] in ["coolant_low_stable_temperature", "RULE_THERMOSTAT_STICKING_OPEN"]
