"""
Cálculos estadísticos y matemáticos deterministas de telemetría OBD-II.
Procesa DataFrames de Polars para obtener min, max, media, desviación estándar, derivadas y valores congelados.
"""
import polars as pl
import numpy as np
from typing import Dict, Any

class SignalStatistics:
    @staticmethod
    def analyze_signal(df: pl.DataFrame, pid_name: str) -> Dict[str, Any]:
        """Calcula estadísticas descriptivas y anomalías básicas para una señal específica."""
        sig_df = df.filter(pl.col("pid") == pid_name).sort("timestamp_monotonic")

        raw_count = sig_df.height
        if sig_df.is_empty() or not {"value", "timestamp_monotonic"}.issubset(sig_df.columns):
            return {"pid": pid_name, "count": 0, "invalid_count": raw_count, "has_data": False}

        sig_df = sig_df.filter(
            pl.col("value").is_not_null()
            & pl.col("value").is_finite()
            & pl.col("timestamp_monotonic").is_not_null()
            & pl.col("timestamp_monotonic").is_finite()
        )
        if sig_df.is_empty():
            return {"pid": pid_name, "count": 0, "invalid_count": raw_count, "has_data": False}

        values = sig_df["value"].to_numpy()
        timestamps = sig_df["timestamp_monotonic"].to_numpy()
        unit = ""
        if "unit" in sig_df.columns:
            units = [
                str(value)
                for value in sig_df["unit"].drop_nulls().unique().to_list()
                if str(value).strip()
            ]
            unit = units[0] if units else ""
        
        count = len(values)
        min_val = float(np.min(values))
        max_val = float(np.max(values))
        mean_val = float(np.mean(values))
        std_val = float(np.std(values))
        median_val = float(np.median(values))

        # Derivada (velocidad de cambio: Δv / Δt)
        if count > 1:
            dt = np.diff(timestamps)
            dt[dt == 0] = 0.001 # evitar división por cero
            dv = np.diff(values)
            derivatives = dv / dt
            max_derivative = float(np.max(np.abs(derivatives)))
        else:
            max_derivative = 0.0

        # Detección de valores congelados (mismo valor durante más de N muestras consecutivo)
        frozen_detected = False
        if count >= 10:
            diffs = np.diff(values)
            zero_diff_runs = np.sum(diffs == 0)
            if zero_diff_runs > count * 0.9: # más del 90% inalterado
                frozen_detected = True

        return {
            "pid": pid_name,
            "count": count,
            "invalid_count": raw_count - count,
            "has_data": True,
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "mean": round(mean_val, 2),
            "std": round(std_val, 2),
            "median": round(median_val, 2),
            "max_rate_of_change": round(max_derivative, 2),
            "frozen_detected": frozen_detected,
            "unit": unit,
        }

    @staticmethod
    def analyze_full_session(df: pl.DataFrame) -> Dict[str, Any]:
        """Analiza todas las señales presentes en el DataFrame de la sesión."""
        if df is None or df.is_empty():
            return {"session_stats": {}, "total_samples": 0}

        if "pid" not in df.columns:
            return {"session_stats": {}, "total_samples": len(df)}

        unique_pids = df["pid"].drop_nulls().unique().to_list()
        stats_by_pid = {}

        for pid in unique_pids:
            stats_by_pid[pid] = SignalStatistics.analyze_signal(df, pid)

        valid_samples = sum(signal["count"] for signal in stats_by_pid.values())
        valid_timestamps = (
            df.filter(
                pl.col("timestamp_monotonic").is_not_null()
                & pl.col("timestamp_monotonic").is_finite()
            )["timestamp_monotonic"]
            if "timestamp_monotonic" in df.columns
            else None
        )
        duration_sec = (
            round(float(valid_timestamps.max() - valid_timestamps.min()), 2)
            if valid_timestamps is not None and len(valid_timestamps) > 0
            else 0.0
        )

        return {
            "total_samples": len(df),
            "valid_samples": valid_samples,
            "invalid_samples": len(df) - valid_samples,
            "duration_sec": duration_sec,
            "signals": stats_by_pid
        }
