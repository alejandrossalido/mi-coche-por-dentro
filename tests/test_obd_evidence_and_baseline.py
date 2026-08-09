from types import SimpleNamespace

import obd
import polars as pl

from analysis.historical_baseline import HistoricalBaselineService
from backend import main as backend_main
from collector.mode06 import Mode06Analyzer
from database.db import DatabaseManager


class FakeResponse:
    def __init__(self, value=None):
        self.value = value

    def is_null(self):
        return self.value is None

    def __bool__(self):
        return True


def test_mode06_returns_only_real_supported_monitor_results():
    supported = obd.commands.MONITOR_MISFIRE_CYLINDER_1
    test = SimpleNamespace(
        tid=0x01,
        name="MISFIRE_COUNT",
        desc="Recuento de fallos de encendido",
        value=2,
        min=0,
        max=10,
        passed=True,
    )

    class Connection:
        def supports(self, command):
            return command == supported

        def query(self, command):
            assert command == supported
            return FakeResponse(SimpleNamespace(tests=[test]))

    monitors = Mode06Analyzer.get_mode06_monitors("v1", Connection())

    assert len(monitors) == 1
    assert monitors[0]["source"] == "ECU_MODE_06"
    assert monitors[0]["value"] == 2.0
    assert monitors[0]["passed"] is True


def test_dtc_scan_links_session_and_persists_real_freeze_frame(monkeypatch, tmp_path):
    test_db = DatabaseManager(str(tmp_path / "dtc.db"))
    vehicle = test_db.create_vehicle("Coche", make="Ford", model="Focus", year=2018)
    session = test_db.create_session(vehicle["id"])

    class Connection:
        def supports(self, command):
            return command == obd.commands.DTC_RPM

        def query(self, command):
            if command == obd.commands.GET_DTC:
                return FakeResponse([("P0301", "Cylinder 1 misfire")])
            if command == obd.commands.GET_CURRENT_DTC:
                return FakeResponse([])
            if command == obd.commands.STATUS:
                return FakeResponse(SimpleNamespace(MIL=True))
            if command == obd.commands.DTC_FREEZE_DTC:
                return FakeResponse("P0301")
            if command == obd.commands.DTC_RPM:
                return FakeResponse(SimpleNamespace(magnitude=1250, units="rpm"))
            return FakeResponse()

    monkeypatch.setattr(backend_main, "db", test_db)
    monkeypatch.setattr(backend_main.adapter, "connection", Connection())

    result = backend_main._perform_dtc_scan(
        vehicle["id"],
        "initial",
        session_id=session["id"],
    )

    assert result["session_id"] == session["id"]
    assert result["scan_type"] == "initial"
    assert result["dtcs"][0]["code"] == "P0301"
    frames = test_db.list_freeze_frames(result["dtcs"][0]["id"])
    assert frames == [
        {
            "id": frames[0]["id"],
            "dtc_record_id": result["dtcs"][0]["id"],
            "parameter": "RPM",
            "value": 1250.0,
            "unit": "rpm",
        }
    ]


def test_historical_baseline_requires_three_measured_clean_sessions(tmp_path):
    test_db = DatabaseManager(str(tmp_path / "baseline.db"))
    vehicle = test_db.create_vehicle("Coche", make="Hyundai", model="Kona", year=2022)
    frames = {}

    class Store:
        def load_session_dataframe(self, session_id):
            return frames[session_id]

    service = HistoricalBaselineService(
        test_db,
        Store(),
        lambda frame, powertrain: [],
    )
    for offset in (0, 5):
        session = test_db.create_session(vehicle["id"], engine_condition="warm")
        test_db.stop_session(session["id"], quality_score=90)
        frames[session["id"]] = pl.DataFrame(
            {
                "pid": ["RPM"] * 6,
                "value": [800 + offset, 805 + offset, 810 + offset, 800 + offset, 805 + offset, 810 + offset],
                "unit": ["rpm"] * 6,
                "data_source": ["measured"] * 6,
            }
        )

    learning = service.build(vehicle["id"], engine_condition="warm")
    assert learning["available"] is False
    assert learning["remaining_session_count"] == 1

    session = test_db.create_session(vehicle["id"], engine_condition="warm")
    test_db.stop_session(session["id"], quality_score=90)
    frames[session["id"]] = pl.DataFrame(
        {
            "pid": ["RPM"] * 6,
            "value": [810, 815, 820, 810, 815, 820],
            "unit": ["rpm"] * 6,
            "data_source": ["measured"] * 6,
        }
    )

    baseline = service.build(vehicle["id"], engine_condition="warm")
    assert baseline["available"] is True
    assert baseline["qualifying_session_count"] == 3
    assert baseline["signals"]["RPM"]["session_count"] == 3
