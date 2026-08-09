"""
Decodificador y Analizador del Modo 06 (On-board diagnostic monitoring test results).
Procesa resultados de pruebas de monitorización no continua:
- Monitores de emisiones (Catalizador, EGR, Evaporativo, Sondas O2).
- Contadores de fallos de encendido por cilindro (Misfire Cylinder 1..4).
"""
from typing import List, Dict, Any, Optional

class Mode06Analyzer:
    @staticmethod
    def get_mode06_monitors(
        vehicle_id: str,
        adapter_connection: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Lee y decodifica únicamente monitores Modo 06 que la ECU declara
        compatibles. Sin conexión real no devuelve resultados.

        Las versiones antiguas generaban monitores de ejemplo. Ese comportamiento
        se elimina para no presentar datos sintéticos como si procedieran de la ECU.
        """
        if adapter_connection is None:
            return []

        try:
            import obd
        except ImportError:
            return []

        monitor_commands = [
            command
            for command in obd.commands[6]
            if command is not None
            and getattr(command, "mode", None) == 6
            and str(getattr(command, "name", "")).startswith("MONITOR_")
        ]
        monitors: List[Dict[str, Any]] = []
        for command in monitor_commands:
            try:
                if hasattr(adapter_connection, "supports") and not adapter_connection.supports(command):
                    continue
                response = adapter_connection.query(command)
                if not response or response.is_null():
                    continue
                for test in getattr(response.value, "tests", []) or []:
                    value, unit = Mode06Analyzer._quantity_parts(test.value)
                    minimum, min_unit = Mode06Analyzer._quantity_parts(test.min)
                    maximum, max_unit = Mode06Analyzer._quantity_parts(test.max)
                    if value is None or minimum is None or maximum is None:
                        continue
                    monitors.append(
                        {
                            "mid": f"{int(getattr(command, 'pid', 0)):02X}",
                            "tid": f"{int(getattr(test, 'tid', 0)):02X}",
                            "name": str(getattr(test, "name", "") or command.name),
                            "description": str(
                                getattr(test, "desc", "") or command.desc
                            ),
                            "value": value,
                            "min": minimum,
                            "max": maximum,
                            "unit": unit or min_unit or max_unit,
                            "passed": bool(getattr(test, "passed", False)),
                            "source": "ECU_MODE_06",
                        }
                    )
            except Exception:
                # Algunos fabricantes anuncian un MID pero no responden al
                # detalle. Se omite ese monitor; nunca se rellena con un valor.
                continue
        return monitors

    @staticmethod
    def _quantity_parts(value: Any):
        magnitude = getattr(value, "magnitude", value)
        unit = str(getattr(value, "units", "") or "")
        try:
            return round(float(magnitude), 4), unit
        except (TypeError, ValueError):
            return None, unit
