"""
Transporte serie para adaptadores ELM327 y STN (Vgate vLinker FS/MC+, OBDLink LX/EX).
Implementa negociación dinámica de baudrate con fallback seguro y métricas de ida y vuelta.
"""
import time
import logging
from typing import Dict, Any, Optional, List
import serial.tools.list_ports

from collector.transports.base_transport import BaseTelemetryTransport, TransportType

try:
    import obd
    from obd import commands
except ImportError:
    obd = None
    commands = None

logger = logging.getLogger(__name__)

# Velocidades preferidas de mayor a menor para negociación serie
PREFERRED_BAUDRATES = [3000000, 2000000, 1000000, 500000, 115200, 38400]

# Lista blanca estricta e inmutable de comandos OBD-II de solo lectura (Modo 01)
READ_ONLY_COMMANDS = frozenset({
    "RPM", "SPEED", "ENGINE_LOAD", "THROTTLE_POS", "MAF", "INTAKE_PRESSURE",
    "COOLANT_TEMP", "INTAKE_TEMP", "CONTROL_MODULE_VOLTAGE", "RUN_TIME",
    "SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "FUEL_PRESSURE", "TIMING_ADVANCE",
    "O2_B1S1", "O2_B1S2", "DISTANCE_W_MIL", "GET_DTC"
})

class ElmStnSerialTransport(BaseTelemetryTransport):
    def __init__(self):
        super().__init__(TransportType.SERIAL_ELM_STN)
        self.active_port: Optional[str] = None
        self.active_baudrate: int = 115200
        self.connection = None
        self.total_queries: int = 0
        self.successful_queries: int = 0
        self.timeout_queries: int = 0
        self.no_data_queries: int = 0
        self.total_round_trip_ms: float = 0.0

    def list_available_ports(self) -> List[Dict[str, str]]:
        """Escanea los puertos COM disponibles en la máquina local."""
        ports = serial.tools.list_ports.comports()
        result = []
        for p in ports:
            description = p.description or ""
            result.append({
                "port": p.device,
                "description": description,
                "hwid": p.hwid or "",
                "is_vlinker_or_obd": any(k in description.lower() for k in ["vlinker", "obd", "ftdi", "ch340", "silicon labs", "bluetooth"])
            })
        return result


    def connect(self, port_or_uri: Optional[str] = None, **kwargs) -> bool:
        """
        Conecta negociando la mejor velocidad serie admitida con fallback seguro.
        """
        target_port = port_or_uri
        if not target_port:
            available = self.list_available_ports()
            obd_ports = [p["port"] for p in available if p["is_vlinker_or_obd"]]
            if obd_ports:
                target_port = obd_ports[0]
            elif available:
                target_port = available[0]["port"]

        if not target_port:
            logger.error("No se encontró ningún puerto COM disponible para el adaptador OBD.")
            self.is_connected = False
            return False

        if obd is None:
            logger.warning("Librería python-OBD no disponible. Utilizando fallback simulado.")
            self.is_connected = False
            return False

        # Intentar negociación de baudrate desde el más rápido al más seguro
        for baud in PREFERRED_BAUDRATES:
            logger.info(f"Probando conexión en puerto {target_port} a {baud} bps...")
            try:
                conn = obd.OBD(portstr=target_port, baudrate=baud, fast=True)
                if conn.status() in [obd.OBDStatus.CAR_CONNECTED, obd.OBDStatus.OBD_CONNECTED]:
                    self.connection = conn
                    self.active_port = target_port
                    self.active_baudrate = baud
                    self.is_connected = True
                    logger.info(f"Conexión serie establecida con éxito en {target_port} a {baud} bps (Estado: {conn.status()}).")
                    return True
                else:
                    conn.close()
            except Exception as e:
                logger.debug(f"Fallo conectando a {baud} bps en {target_port}: {e}")

        logger.error(f"No se pudo establecer comunicación válida con la ECU en {target_port}.")
        self.is_connected = False
        return False

    def disconnect(self) -> bool:
        """Cierra el puerto serie limpiamente."""
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                logger.error(f"Error cerrando puerto serie: {e}")
            self.connection = None
        self.is_connected = False
        return True

    def query_pid(self, pid_name: str) -> Dict[str, Any]:
        """Ejecuta la consulta serie de un PID y registra métricas de idas y vueltas."""
        self.total_queries += 1
        t0 = time.time()

        if pid_name not in READ_ONLY_COMMANDS:
            return {
                "pid": pid_name,
                "value": None,
                "unit": "",
                "success": False,
                "query_round_trip_ms": (time.time() - t0) * 1000.0,
                "raw_response": "",
                "error": "COMMAND_NOT_ALLOWED"
            }

        if not self.is_connected or not self.connection or commands is None:
            return {
                "pid": pid_name,
                "value": None,
                "unit": "",
                "success": False,
                "query_round_trip_ms": 0.0,
                "raw_response": "",
                "error": "NOT_CONNECTED"
            }


        cmd = getattr(commands, pid_name, None)
        if not cmd:
            return {
                "pid": pid_name,
                "value": None,
                "unit": "",
                "success": False,
                "query_round_trip_ms": (time.time() - t0) * 1000.0,
                "raw_response": "",
                "error": "UNKNOWN_PID"
            }

        try:
            resp = self.connection.query(cmd)
            round_trip_ms = (time.time() - t0) * 1000.0
            self.total_round_trip_ms += round_trip_ms

            if resp is None or resp.is_null():
                self.no_data_queries += 1
                return {
                    "pid": pid_name,
                    "value": None,
                    "unit": "",
                    "success": False,
                    "query_round_trip_ms": round_trip_ms,
                    "raw_response": str(resp.value) if resp else "NO_DATA",
                    "error": "NO_DATA"
                }

            val = float(resp.value.magnitude) if hasattr(resp.value, "magnitude") else float(resp.value)
            unit = str(resp.value.units) if hasattr(resp.value, "units") else ""

            self.successful_queries += 1
            return {
                "pid": pid_name,
                "value": val,
                "unit": unit,
                "success": True,
                "query_round_trip_ms": round_trip_ms,
                "raw_response": str(resp.raw_string) if hasattr(resp, "raw_string") else "",
                "error": None
            }
        except Exception as e:
            round_trip_ms = (time.time() - t0) * 1000.0
            self.timeout_queries += 1
            return {
                "pid": pid_name,
                "value": None,
                "unit": "",
                "success": False,
                "query_round_trip_ms": round_trip_ms,
                "raw_response": "",
                "error": str(e)
            }

    def get_transport_metrics(self) -> Dict[str, Any]:
        """Retorna las métricas precisas de rendimiento y tasa de respuestas."""
        avg_round_trip = (self.total_round_trip_ms / self.total_queries) if self.total_queries > 0 else 0.0
        success_rate = (self.successful_queries / self.total_queries) if self.total_queries > 0 else 0.0
        timeout_rate = (self.timeout_queries / self.total_queries) if self.total_queries > 0 else 0.0
        no_data_rate = (self.no_data_queries / self.total_queries) if self.total_queries > 0 else 0.0

        return {
            "transport_type": self.transport_type.value,
            "port": self.active_port,
            "baudrate": self.active_baudrate,
            "is_connected": self.is_connected,
            "total_queries": self.total_queries,
            "successful_queries": self.successful_queries,
            "success_rate": round(success_rate, 4),
            "timeout_rate": round(timeout_rate, 4),
            "no_data_rate": round(no_data_rate, 4),
            "avg_query_round_trip_ms": round(avg_round_trip, 2)
        }
