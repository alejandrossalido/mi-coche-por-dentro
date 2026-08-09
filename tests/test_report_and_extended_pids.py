import polars as pl

from analysis.diagnostic_summary import DiagnosticSummary
from analysis.rules_engine import RuleEngine
from collector.capture_profiles import CaptureProfileManager
from collector.pid_discovery import STANDARD_PIDS
from collector.poller import FUEL_STATUS_CODES


def test_idle_rule_accepts_polars_series_without_report_crash():
    rows = []
    for index in range(20):
        timestamp = float(index)
        rows.extend(
            [
                {"pid": "SPEED", "value": 0.0, "timestamp_monotonic": timestamp},
                {"pid": "RPM", "value": 800.0, "timestamp_monotonic": timestamp},
            ]
        )

    findings = RuleEngine().evaluate_session(pl.DataFrame(rows))

    assert findings == []


def test_engine_off_samples_do_not_create_false_idle_alert():
    rows = []
    for index in range(40):
        rpm = 0.0 if index < 5 else 805.0 + (index % 3 - 1) * 8.0
        rows.extend(
            [
                {"pid": "SPEED", "value": 0.0, "timestamp_monotonic": float(index)},
                {"pid": "RPM", "value": rpm, "timestamp_monotonic": float(index)},
            ]
        )
    df = pl.DataFrame(rows)

    findings = RuleEngine().evaluate_session(df, powertrain_type="diesel")
    summary = DiagnosticSummary.build(
        df, {}, findings, [], {"overall_score": 90}, "diesel"
    )

    assert not any(
        item["id"] in {"idle_instability", "idle_rpm_instability"}
        for item in summary["alerts"]
    )


def test_complete_profile_requests_every_dashboard_sensor_family():
    profile = CaptureProfileManager.get_profile("COMPLETE_DIAGNOSTIC")
    requested = set(profile["pids"])
    required = {
        "OIL_TEMP",
        "AMBIANT_AIR_TEMP",
        "CATALYST_TEMP_B1S1",
        "BAROMETRIC_PRESSURE",
        "COMMANDED_EGR",
        "EGR_ERROR",
        "FUEL_RAIL_PRESSURE_DIRECT",
        "FUEL_INJECT_TIMING",
        "FUEL_RATE",
        "CONTROL_MODULE_VOLTAGE",
        "ELM_VOLTAGE",
    }

    assert required.issubset(requested)


def test_discovery_catalog_contains_real_python_obd_command_names():
    names = {item[0] for item in STANDARD_PIDS}

    assert "BAROMETRIC_PRESSURE" in names
    assert "COMMANDED_EGR" in names
    assert "AMBIANT_AIR_TEMP" in names
    assert "CATALYST_TEMP_B1S1" in names
    assert "ELM_VOLTAGE" in names
    assert "BARO_PRESSURE" not in names
    assert "EGR_COMMANDED" not in names


def test_fuel_status_codes_are_numeric_and_storable_in_parquet():
    assert FUEL_STATUS_CODES["Closed loop, using oxygen sensor feedback to determine fuel mix"] == 2.0
    assert all(isinstance(value, float) for value in FUEL_STATUS_CODES.values())
