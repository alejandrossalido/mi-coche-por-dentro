import polars as pl

from analysis.comparator import SessionComparator
from analysis.ai_service import AIService
from analysis.diagnostic_summary import DiagnosticSummary
from analysis.session_quality import SessionQualityCalculator
from analysis.statistics import SignalStatistics
from collector.capture_profiles import CaptureProfileManager


def _frame(values):
    rows = []
    for index, (pid, value) in enumerate(values):
        rows.append(
            {
                "pid": pid,
                "value": value,
                "timestamp_monotonic": float(index),
                "latency_ms": 8.0,
            }
        )
    return pl.DataFrame(
        rows,
        schema_overrides={
            "pid": pl.String,
            "value": pl.Float64,
            "timestamp_monotonic": pl.Float64,
            "latency_ms": pl.Float64,
        },
    )


def test_empty_capture_has_invalid_conclusion():
    df = _frame([("RPM", None), ("COOLANT_TEMP", None)])
    quality = SessionQualityCalculator().calculate_quality(df)
    result = DiagnosticSummary.build(df, {}, [], [], quality)

    assert result["conclusion"]["verdict"] == "invalid"
    assert result["alerts"][0]["id"] == "capture_no_valid_data"
    assert quality["overall_score"] == 0


def test_threshold_alerts_are_evidence_backed():
    df = _frame(
        [
            ("COOLANT_TEMP", 90.0),
            ("COOLANT_TEMP", 111.0),
            ("CONTROL_MODULE_VOLTAGE", 11.4),
            ("RPM", 850.0),
        ]
    )
    stats = SignalStatistics.analyze_full_session(df)
    quality = SessionQualityCalculator().calculate_quality(df)
    result = DiagnosticSummary.build(df, stats, [], [], quality)

    alert_ids = {alert["id"] for alert in result["alerts"]}
    assert "coolant_temp_high_110.0" in alert_ids
    assert "control_module_voltage_low" in alert_ids
    assert result["conclusion"]["verdict"] == "urgent"


def test_complete_and_specific_guided_profiles_exist():
    profiles = {profile["id"]: profile for profile in CaptureProfileManager.list_profiles()}
    expected = {
        "COMPLETE_DIAGNOSTIC",
        "BATTERY_CHARGING",
        "COOLING_SYSTEM",
        "IDLE_STABILITY",
        "INTAKE_TURBO",
        "FUEL_MIXTURE",
        "EMISSIONS_ITV",
    }

    assert expected.issubset(profiles)
    assert len(profiles["COMPLETE_DIAGNOSTIC"]["steps"]) >= 5


def test_before_after_comparison_produces_conclusion():
    before = _frame([("RPM", 700.0), ("RPM", 1000.0), ("RPM", 850.0)])
    after = _frame([("RPM", 840.0), ("RPM", 850.0), ("RPM", 860.0)])

    result = SessionComparator.compare_sessions(before, after)

    assert result["conclusion"]["verdict"] == "improved"
    assert result["signals_compared"]["RPM"]["stability_improved"] is True


def test_diagnostic_chat_separates_facts_hypotheses_and_actions():
    response = AIService().query_diagnostic_chat(
        user_question="El coche da tirones al acelerar en tercera",
        vehicle_info={"display_name": "Coche de prueba", "powertrain_type": "diesel"},
        dtcs=[],
        stats={
            "signals": {
                "RPM": {"has_data": True, "min": 800, "max": 2800, "mean": 1600, "std": 120},
                "INTAKE_PRESSURE": {"has_data": True, "min": 35, "max": 160, "mean": 90, "std": 20},
            }
        },
        rule_findings=[],
        mode="simple",
    )

    assert response["status"] == "success"
    assert response["recommended_test"]["profile_id"] == "INTAKE_TURBO"
    assert response["hypotheses"][0]["confirmed"] is False
    assert len(response["solutions"]) == 3
    assert response["evidence"][0]["id"] == "EV-001"


def test_diagnostic_chat_does_not_claim_safety_without_data():
    response = AIService().query_diagnostic_chat(
        user_question="¿Puedo seguir circulando?",
        vehicle_info={"display_name": "Coche de prueba"},
        dtcs=[],
        stats={},
        rule_findings=[],
    )

    assert response["urgency"]["level"] == "unknown"
    assert response["urgency"]["can_drive"] is None
