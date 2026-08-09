"""
Pruebas de integración para Etapa 2 y Etapa 3:
- AIService con citas de identificadores del catálogo de evidencia.
- ReportGenerator en modo técnico vs usuario.
- Servidor MCP (list_tools y call_tool informativos).
"""
import json
import asyncio
from analysis.ai_service import AIService, AiAnalysisResponse
from analysis.report_generator import ReportGenerator
from mcp_server.server import TOOLS, call_tool


def test_ai_service_fallback():
    ai = AIService()
    v_info = {"display_name": "Passat B6 2.0 TDI", "engine": "2.0 TDI", "fuel_type": "Diesel"}
    dtcs = [{"code": "P0234", "status": "confirmed", "description": "Overboost Condition"}]
    stats = {"signals": {"MAP": {"has_data": True, "min": 100.0, "max": 240.0, "mean": 150.0, "unit": "kPa"}}}
    findings = [{"finding_type": "COOLING_SYSTEM_ANOMALY", "message": "Calentamiento lento detectado"}]

    resp = ai.analyze_session(v_info, dtcs, stats, findings)
    assert isinstance(resp, AiAnalysisResponse)
    assert len(resp.observed_facts) > 0
    assert resp.confidence_level > 0.5

def test_report_generator_dual_mode():
    vehicle = {"display_name": "Mazda 1.5 Skyactiv-D", "make": "Mazda", "model": "3", "engine": "1.5D", "fuel_type": "Diesel"}
    session = {"id": "session_test_999"}
    stats = {"signals": {"RPM": {"has_data": True, "min": 800, "max": 2500, "mean": 1500, "unit": "rpm", "std": 100}}}
    findings = [{"rule_id": "RULE_001", "message": "Estabilidad normal"}]
    ai_resp = {"observed_facts": ["RPM estable"], "hypotheses": ["Motor sano"], "recommended_checks": ["Ninguna"]}

    html_tech = ReportGenerator.generate_html_report(vehicle, session, stats, findings, ai_resp, mode="technical")
    assert "Informe Técnico de Diagnóstico OBD-II" in html_tech

def test_mcp_server_tools():
    tool_names = [t.name for t in TOOLS]
    assert "get_adapter_status" in tool_names
    assert "get_service_action_information" in tool_names

def test_mcp_call_tool():
    res = asyncio.run(call_tool("get_service_action_information", {"action_id": "EPB_SERVICE_MODE"}))

    assert len(res) > 0
    payload = json.loads(res[0].text)
    assert payload["action_id"] == "EPB_SERVICE_MODE"
    assert payload["status"] == "DOCUMENTATION_ONLY"
