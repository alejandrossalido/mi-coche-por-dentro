"""
Gestor del adaptador OBD (vLinker / OBDLink / Puerto COM).
Utiliza ConnectionStateMachine como única fuente de verdad para el ciclo de vida de la conexión.
"""
import time
import logging
from typing import Optional, List, Dict, Any, Callable
import serial.tools.list_ports
from collector.connection_state_machine import ConnectionStateMachine, ConnectionState

try:
    import obd
except ImportError:
    obd = None

logger = logging.getLogger(__name__)

# Alias de compatibilidad
AdapterState = ConnectionState

class AdapterManager:
    def __init__(self, preferred_port: Optional[str] = None, state_machine: Optional[ConnectionStateMachine] = None):
        self.preferred_port = preferred_port
        self.state_machine = state_machine or ConnectionStateMachine()
        self.connection = None
        self.active_port: Optional[str] = None
        self.protocol_name: Optional[str] = None
        self.latency_ms: float = 0.0
        self._on_state_change_callbacks: List[Callable[[ConnectionState], None]] = []

        self.state_machine.register_callback(self._on_machine_state_change)

    @property
    def state(self) -> ConnectionState:
        return self.state_machine.state

    def set_state(self, new_state: ConnectionState, reason: str = "Asignación directa de estado"):
        self.state_machine.transition_to(new_state, reason)

    def _on_machine_state_change(self, old_state: ConnectionState, new_state: ConnectionState):

        for cb in self._on_state_change_callbacks:
            try:
                cb(new_state)
            except Exception as e:
                logger.error(f"Error en callback de estado: {e}")

    def register_state_callback(self, callback: Callable[[ConnectionState], None]):
        self._on_state_change_callbacks.append(callback)

    def list_available_ports(self) -> List[Dict[str, Any]]:
        """Busca y retorna todos los puertos COM disponibles en Windows."""
        ports = serial.tools.list_ports.comports()
        result = []
        for p in ports:
            description = p.description or ""
            hwid = p.hwid or ""
            identity = f"{description} {hwid} {getattr(p, 'manufacturer', '') or ''}".lower()
            excluded = any(
                marker in identity
                for marker in (
                    "active management technology",
                    "intel(r) amt",
                    "- sol (com",
                )
            )
            priority = 0
            if any(marker in identity for marker in ("vlinker", "vgate", "obdlink", "obd")):
                priority = 100
            elif "vid_0403&pid_6015" in identity or "vid:pid=0403:6015" in identity:
                priority = 90
            elif any(marker in identity for marker in ("usb serial", "ftdi", "ch340", "cp210")):
                priority = 70
            elif "bluetooth" in identity:
                priority = 40
            if excluded:
                priority = -100
            result.append({
                "port": p.device,
                "description": description,
                "hwid": hwid,
                "is_obdlink": priority > 0,
                "priority": priority,
                "excluded": excluded,
            })
        return sorted(result, key=lambda item: (-item["priority"], item["port"]))

    def connect(self, com_port: Optional[str] = None, baudrate: int = 115200, fast: bool = True) -> bool:
        """Conecta al adaptador OBD en el puerto COM especificado o detectado."""
        if self.state != ConnectionState.DISCONNECTED or self.connection is not None:
            self.disconnect()
        self.state_machine.transition_to(ConnectionState.DISCOVERING_ADAPTER, "Iniciando escaneo de puertos")
        target_port = com_port or self.preferred_port

        if not target_port:
            available = self.list_available_ports()
            obd_ports = [p["port"] for p in available if p["is_obdlink"]]
            if obd_ports:
                target_port = obd_ports[0]

        if not target_port:
            self.state_machine.transition_to(ConnectionState.ERROR, "No se encontró ningún puerto COM")
            return False

        self.state_machine.transition_to(ConnectionState.ADAPTER_FOUND, f"Puerto {target_port} seleccionado")
        self.state_machine.transition_to(ConnectionState.CONNECTING_ADAPTER, "Abriendo puerto serie")
        self.active_port = target_port

        if obd is None:
            # Modo Simulación si python-OBD no estuviera cargado
            self.state_machine.transition_to(ConnectionState.ADAPTER_CONNECTED, "Conexión simulada OK")
            self.state_machine.transition_to(ConnectionState.INITIALIZING_PROTOCOL, "Inicializando simulador")
            self.state_machine.transition_to(ConnectionState.VEHICLE_CONNECTED, "Simulador CAN listo")
            self.protocol_name = "SIMULATED_CAN_11BIT_500K"
            return True

        start_time = time.time()
        try:
            self.connection = obd.OBD(portstr=target_port, baudrate=baudrate, fast=fast)
            self.latency_ms = (time.time() - start_time) * 1000.0

            if self.connection.status() == obd.OBDStatus.CAR_CONNECTED:
                self.protocol_name = str(self.connection.protocol_name())
                self.state_machine.transition_to(ConnectionState.ADAPTER_CONNECTED, "Conexión serie OK")
                self.state_machine.transition_to(ConnectionState.INITIALIZING_PROTOCOL, "Protocolo verificado")
                self.state_machine.transition_to(ConnectionState.VEHICLE_CONNECTED, "ECU respondiendo")
                return True
            elif self.connection.status() == obd.OBDStatus.OBD_CONNECTED:
                self._close_connection()
                self.state_machine.transition_to(ConnectionState.VEHICLE_NOT_RESPONDING, "ECU no responde")
                return False
            else:
                self._close_connection()
                self.state_machine.transition_to(ConnectionState.ERROR, "Error de estado OBD")
                return False
        except Exception as e:
            logger.error(f"Error conectando al adaptador OBD en {target_port}: {e}")
            self._close_connection()
            self.state_machine.transition_to(ConnectionState.ERROR, str(e))
            return False

    def disconnect(self):
        """Desconecta limpiamente el puerto COM."""
        self._close_connection()
        self.active_port = None
        self.protocol_name = None
        self.latency_ms = 0.0
        self.state_machine.transition_to(ConnectionState.DISCONNECTED, "Desconexión manual")

    def _close_connection(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                logger.error(f"Error cerrando conexión OBD: {e}")
            self.connection = None

    def get_status(self) -> Dict[str, Any]:
        return {
            "state": self.state_machine.state.value,
            "port": self.active_port,
            "protocol": self.protocol_name,
            "latency_ms": round(self.latency_ms, 2),
            "is_connected": self.state_machine.state in [ConnectionState.VEHICLE_CONNECTED, ConnectionState.READY, ConnectionState.CAPTURING]
        }
