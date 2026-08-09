"""
Transporte de simulación sintética de telemetría OBD-II para desarrollo y pruebas sin vehículo conectado.
"""
import time
import math
import random
from typing import Dict, Any, Optional
from collector.transports.base_transport import BaseTelemetryTransport, TransportType

class SimulatorTransport(BaseTelemetryTransport):
    def __init__(self):
        super().__init__(TransportType.SIMULATOR)
        self.start_time: float = 0.0
        self.total_queries: int = 0
        self.successful_queries: int = 0

    def connect(self, port_or_uri: Optional[str] = None, **kwargs) -> bool:
        self.start_time = time.time()
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.is_connected = False
        return True

    def query_pid(self, pid_name: str) -> Dict[str, Any]:
        known_pids = {"RPM", "SPEED", "COOLANT_TEMP", "INTAKE_TEMP", "ENGINE_LOAD", "THROTTLE_POS", "MAF", "INTAKE_PRESSURE", "CONTROL_MODULE_VOLTAGE", "RUN_TIME"}
        if pid_name not in known_pids:
            return {
                "pid": pid_name,
                "value": None,
                "unit": "",
                "success": False,
                "query_round_trip_ms": 1.0,
                "raw_response": "",
                "error": "UNKNOWN_PID"
            }


        self.total_queries += 1
        self.successful_queries += 1
        elapsed = time.time() - self.start_time if self.start_time > 0 else 0.0

        val = 0.0
        unit = ""

        if pid_name == "RPM":
            val = round(800 + 1600 * math.sin(elapsed / 5.0) + random.uniform(-15, 15), 1)
            unit = "rpm"
        elif pid_name == "SPEED":
            val = round(max(0.0, 50.0 + 35.0 * math.sin(elapsed / 10.0) + random.uniform(-2, 2)), 1)
            unit = "kph"
        elif pid_name == "COOLANT_TEMP":
            val = round(min(92.0, 20.0 + elapsed * 0.4), 1)
            unit = "degC"
        elif pid_name == "INTAKE_TEMP":
            val = round(22.0 + random.uniform(-0.5, 0.5), 1)
            unit = "degC"
        elif pid_name == "ENGINE_LOAD":
            val = round(max(10.0, 35.0 + 25.0 * math.sin(elapsed / 4.0) + random.uniform(-2, 2)), 1)
            unit = "percent"
        elif pid_name == "THROTTLE_POS":
            val = round(max(0.0, 15.0 + 30.0 * math.sin(elapsed / 4.0) + random.uniform(-1, 1)), 1)
            unit = "percent"
        elif pid_name == "MAF":
            val = round(max(2.0, 12.0 + 18.0 * math.sin(elapsed / 5.0) + random.uniform(-0.5, 0.5)), 2)
            unit = "gps"
        elif pid_name == "INTAKE_PRESSURE":
            val = round(max(30.0, 101.0 - 45.0 * math.sin(elapsed / 5.0)), 1)
            unit = "kPa"
        elif pid_name == "CONTROL_MODULE_VOLTAGE":
            val = round(14.2 + random.uniform(-0.05, 0.05), 2)
            unit = "V"
        elif pid_name == "RUN_TIME":
            val = round(elapsed, 1)
            unit = "seconds"

        simulated_latency_ms = round(4.0 + random.uniform(-1.0, 2.0), 2)

        return {
            "pid": pid_name,
            "value": val,
            "unit": unit,
            "success": True,
            "query_round_trip_ms": simulated_latency_ms,
            "raw_response": f"41 {pid_name} {val}",
            "error": None
        }


    def get_transport_metrics(self) -> Dict[str, Any]:
        return {
            "transport_type": self.transport_type.value,
            "port": "SIMULATED",
            "baudrate": 0,
            "is_connected": self.is_connected,
            "total_queries": self.total_queries,
            "successful_queries": self.successful_queries,
            "success_rate": 1.0,
            "timeout_rate": 0.0,
            "no_data_rate": 0.0,
            "avg_query_round_trip_ms": 4.5
        }
