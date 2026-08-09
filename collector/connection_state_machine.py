"""
Máquina de estados explícita de conexión y ciclo de vida de la adquisición OBD-II.
Gestiona transiciones seguras con timeouts, logging estructurado y callbacks de eventos.
"""
import enum
import time
import logging
from typing import List, Callable, Dict, Any

logger = logging.getLogger(__name__)

class ConnectionState(str, enum.Enum):
    DISCONNECTED = "DISCONNECTED"
    DISCOVERING_ADAPTER = "DISCOVERING_ADAPTER"
    ADAPTER_FOUND = "ADAPTER_FOUND"
    CONNECTING_ADAPTER = "CONNECTING_ADAPTER"
    ADAPTER_CONNECTED = "ADAPTER_CONNECTED"
    INITIALIZING_PROTOCOL = "INITIALIZING_PROTOCOL"
    VEHICLE_NOT_RESPONDING = "VEHICLE_NOT_RESPONDING"
    VEHICLE_CONNECTED = "VEHICLE_CONNECTED"
    CAPABILITY_DISCOVERY = "CAPABILITY_DISCOVERY"
    READY = "READY"
    CAPTURING = "CAPTURING"
    CONNECTION_DEGRADED = "CONNECTION_DEGRADED"
    CONNECTION_LOST = "CONNECTION_DEGRADED"
    ADAPTER_NOT_FOUND = "DISCONNECTED"
    RECONNECTING = "RECONNECTING"
    ERROR = "ERROR"


ALLOWED_TRANSITIONS: Dict[ConnectionState, set] = {
    ConnectionState.DISCONNECTED: {ConnectionState.DISCOVERING_ADAPTER, ConnectionState.CONNECTION_DEGRADED, ConnectionState.ERROR},

    ConnectionState.DISCOVERING_ADAPTER: {ConnectionState.ADAPTER_FOUND, ConnectionState.DISCONNECTED, ConnectionState.ERROR},
    ConnectionState.ADAPTER_FOUND: {ConnectionState.CONNECTING_ADAPTER, ConnectionState.DISCONNECTED, ConnectionState.ERROR},
    ConnectionState.CONNECTING_ADAPTER: {ConnectionState.ADAPTER_CONNECTED, ConnectionState.DISCONNECTED, ConnectionState.ERROR},
    ConnectionState.ADAPTER_CONNECTED: {ConnectionState.INITIALIZING_PROTOCOL, ConnectionState.DISCONNECTED, ConnectionState.ERROR},
    ConnectionState.INITIALIZING_PROTOCOL: {ConnectionState.VEHICLE_CONNECTED, ConnectionState.VEHICLE_NOT_RESPONDING, ConnectionState.ERROR},
    ConnectionState.VEHICLE_NOT_RESPONDING: {ConnectionState.VEHICLE_CONNECTED, ConnectionState.RECONNECTING, ConnectionState.DISCONNECTED, ConnectionState.ERROR},

    ConnectionState.VEHICLE_CONNECTED: {ConnectionState.CAPABILITY_DISCOVERY, ConnectionState.CAPTURING, ConnectionState.DISCONNECTED, ConnectionState.CONNECTION_DEGRADED},
    ConnectionState.CAPABILITY_DISCOVERY: {ConnectionState.READY, ConnectionState.ERROR, ConnectionState.DISCONNECTED},
    ConnectionState.READY: {ConnectionState.CAPTURING, ConnectionState.DISCONNECTED},
    ConnectionState.CAPTURING: {ConnectionState.READY, ConnectionState.VEHICLE_CONNECTED, ConnectionState.CONNECTION_DEGRADED, ConnectionState.ERROR, ConnectionState.DISCONNECTED},
    ConnectionState.CONNECTION_DEGRADED: {ConnectionState.RECONNECTING, ConnectionState.VEHICLE_NOT_RESPONDING, ConnectionState.ERROR, ConnectionState.DISCONNECTED},

    ConnectionState.RECONNECTING: {ConnectionState.VEHICLE_CONNECTED, ConnectionState.ERROR, ConnectionState.DISCONNECTED},
    ConnectionState.ERROR: {ConnectionState.DISCONNECTED, ConnectionState.RECONNECTING}
}

class ConnectionStateMachine:
    def __init__(self):
        self.state: ConnectionState = ConnectionState.DISCONNECTED
        self.state_entry_time: float = time.time()
        self._callbacks: List[Callable[[ConnectionState, ConnectionState], None]] = []
        self.history: List[Dict[str, Any]] = []

    def register_callback(self, callback: Callable[[ConnectionState, ConnectionState], None]):
        self._callbacks.append(callback)

    def transition_to(self, new_state: ConnectionState, reason: str = "") -> bool:
        if self.state == new_state:
            return True

        # Validar si la transición está en la mapa de saltos legales
        allowed = ALLOWED_TRANSITIONS.get(self.state, set())
        if new_state not in allowed:
            logger.warning(f"Transición ilegal rechazada: {self.state.value} -> {new_state.value} (Razon: '{reason}')")
            return False

        old_state = self.state
        now = time.time()
        duration_in_old_state = now - self.state_entry_time


        logger.info(f"State transition: {old_state.value} -> {new_state.value} (Razon: '{reason}', Estuvo en {old_state.value}: {duration_in_old_state:.2f}s)")

        self.state = new_state
        self.state_entry_time = now

        entry = {
            "from_state": old_state.value,
            "to_state": new_state.value,
            "timestamp": now,
            "reason": reason,
            "duration_sec": round(duration_in_old_state, 2)
        }
        self.history.append(entry)
        if len(self.history) > 100:
            self.history.pop(0)

        for cb in self._callbacks:
            try:
                cb(old_state, new_state)
            except Exception as e:
                logger.error(f"Error en callback de maquina de estados: {e}")

        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "current_state": self.state.value,
            "state_duration_sec": round(time.time() - self.state_entry_time, 2),
            "history_count": len(self.history),
            "is_connected": self.state in [ConnectionState.VEHICLE_CONNECTED, ConnectionState.READY, ConnectionState.CAPTURING],
            "is_capturing": self.state == ConnectionState.CAPTURING
        }
