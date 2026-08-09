"""
Gestión de Líneas Base Aprendidas por Vehículo (VEHICLE_BASELINE).
Calcula los percentiles (P10, P50, P90) y desviaciones históricas a partir de sesiones anteriores del propio coche.
Categoría de Confianza: VEHICLE_BASELINE
"""
from typing import Dict, Any, Optional
import polars as pl

class VehicleBaselineManager:
    @staticmethod
    def calculate_learned_baseline(df_session: pl.DataFrame) -> Dict[str, Any]:
        """Calcula los percentiles P10, P50, P90 y medias para cada PID de una sesión."""
        if df_session is None or df_session.is_empty():
            return {"confidence_tier": "UNVERIFIED", "signals": {}}

        numeric_cols = [c for c, dtype in zip(df_session.columns, df_session.dtypes) if dtype in (pl.Float64, pl.Float32, pl.Int64, pl.Int32)]
        learned_signals = {}

        for col in numeric_cols:
            if col in ("timestamp_ms", "elapsed_sec"):
                continue
            series = df_session[col].drop_nulls()
            if len(series) < 5:
                continue

            learned_signals[col] = {
                "parameter": col,
                "p10": float(series.quantile(0.10)),
                "p50_median": float(series.median()),
                "p90": float(series.quantile(0.90)),
                "mean": float(series.mean()),
                "std": float(series.std()),
                "min": float(series.min()),
                "max": float(series.max()),
                "sample_count": len(series),
                "confidence": "VEHICLE_BASELINE"
            }

        return {
            "confidence_tier": "VEHICLE_BASELINE",
            "description": "Línea base aprendida mediante percentiles históricos del propio vehículo.",
            "signals": learned_signals
        }
