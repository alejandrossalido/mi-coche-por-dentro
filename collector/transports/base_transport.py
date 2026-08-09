"""
Interfaz base abstracta para transportes de telemetría OBD-II (puerto serie real, simulador y reproducción playback).
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import enum

class TransportType(str, enum.Enum):
    SERIAL_ELM_STN = "SERIAL_ELM_STN"
    SIMULATOR = "SIMULATOR"
    PLAYBACK = "PLAYBACK"

class BaseTelemetryTransport(ABC):
    def __init__(self, transport_type: TransportType):
        self.transport_type = transport_type
        self.is_connected: bool = False

    @abstractmethod
    def connect(self, port_or_uri: Optional[str] = None, **kwargs) -> bool:
        """Establece la conexión con la fuente de telemetría."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Cierra la conexión limpiamente."""
        pass

    @abstractmethod
    def query_pid(self, pid_name: str) -> Dict[str, Any]:
        """
        Consulta un PID individual.
        Retorna un diccionario estructurado:
        {
            "pid": str,
            "value": Optional[float],
            "unit": str,
            "success": bool,
            "query_round_trip_ms": float,
            "raw_response": str,
            "error": Optional[str]
        }
        """
        pass

    @abstractmethod
    def get_transport_metrics(self) -> Dict[str, Any]:
        """Retorna las métricas de rendimiento y calidad del transporte."""
        pass
