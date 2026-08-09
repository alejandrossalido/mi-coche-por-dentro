"""
Servidor MCP (Model Context Protocol) de solo lectura para 'Mi Coche por Dentro'.
Expone herramientas seguras para consulta de estado, DTCs, sesiones y análisis por IA.
"""
import json
import asyncio
from typing import Dict, Any, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from database.db import DatabaseManager
from database.parquet_store import TelemetryStore
from analysis.statistics import SignalStatistics
from analysis.rules_engine import RuleEngine
from analysis.event_analyzer import EventWindowAnalyzer

db = DatabaseManager()
telemetry_store = TelemetryStore()
rule_engine = RuleEngine()

mcp_app = Server("vehicle-ai-mcp")

TOOLS = [
    Tool(
        name="get_adapter_status",
        description="Obtiene el estado de conexión actual con el adaptador OBDLink LX y el vehículo.",
        inputSchema={"type": "object", "properties": {}}
    ),
    Tool(
        name="list_vehicles",
        description="Lista todos los vehículos registrados en el expediente del garaje local.",
        inputSchema={"type": "object", "properties": {}}
    ),
    Tool(
        name="read_fault_codes",
        description="Recupera el histórico y los registros de códigos de avería (DTC) escaneados para un vehículo.",
        inputSchema={
            "type": "object",
            "properties": {
                "vehicle_id": {"type": "string", "description": "ID del vehículo"}
            },
            "required": ["vehicle_id"]
        }
    ),
    Tool(
        name="list_sessions",
        description="Lista las sesiones de telemetría registradas para un vehículo.",
        inputSchema={
            "type": "object",
            "properties": {
                "vehicle_id": {"type": "string", "description": "ID del vehículo"}
            }
        }
    ),
    Tool(
        name="get_session_summary",
        description="Obtiene el resumen estadístico determinista y muestras de una sesión de telemetría.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "ID de la sesión"}
            },
            "required": ["session_id"]
        }
    ),
    Tool(
        name="find_anomalies",
        description="Ejecuta el motor de reglas deterministas sobre una sesión para detectar fallos objetivamente.",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "ID de la sesión"}
            },
            "required": ["session_id"]
        }
    ),
    Tool(
        name="get_event_window",
        description="Extrae la ventana de telemetría de ±10 segundos alrededor de un evento marcado (ej. tirón, humo, vibración).",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "ID de la sesión"},
                "offset_ms": {"type": "number", "description": "Offset en milisegundos del marcador de evento"}
            },
            "required": ["session_id", "offset_ms"]
        }
    ),
    Tool(
        name="get_service_action_information",
        description="Obtiene información y documentación técnica sobre una función de servicio (ej. EPB, reset de servicio).",
        inputSchema={
            "type": "object",
            "properties": {
                "action_id": {"type": "string", "description": "ID de la acción de servicio (ej: EPB_SERVICE_MODE, OIL_RESET)"}
            },
            "required": ["action_id"]
        }
    ),
    Tool(
        name="get_service_action_risks",
        description="Obtiene las advertencias de seguridad y riesgos de una función de servicio.",
        inputSchema={
            "type": "object",
            "properties": {
                "action_id": {"type": "string", "description": "ID de la acción de servicio"}
            },
            "required": ["action_id"]
        }
    ),

]

@mcp_app.list_tools()
async def list_tools() -> List[Tool]:
    return TOOLS

@mcp_app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if name == "get_adapter_status":
        return [TextContent(type="text", text=json.dumps({"state": "SIMULATED_OR_DISCONNECTED", "is_connected": False}))]
    
    elif name == "list_vehicles":
        vehicles = db.list_vehicles()
        return [TextContent(type="text", text=json.dumps(vehicles, indent=2))]

    elif name == "read_fault_codes":
        v_id = arguments.get("vehicle_id", "")
        scans = db.list_dtc_scans(v_id)
        return [TextContent(type="text", text=json.dumps(scans, indent=2))]


    elif name == "list_sessions":
        v_id = arguments.get("vehicle_id")
        sessions = db.list_sessions(vehicle_id=v_id)
        return [TextContent(type="text", text=json.dumps(sessions, indent=2))]

    elif name == "get_session_summary":
        s_id = arguments.get("session_id", "")
        df = telemetry_store.load_session_dataframe(s_id)
        if df is None or df.is_empty():
            return [TextContent(type="text", text=json.dumps({"error": "No data found for session"}))]
        stats = SignalStatistics.analyze_full_session(df)
        return [TextContent(type="text", text=json.dumps(stats, indent=2))]

    elif name == "find_anomalies":
        s_id = arguments.get("session_id", "")
        df = telemetry_store.load_session_dataframe(s_id)
        findings = rule_engine.evaluate_session(df)
        return [TextContent(type="text", text=json.dumps(findings, indent=2))]

    elif name == "get_event_window":
        s_id = arguments.get("session_id", "")
        offset = float(arguments.get("offset_ms", 0.0))
        df = telemetry_store.load_session_dataframe(s_id)
        analyzer = EventWindowAnalyzer()
        impact = analyzer.analyze_event_impact(df, offset)
        return [TextContent(type="text", text=json.dumps(impact, indent=2))]

    elif name == "get_service_action_information":
        action_id = arguments.get("action_id", "")
        info = {
            "action_id": action_id,
            "status": "DOCUMENTATION_ONLY",
            "description": f"Guía técnica e información del procedimiento para {action_id}",
            "requires_human_confirmation": True,
            "requires_v2_plugin": True
        }
        return [TextContent(type="text", text=json.dumps(info, indent=2))]

    elif name == "get_service_action_risks":
        action_id = arguments.get("action_id", "")
        risks = {
            "action_id": action_id,
            "warnings": [
                "Esta acción altera estados físicos del vehículo.",
                "Debe realizarse con el vehículo inmovilizado y bajo supervisión técnica.",
                "Se requiere confirmación física y token de un solo uso generado en el Dashboard local."
            ]
        }
        return [TextContent(type="text", text=json.dumps(risks, indent=2))]

    return [TextContent(type="text", text=json.dumps({"error": f"Tool '{name}' not found"}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await mcp_app.run(read_stream, write_stream, mcp_app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
