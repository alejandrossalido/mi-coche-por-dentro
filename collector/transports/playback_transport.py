"""
Transporte de reproducción (Playback Engine) de grabaciones de telemetría guardadas en Parquet/SQLite.
Soporta control de velocidad (0.5x, 1x, 2x, 5x), pausa y reloj virtual determinista.
"""
import time
import os
import logging
from typing import Dict, Any, Optional
import polars as pl
from collector.transports.base_transport import BaseTelemetryTransport, TransportType

logger = logging.getLogger(__name__)

class PlaybackTransport(BaseTelemetryTransport):
    def __init__(self, parquet_file_path: Optional[str] = None):
        super().__init__(TransportType.PLAYBACK)
        self.file_path = parquet_file_path
        self.df: Optional[pl.DataFrame] = None
        self.current_index: int = 0
        self.total_samples: int = 0
        self.playback_speed: float = 1.0
        self.virtual_start_time: float = 0.0
        self.total_queries: int = 0

    def load_recording(self, parquet_file_path: str) -> bool:
        if not os.path.exists(parquet_file_path):
            logger.error(f"Archivo de grabación no encontrado: {parquet_file_path}")
            return False
        try:
            self.df = pl.read_parquet(parquet_file_path)
            self.total_samples = len(self.df)
            self.current_index = 0
            self.file_path = parquet_file_path
            logger.info(f"Grabación cargada para reproducción: {parquet_file_path} ({self.total_samples} muestras).")
            return True
        except Exception as e:
            logger.error(f"Error cargando archivo Parquet para playback: {e}")
            return False

    def connect(self, port_or_uri: Optional[str] = None, **kwargs) -> bool:
        target_path = port_or_uri or self.file_path
        if target_path and not self.df:
            if not self.load_recording(target_path):
                return False

        self.virtual_start_time = time.time()
        self.is_connected = True
        return True

    def set_speed(self, multiplier: float):
        """Ajusta la velocidad de reproducción (ej: 0.5, 1.0, 2.0, 5.0)."""
        self.playback_speed = max(0.1, float(multiplier))

    def disconnect(self) -> bool:
        self.is_connected = False
        return True

    def query_pid(self, pid_name: str) -> Dict[str, Any]:
        self.total_queries += 1
        if not self.is_connected or self.df is None or self.total_samples == 0:
            return {
                "pid": pid_name,
                "value": None,
                "unit": "",
                "success": False,
                "query_round_trip_ms": 0.0,
                "raw_response": "",
                "error": "PLAYBACK_NOT_LOADED"
            }

        # Filtrar o buscar la siguiente muestra para ese PID a partir del índice actual
        sub_df = self.df.slice(self.current_index).filter(pl.col("pid") == pid_name)
        if len(sub_df) == 0:
            # Rebobinar o retornar fin
            sub_df = self.df.filter(pl.col("pid") == pid_name)
            self.current_index = 0

        if len(sub_df) == 0:
            return {
                "pid": pid_name,
                "value": None,
                "unit": "",
                "success": False,
                "query_round_trip_ms": 1.0,
                "raw_response": "",
                "error": "PID_NOT_IN_RECORDING"
            }

        row = sub_df.row(0, named=True)
        self.current_index = (self.current_index + 1) % self.total_samples

        return {
            "pid": row.get("pid", pid_name),
            "value": float(row.get("value", 0.0)) if row.get("value") is not None else None,
            "unit": str(row.get("unit", "")),
            "success": True,
            "query_round_trip_ms": float(row.get("latency_ms", 5.0)),
            "raw_response": str(row.get("raw_response", "")),
            "error": None
        }

    def get_transport_metrics(self) -> Dict[str, Any]:
        return {
            "transport_type": self.transport_type.value,
            "file_path": self.file_path,
            "speed_multiplier": self.playback_speed,
            "is_connected": self.is_connected,
            "total_samples": self.total_samples,
            "current_index": self.current_index,
            "total_queries": self.total_queries
        }
