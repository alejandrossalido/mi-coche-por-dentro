"""
Tests unitarios para servicios avanzados: AIService, SessionComparator, ReportGenerator y Launcher.
"""
import polars as pl
from analysis.ai_service import AIService
from analysis.comparator import SessionComparator
from analysis.report_generator import ReportGenerator

def test_ai_service_response_schema():
    ai = AIService()
    vehicle = {"display_name": "Golf GTI 2.0 TSI", "engine": "2.0 TSI", "fuel_type": "Gasolina"}
    dtcs = [{"code": "P0171", "status": "confirmed", "description": "System Too Lean (Bank 1)"}]
    stats = {
        "signals": {
            "RPM": {"has_data": True, "min": 800, "max": 2500, "mean": 1200, "std": 150, "unit": "rpm"},
            "COOLANT_TEMP": {"has_data": True, "min": 20, "max": 65, "mean": 55, "std": 10, "unit": "°C"}
        }
    }
    rule_findings = [
        {"rule_id": "RULE_THERMOSTAT_STICKING_OPEN", "finding_type": "COOLING_SYSTEM_ANOMALY", "severity": "warning", "message": "Termostato abierto."}
    ]

    resp = ai.analyze_session(vehicle_info=vehicle, dtcs=dtcs, stats=stats, rule_findings=rule_findings)
    assert resp.confidence_level > 0.5
    assert len(resp.observed_facts) > 0
    assert len(resp.hypotheses) > 0
    assert len(resp.recommended_checks) > 0

def test_session_comparator():
    df_a = pl.DataFrame({
        "pid": ["RPM", "COOLANT_TEMP"],
        "value": [1000.0, 40.0],
        "timestamp_monotonic": [1.0, 1.0]
    })
    df_b = pl.DataFrame({
        "pid": ["RPM", "COOLANT_TEMP"],
        "value": [850.0, 90.0],
        "timestamp_monotonic": [1.0, 1.0]
    })

    comp = SessionComparator.compare_sessions(df_a, df_b, "Sesión Frío", "Sesión Caliente")
    assert "signals_compared" in comp
    assert "RPM" in comp["signals_compared"]
    assert comp["signals_compared"]["RPM"]["delta_mean"] == -150.0

def test_report_generator_html():
    vehicle = {"display_name": "Golf GTI", "make": "VW", "model": "Golf", "engine": "2.0 TSI", "fuel_type": "Gasolina"}
    session = {"id": "test_session_123"}
    stats = {"signals": {"RPM": {"has_data": True, "min": 800, "max": 2500, "mean": 1200, "std": 150, "unit": "rpm"}}}
    findings = [{"rule_id": "TEST_RULE", "message": "Mensaje de prueba"}]

    html = ReportGenerator.generate_html_report(vehicle, session, stats, findings)
    assert "<!DOCTYPE html>" in html
    assert "Golf GTI" in html
    assert "TEST_RULE" in html
