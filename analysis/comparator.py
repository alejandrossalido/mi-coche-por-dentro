"""
Módulo de comparación de sesiones de telemetría (Session A vs Session B).
Calcula variaciones porcentuales, deltas y mejoras de rendimiento/estabilidad entre dos pruebas.
"""
import polars as pl
from typing import Dict, Any
from analysis.statistics import SignalStatistics

class SessionComparator:
    @staticmethod
    def compare_sessions(df_a: pl.DataFrame, df_b: pl.DataFrame,
                         label_a: str = "Sesión A (Antes)",
                         label_b: str = "Sesión B (Después)") -> Dict[str, Any]:
        """Compara dos DataFrames de telemetría y genera el informe delta."""
        if df_a is None or df_a.is_empty() or df_b is None or df_b.is_empty():
            return {"error": "Se requieren datos válidos en ambas sesiones para realizar la comparación."}

        stats_a = SignalStatistics.analyze_full_session(df_a)
        stats_b = SignalStatistics.analyze_full_session(df_b)

        signals_a = stats_a.get("signals", {})
        signals_b = stats_b.get("signals", {})

        common_pids = set(signals_a.keys()).intersection(set(signals_b.keys()))
        comparison_results = {}

        for pid in common_pids:
            s_a = signals_a[pid]
            s_b = signals_b[pid]

            if not s_a.get("has_data") or not s_b.get("has_data"):
                continue

            mean_a = s_a.get("mean", 0.0)
            mean_b = s_b.get("mean", 0.0)
            std_a = s_a.get("std", 0.0)
            std_b = s_b.get("std", 0.0)

            delta_mean = mean_b - mean_a
            pct_change_mean = ((delta_mean / mean_a) * 100.0) if mean_a != 0 else 0.0

            delta_std = std_b - std_a
            pct_change_std = ((delta_std / std_a) * 100.0) if std_a != 0 else 0.0

            comparison_results[pid] = {
                "session_a": {"mean": mean_a, "std": std_a, "min": s_a.get("min"), "max": s_a.get("max")},
                "session_b": {"mean": mean_b, "std": std_b, "min": s_b.get("min"), "max": s_b.get("max")},
                "delta_mean": round(delta_mean, 2),
                "pct_change_mean": round(pct_change_mean, 2),
                "delta_std": round(delta_std, 2),
                "pct_change_std": round(pct_change_std, 2),
                "stability_improved": std_b < std_a
            }

        improved = sum(1 for item in comparison_results.values() if item["stability_improved"])
        worsened = len(comparison_results) - improved
        if not comparison_results:
            verdict = "invalid"
            summary = "No hay señales válidas comunes para comparar."
        elif improved > worsened:
            verdict = "improved"
            summary = f"La estabilidad mejoró en {improved} de {len(comparison_results)} señales comparables."
        elif worsened > improved:
            verdict = "worsened"
            summary = f"La variabilidad aumentó en {worsened} de {len(comparison_results)} señales comparables."
        else:
            verdict = "mixed"
            summary = "El resultado es mixto; no hay una mejora global concluyente."

        return {
            "label_a": label_a,
            "label_b": label_b,
            "duration_a_sec": stats_a.get("duration_sec"),
            "duration_b_sec": stats_b.get("duration_sec"),
            "signals_compared": comparison_results,
            "conclusion": {
                "verdict": verdict,
                "summary": summary,
                "improved_signals": improved,
                "worsened_signals": worsened,
            },
        }
