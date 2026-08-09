"""
Calculador de Puntuación de Calidad de Sesión de Telemetría (Session Quality Score: 0-100).
Evalúa subpuntuaciones de estabilidad serie, integridad de marcas temporales y completitud de señales.
"""
from typing import Dict, Any, Optional
import polars as pl

class SessionQualityCalculator:
    def __init__(self):
        pass

    def calculate_quality(self, df: Optional[pl.DataFrame], transport_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calcula la calidad técnica global y subpuntuaciones de la sesión.
        """
        if df is None or len(df) == 0:
            return {
                "overall_score": 0.0,
                "connection_quality": 0.0,
                "timing_quality": 0.0,
                "signal_completeness": 0.0,
                "analysis_suitability": {
                    "warmup_analysis": False,
                    "idle_analysis": False,
                    "transient_jerk_analysis": False,
                    "dtc_context_analysis": False
                },
                "warnings": ["No hay muestras registradas en la sesión."]
            }

        total_samples = len(df)

        # 1. Calidad de Conexión (basado en el transporte y nulos)
        null_count = df.select(pl.col("value").is_null().sum()).item()
        valid_sample_ratio = (total_samples - null_count) / total_samples if total_samples > 0 else 0.0

        if valid_sample_ratio == 0:
            return {
                "overall_score": 0.0,
                "connection_quality": 0.0,
                "timing_quality": 0.0,
                "signal_completeness": 0.0,
                "total_samples": total_samples,
                "valid_samples": 0,
                "unique_pids_count": 0,
                "analysis_suitability": {
                    "warmup_analysis": False,
                    "idle_analysis": False,
                    "transient_jerk_analysis": False,
                    "dtc_context_analysis": False,
                },
                "warnings": [
                    "La ECU no entregó ninguna lectura OBD válida. La sesión no es apta para diagnóstico."
                ],
            }

        if transport_metrics:
            success_rate = float(transport_metrics.get("success_rate", 1.0))
            timeout_rate = float(transport_metrics.get("timeout_rate", 0.0))
            conn_score = round(max(0.0, (success_rate - timeout_rate) * 100.0), 1)
        else:
            conn_score = round(valid_sample_ratio * 100.0, 1)

        # 2. Calidad de Temporización (latencia y jitter)
        avg_latency = df.select(pl.col("latency_ms").mean()).item() or 10.0
        if avg_latency <= 20.0:
            timing_score = 100.0
        elif avg_latency <= 50.0:
            timing_score = 80.0
        elif avg_latency <= 100.0:
            timing_score = 60.0
        else:
            timing_score = 40.0

        # 3. Completitud de Señales
        valid_df = df.filter(pl.col("value").is_not_null() & pl.col("value").is_finite())
        unique_pids = set(valid_df.select(pl.col("pid").unique()).to_series().to_list())
        essential_pids = {"RPM", "SPEED", "ENGINE_LOAD", "COOLANT_TEMP"}
        found_essential = essential_pids.intersection(unique_pids)
        signal_score = round((len(found_essential) / len(essential_pids)) * 100.0, 1)

        # Puntuación global ponderada
        overall_score = round(0.4 * conn_score + 0.3 * timing_score + 0.3 * signal_score, 1)

        has_map = ("INTAKE_PRESSURE" in unique_pids) or ("MAP" in unique_pids)

        # Idoneidad para distintos análisis
        suitability = {
            "warmup_analysis": "COOLANT_TEMP" in unique_pids and total_samples > 50,
            "idle_analysis": "RPM" in unique_pids and overall_score >= 60.0,
            "transient_jerk_analysis": has_map and "MAF" in unique_pids and timing_score >= 80.0,
            "dtc_context_analysis": overall_score >= 50.0
        }

        warnings = []
        if overall_score < 70.0:
            warnings.append("Calidad global de sesión baja (<70). Los análisis transitorios pueden ser imprecisos.")
        if not has_map:
            warnings.append("Falta señal de presión de admisión (MAP/INTAKE_PRESSURE). No se pueden analizar tirones de turbo.")


        return {
            "overall_score": overall_score,
            "connection_quality": conn_score,
            "timing_quality": timing_score,
            "signal_completeness": signal_score,
            "total_samples": total_samples,
            "unique_pids_count": len(unique_pids),
            "analysis_suitability": suitability,
            "warnings": warnings
        }
