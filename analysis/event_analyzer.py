"""
Analizador de ventanas temporales alrededor de marcadores de eventos.
Extrae ±10 segundos respecto a un evento (ej. tirón) y detecta qué señal cambió primero.
"""
import polars as pl
from typing import Dict, Any

class EventWindowAnalyzer:
    def __init__(self, window_before_sec: float = 10.0, window_after_sec: float = 10.0):
        self.window_before = window_before_sec
        self.window_after = window_after_sec

    def extract_event_window(self, df: pl.DataFrame, event_offset_ms: float) -> pl.DataFrame:
        """Filtra los datos de telemetría en la ventana alrededor del marcador del evento."""
        if df is None or df.is_empty():
            return pl.DataFrame()

        event_sec = event_offset_ms / 1000.0
        start_sec = max(0.0, event_sec - self.window_before)
        end_sec = event_sec + self.window_after

        return df.filter(
            (pl.col("timestamp_monotonic") >= start_sec) &
            (pl.col("timestamp_monotonic") <= end_sec)
        )

    def analyze_event_impact(self, df: pl.DataFrame, event_offset_ms: float) -> Dict[str, Any]:
        """Calcula el impacto del evento en cada señal registrada."""
        window_df = self.extract_event_window(df, event_offset_ms)
        if window_df.is_empty():
            return {"event_offset_ms": event_offset_ms, "found": False}

        event_sec = event_offset_ms / 1000.0
        pids = window_df["pid"].unique().to_list()
        signal_changes = {}

        for pid in pids:
            pid_df = window_df.filter(pl.col("pid") == pid).sort("timestamp_monotonic")
            if pid_df.height < 3:
                continue

            before_df = pid_df.filter(pl.col("timestamp_monotonic") < event_sec)
            after_df = pid_df.filter(pl.col("timestamp_monotonic") >= event_sec)

            if before_df.is_empty() or after_df.is_empty():
                continue

            mean_before = float(before_df["value"].mean())
            mean_after = float(after_df["value"].mean())
            std_before = float(before_df["value"].std()) or 0.001
            delta = mean_after - mean_before
            z_score = abs(delta) / std_before

            signal_changes[pid] = {
                "mean_before": round(mean_before, 2),
                "mean_after": round(mean_after, 2),
                "delta": round(delta, 2),
                "z_score": round(z_score, 2),
                "significant_change": z_score > 2.0
            }

        return {
            "event_offset_ms": event_offset_ms,
            "window_sec": [event_sec - self.window_before, event_sec + self.window_after],
            "found": True,
            "signal_impacts": signal_changes
        }
