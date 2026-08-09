"""
Módulo de descubrimiento automático de PIDs por vehículo.
Inspecciona la compatibilidad real expuesta por la ECU y evalúa frecuencia y estabilidad de cada señal.
"""
import time
from typing import Dict, List, Any
import logging

try:
    import obd
    from obd import commands
except ImportError:
    obd = None
    commands = None

logger = logging.getLogger(__name__)

# PIDs OBD-II estándar principales
STANDARD_PIDS = [
    ("RPM", "01", "0C", "Engine RPM", "rpm"),
    ("SPEED", "01", "0D", "Vehicle Speed", "km/h"),
    ("COOLANT_TEMP", "01", "05", "Engine Coolant Temp", "°C"),
    ("INTAKE_TEMP", "01", "0F", "Intake Air Temp", "°C"),
    ("MAF", "01", "10", "Mass Air Flow", "g/s"),
    ("INTAKE_PRESSURE", "01", "0B", "Intake Manifold Pressure (MAP)", "kPa"),
    ("ENGINE_LOAD", "01", "04", "Calculated Engine Load", "%"),
    ("THROTTLE_POS", "01", "11", "Throttle Position", "%"),
    ("THROTTLE_ACTUATOR", "01", "4C", "Commanded Throttle Actuator", "%"),
    ("ACCELERATOR_POS_D", "01", "49", "Accelerator Pedal Position D", "%"),
    ("ACCELERATOR_POS_E", "01", "4A", "Accelerator Pedal Position E", "%"),
    ("RELATIVE_ACCEL_POS", "01", "5A", "Relative Accelerator Pedal Position", "%"),
    ("OIL_TEMP", "01", "5C", "Engine Oil Temperature", "°C"),
    ("AMBIANT_AIR_TEMP", "01", "46", "Ambient Air Temperature", "°C"),
    ("CATALYST_TEMP_B1S1", "01", "3C", "Catalyst Temperature Bank 1 Sensor 1", "°C"),
    ("CATALYST_TEMP_B2S1", "01", "3D", "Catalyst Temperature Bank 2 Sensor 1", "°C"),
    ("CATALYST_TEMP_B1S2", "01", "3E", "Catalyst Temperature Bank 1 Sensor 2", "°C"),
    ("CATALYST_TEMP_B2S2", "01", "3F", "Catalyst Temperature Bank 2 Sensor 2", "°C"),
    ("BAROMETRIC_PRESSURE", "01", "33", "Barometric Pressure", "kPa"),
    ("COMMANDED_EGR", "01", "2C", "Commanded EGR", "%"),
    ("EGR_ERROR", "01", "2D", "EGR Error", "%"),
    ("SHORT_FUEL_TRIM_1", "01", "06", "Short Term Fuel Trim Bank 1", "%"),
    ("LONG_FUEL_TRIM_1", "01", "07", "Long Term Fuel Trim Bank 1", "%"),
    ("FUEL_STATUS", "01", "03", "Fuel System Status", "state"),
    ("FUEL_PRESSURE", "01", "0A", "Fuel Pressure", "kPa"),
    ("FUEL_RAIL_PRESSURE_DIRECT", "01", "23", "Fuel Rail Gauge Pressure", "kPa"),
    ("FUEL_RAIL_PRESSURE_ABS", "01", "59", "Fuel Rail Absolute Pressure", "kPa"),
    ("COMMANDED_EQUIV_RATIO", "01", "44", "Commanded Equivalence Ratio", "lambda"),
    ("FUEL_INJECT_TIMING", "01", "5D", "Fuel Injection Timing", "degree"),
    ("FUEL_RATE", "01", "5E", "Engine Fuel Rate", "L/h"),
    ("CONTROL_MODULE_VOLTAGE", "01", "42", "Control Module Voltage", "V"),
    ("ELM_VOLTAGE", "AT", "RV", "OBD Adapter Supply Voltage", "V"),
    ("RUN_TIME", "01", "1F", "Time Since Engine Start", "s"),
]

class PIDDiscovery:
    def __init__(self, adapter_connection=None):
        self.connection = adapter_connection

    def discover_supported_pids(self) -> List[Dict[str, Any]]:
        """
        Descubre los PIDs soportados por la ECU conectada.
        Prueba cada PID para verificar respuesta real (Status: Compatible, Irregular, No Compatible).
        """
        results = []
        
        if self.connection is None or not hasattr(self.connection, "supports"):
            # Sin conexión real a la ECU, marcar como no verificado (evitar compatibilidad falsa)
            for name, mode, pid_hex, desc, unit in STANDARD_PIDS:
                results.append({
                    "pid_name": name,
                    "mode": mode,
                    "pid": pid_hex,
                    "description": desc,
                    "unit": unit,
                    "supported_reported": False,
                    "supported_verified": False,
                    "avg_latency_ms": 0.0,
                    "success_rate": 0.0,
                    "status": "not_tested",
                    "reason": "NO_VEHICLE_CONNECTION"
                })
            return results


        for name, mode, pid_hex, desc, unit in STANDARD_PIDS:
            cmd = getattr(commands, name, None)
            if cmd is None:
                continue

            # Los comandos AT del propio adaptador no aparecen en el mapa de
            # PIDs de la ECU, aunque sí se puedan consultar.
            reported = name == "ELM_VOLTAGE" or self.connection.supports(cmd)
            verified = False
            latencies = []
            success_count = 0
            trials = 3

            if reported:
                for _ in range(trials):
                    t0 = time.time()
                    resp = self.connection.query(cmd)
                    t_diff = (time.time() - t0) * 1000.0
                    latencies.append(t_diff)
                    if resp and not resp.is_null():
                        success_count += 1
                
                success_rate = success_count / float(trials)
                verified = success_count > 0
                avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
                status = "compatible" if success_rate > 0.8 else ("irregular" if success_rate > 0 else "unresponsive")
            else:
                success_rate = 0.0
                avg_lat = 0.0
                status = "unsupported"

            results.append({
                "pid_name": name,
                "mode": mode,
                "pid": pid_hex,
                "description": desc,
                "unit": unit,
                "supported_reported": reported,
                "supported_verified": verified,
                "avg_latency_ms": round(avg_lat, 2),
                "success_rate": round(success_rate, 2),
                "status": status
            })

        return results
