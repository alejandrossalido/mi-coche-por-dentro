"""
Gestor del adaptador OBD (vLinker / OBDLink / Puerto COM).
Utiliza ConnectionStateMachine como única fuente de verdad para el ciclo de vida de la conexión.
"""
import logging
import os
import re
import threading
import time
from typing import Optional, List, Dict, Any, Callable
import serial.tools.list_ports
from collector.connection_state_machine import ConnectionStateMachine, ConnectionState

try:
    import obd
except ImportError:
    obd = None

logger = logging.getLogger(__name__)

COM_PORT_PATTERN = re.compile(r"^COM[1-9][0-9]{0,2}$", re.IGNORECASE)
FALLBACK_BAUDRATES = (115200, 38400)

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
        self.active_baudrate: Optional[int] = None
        self.fast_mode: Optional[bool] = None
        self.last_error: Optional[str] = None
        self.connection_attempts: List[Dict[str, Any]] = []
        self._connection_lock = threading.Lock()
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
        if not self._connection_lock.acquire(blocking=False):
            self.last_error = "Ya hay un intento de conexión OBD en curso."
            return False
        try:
            if self.state != ConnectionState.DISCONNECTED or self.connection is not None:
                self._disconnect_unlocked("Preparando un nuevo intento de conexión")
            self.last_error = None
            self.connection_attempts = []
            self.state_machine.transition_to(ConnectionState.DISCOVERING_ADAPTER, "Iniciando escaneo de puertos")
            target_port = str(com_port or self.preferred_port or "").strip().upper()

            if not target_port:
                available = self.list_available_ports()
                obd_ports = [p["port"] for p in available if p["is_obdlink"] and not p["excluded"]]
                if obd_ports:
                    target_port = str(obd_ports[0]).upper()

            if not target_port:
                self.last_error = "No se encontró ningún puerto OBD compatible."
                self.state_machine.transition_to(ConnectionState.ERROR, self.last_error)
                return False
            if not COM_PORT_PATTERN.fullmatch(target_port):
                self.last_error = "El puerto seleccionado no tiene un nombre COM válido."
                self.state_machine.transition_to(ConnectionState.ERROR, self.last_error)
                return False

            self.state_machine.transition_to(ConnectionState.ADAPTER_FOUND, f"Puerto {target_port} seleccionado")
            self.state_machine.transition_to(ConnectionState.CONNECTING_ADAPTER, "Abriendo puerto serie")

            if obd is None:
                if os.getenv("APP_MODE", "production").strip().lower() in {"demo", "simulated"}:
                    self.active_port = target_port
                    self.state_machine.transition_to(ConnectionState.ADAPTER_CONNECTED, "Conexión simulada OK")
                    self.state_machine.transition_to(ConnectionState.INITIALIZING_PROTOCOL, "Inicializando simulador")
                    self.state_machine.transition_to(ConnectionState.VEHICLE_CONNECTED, "Simulador CAN listo")
                    self.protocol_name = "SIMULATED_CAN_11BIT_500K"
                    return True
                self.last_error = "La dependencia python-OBD no está instalada."
                self.state_machine.transition_to(ConnectionState.ERROR, self.last_error)
                return False

            baudrates = list(dict.fromkeys((int(baudrate), *FALLBACK_BAUDRATES)))
            attempt_plan = list(dict.fromkeys(
                (candidate_baud, candidate_fast)
                for candidate_baud in baudrates
                for candidate_fast in (bool(fast), not bool(fast))
            ))
            adapter_seen = False
            last_exception: Optional[Exception] = None
            for attempt_number, (candidate_baud, candidate_fast) in enumerate(attempt_plan, start=1):
                started = time.monotonic()
                candidate = None
                try:
                    logger.info(
                        "Intento OBD %s/%s en %s (%s bps, fast=%s)",
                        attempt_number,
                        len(attempt_plan),
                        target_port,
                        candidate_baud,
                        candidate_fast,
                    )
                    candidate = obd.OBD(
                        portstr=target_port,
                        baudrate=candidate_baud,
                        fast=candidate_fast,
                    )
                    latency_ms = (time.monotonic() - started) * 1000.0
                    status = candidate.status()
                    adapter_seen = adapter_seen or status == obd.OBDStatus.OBD_CONNECTED
                    self.connection_attempts.append({
                        "baudrate": candidate_baud,
                        "fast": candidate_fast,
                        "status": str(status),
                        "latency_ms": round(latency_ms, 2),
                    })
                    if status == obd.OBDStatus.CAR_CONNECTED:
                        self.connection = candidate
                        self.active_port = target_port
                        self.active_baudrate = candidate_baud
                        self.fast_mode = candidate_fast
                        self.latency_ms = latency_ms
                        self.protocol_name = str(candidate.protocol_name())
                        self.state_machine.transition_to(ConnectionState.ADAPTER_CONNECTED, "Conexión serie OK")
                        self.state_machine.transition_to(ConnectionState.INITIALIZING_PROTOCOL, "Protocolo verificado")
                        self.state_machine.transition_to(ConnectionState.VEHICLE_CONNECTED, "ECU respondiendo")
                        return True
                except Exception as exc:
                    last_exception = exc
                    self.connection_attempts.append({
                        "baudrate": candidate_baud,
                        "fast": candidate_fast,
                        "status": "ERROR",
                        "latency_ms": round((time.monotonic() - started) * 1000.0, 2),
                    })
                    logger.warning(
                        "Fallo OBD en %s (%s bps, fast=%s): %s",
                        target_port,
                        candidate_baud,
                        candidate_fast,
                        exc,
                    )
                finally:
                    if candidate is not None and candidate is not self.connection:
                        try:
                            candidate.close()
                        except Exception:
                            logger.debug("No se pudo cerrar un intento OBD fallido.", exc_info=True)

            self.active_port = None
            self.active_baudrate = None
            self.fast_mode = None
            self.protocol_name = None
            self.latency_ms = 0.0
            if adapter_seen:
                self.last_error = "El adaptador responde, pero la ECU no. Comprueba el contacto del coche."
                self.state_machine.transition_to(ConnectionState.VEHICLE_NOT_RESPONDING, self.last_error)
            else:
                self.last_error = (
                    "No se pudo abrir el adaptador OBD. Comprueba el puerto, el controlador y que otra aplicación no lo esté usando."
                )
                reason = f"{self.last_error} ({last_exception})" if last_exception else self.last_error
                self.state_machine.transition_to(ConnectionState.ERROR, reason)
            return False
        finally:
            self._connection_lock.release()

    def disconnect(self):
        """Desconecta limpiamente el puerto COM."""
        with self._connection_lock:
            self._disconnect_unlocked("Desconexión manual")

    def _disconnect_unlocked(self, reason: str):
        self._close_connection()
        self.active_port = None
        self.active_baudrate = None
        self.fast_mode = None
        self.protocol_name = None
        self.latency_ms = 0.0
        self.state_machine.transition_to(ConnectionState.DISCONNECTED, reason)

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
            "baudrate": self.active_baudrate,
            "fast_mode": self.fast_mode,
            "last_error": self.last_error,
            "attempt_count": len(self.connection_attempts),
            "is_connected": self.state_machine.state in [ConnectionState.VEHICLE_CONNECTED, ConnectionState.READY, ConnectionState.CAPTURING]
        }
