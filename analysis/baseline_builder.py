"""
Constructor de Líneas Base del Vehículo (Vehicle Baselines).
Construye patrones esperados de comportamiento dinámico por contexto a partir de sesiones sanas aprobadas.
"""
from typing import Dict, Any, List, Optional
import polars as pl

class VehicleBaselineBuilder:
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id

    def build_baseline(self, healthy_session_dfs: List[pl.DataFrame], context_name: str = "idle_warm", min_samples: int = 3) -> Dict[str, Any]:
        """
        Calcula percentiles (p10, p50, p90), medias y variabilidad de señales a partir de sesiones declaradas sanas.
        """
        if not healthy_session_dfs:
            return {
                "vehicle_id": self.vehicle_id,
                "context": context_name,
                "status": "NO_DATA",
                "sample_sessions_count": 0,
                "signals": {}
            }

        # Combinar dataframes de sesiones sanas
        combined_df = pl.concat(healthy_session_dfs)
        if len(combined_df) == 0:
            return {
                "vehicle_id": self.vehicle_id,
                "context": context_name,
                "status": "EMPTY",
                "sample_sessions_count": len(healthy_session_dfs),
                "signals": {}
            }

        signal_baselines = {}
        unique_pids = combined_df.select(pl.col("pid").unique()).to_series().to_list()

        for pid_name in unique_pids:
            pid_df = combined_df.filter((pl.col("pid") == pid_name) & pl.col("value").is_not_null())
            if len(pid_df) < min_samples:
                continue


            stats = pid_df.select([
                pl.col("value").mean().alias("mean"),
                pl.col("value").median().alias("p50"),
                pl.col("value").quantile(0.10).alias("p10"),
                pl.col("value").quantile(0.90).alias("p90"),
                pl.col("value").std().alias("std")
            ]).to_dicts()[0]

            signal_baselines[pid_name] = {
                "mean": round(float(stats["mean"]), 2) if stats["mean"] is not None else 0.0,
                "p50": round(float(stats["p50"]), 2) if stats["p50"] is not None else 0.0,
                "p10": round(float(stats["p10"]), 2) if stats["p10"] is not None else 0.0,
                "p90": round(float(stats["p90"]), 2) if stats["p90"] is not None else 0.0,
                "std": round(float(stats["std"]), 2) if stats["std"] is not None else 0.0,
            }

        return {
            "vehicle_id": self.vehicle_id,
            "context": context_name,
            "status": "VALID",
            "sample_sessions_count": len(healthy_session_dfs),
            "signals": signal_baselines
        }

    def evaluate_deviation(self, current_sample: Dict[str, Any], baseline: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Compara una muestra actual con la línea base del vehículo para detectar desviaciones significativas.
        """
        pid = current_sample.get("pid")
        val = current_sample.get("value")
        if not pid or val is None or "signals" not in baseline or pid not in baseline["signals"]:
            return None

        b = baseline["signals"][pid]
        p10 = b["p10"]
        p90 = b["p90"]
        p50 = b["p50"]

        if val < p10:
            pct_diff = round(((val - p50) / p50) * 100.0, 1) if p50 != 0 else 0.0
            return {
                "pid": pid,
                "status": "BELOW_BASELINE",
                "value": val,
                "baseline_p50": p50,
                "baseline_p10": p10,
                "deviation_percent": pct_diff
            }
        elif val > p90:
            pct_diff = round(((val - p50) / p50) * 100.0, 1) if p50 != 0 else 0.0
            return {
                "pid": pid,
                "status": "ABOVE_BASELINE",
                "value": val,
                "baseline_p50": p50,
                "baseline_p90": p90,
                "deviation_percent": pct_diff
            }

        return None
