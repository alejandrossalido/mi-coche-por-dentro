"""
Módulo de almacenamiento atómico y seguro de telemetría en formato Apache Parquet.
Utiliza escrituras atómicas (.partial único por sesión -> .parquet) y validación estricta de session_id contra Path Traversal.
"""
import os
import uuid
import pyarrow as pa
import pyarrow.parquet as pq
import polars as pl
from typing import List, Dict, Any, Optional
from app_paths import telemetry_path

TELEMETRY_SCHEMA = pa.schema([
    ("session_id", pa.string()),
    ("timestamp_monotonic", pa.float64()),
    ("timestamp_utc", pa.string()),
    ("pid", pa.string()),
    ("value", pa.float64()),
    ("unit", pa.string()),
    ("ecu", pa.string()),
    ("quality", pa.float64()),
    ("latency_ms", pa.float64()),
    ("raw_response", pa.string()),
    ("data_source", pa.string()),
])

class CorruptSessionFile(Exception):
    """Excepción lanzada cuando el archivo Parquet de una sesión existente está corrompido."""
    pass

class TelemetryStore:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = str(telemetry_path())
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def validate_session_id(self, session_id: str) -> str:
        r"""Valida session_id y previene vulnerabilidades de Path Traversal (..\..)."""
        safe_id = os.path.basename(str(session_id)).strip()

        if not safe_id or ".." in session_id or "/" in session_id or "\\" in session_id:
            # Intentar parsear como UUID si es posible
            try:
                safe_id = str(uuid.UUID(session_id))
            except ValueError:
                raise ValueError(f"Identificador de sesión inválido o con intento de Path Traversal: {session_id}")

        resolved_path = os.path.abspath(os.path.join(self.base_dir, f"session_{safe_id}.parquet"))
        if not resolved_path.startswith(self.base_dir):
            raise ValueError(f"Intento de escape de directorio base detectado: {session_id}")
        return safe_id

    def get_session_file_path(self, session_id: str) -> str:
        safe_id = self.validate_session_id(session_id)
        return os.path.join(self.base_dir, f"session_{safe_id}.parquet")

    def save_samples(self, session_id: str, samples: List[Dict[str, Any]]) -> str:
        """
        Escribe de forma atómica las muestras a un archivo Parquet.
        Utiliza un nombre temporal único por UUID y realiza validación antes de publicar.
        """
        if not samples:
            return self.get_session_file_path(session_id)

        final_path = self.get_session_file_path(session_id)
        temp_path = f"{final_path}.{uuid.uuid4().hex}.partial"

        table_data = {
            "session_id": [s.get("session_id", session_id) for s in samples],
            "timestamp_monotonic": [float(s.get("timestamp_monotonic", 0.0)) for s in samples],
            "timestamp_utc": [str(s.get("timestamp_utc", "")) for s in samples],
            "pid": [str(s.get("pid", "")) for s in samples],
            "value": [float(s.get("value", 0.0)) if s.get("value") is not None else None for s in samples],
            "unit": [str(s.get("unit", "")) for s in samples],
            "ecu": [str(s.get("ecu", "ENGINE")) for s in samples],
            "quality": [float(s.get("quality", 1.0)) for s in samples],
            "latency_ms": [float(s.get("latency_ms", 0.0)) for s in samples],
            "raw_response": [str(s.get("raw_response", "")) for s in samples],
            "data_source": [str(s.get("data_source", "measured")) for s in samples],
        }

        new_table = pa.Table.from_pydict(table_data, schema=TELEMETRY_SCHEMA)

        if os.path.exists(final_path):
            try:
                existing_table = pq.read_table(final_path)
                combined_table = pa.concat_tables([existing_table, new_table])
            except Exception as exc:
                raise CorruptSessionFile(f"El archivo Parquet {final_path} está corrupto y no se sobreescribirá silenciosamente.") from exc
        else:
            combined_table = new_table

        # Escribir primero en el archivo temporal único .partial
        pq.write_table(combined_table, temp_path, compression="snappy")

        # Validar metadata del temporal antes de reemplazar
        try:
            pq.read_metadata(temp_path)
        except Exception as exc:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise ValueError(f"Fallo en la validación de integridad del archivo Parquet temporal: {exc}")

        # Renombrar atómicamente temp_path a final_path
        os.replace(temp_path, final_path)

        return final_path

    def load_session_dataframe(self, session_id: str) -> Optional[pl.DataFrame]:
        """Carga los datos de una sesión usando lectura diferida de Polars."""
        file_path = self.get_session_file_path(session_id)
        if not os.path.exists(file_path):
            return None
        return pl.read_parquet(file_path)
