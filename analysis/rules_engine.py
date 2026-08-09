"""
Motor de reglas diagnósticas deterministas para 'Mi Coche por Dentro'.
Carga reglas externas definidas en YAML conforme a la Sección 22 de la especificación maestra.
"""
import os
import logging
import polars as pl
from typing import List, Dict, Any, Optional
from app_paths import resource_path
from analysis.operating_windows import idle_rpm_series

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)

DEFAULT_RULES_PATH = str(resource_path("rules/diagnostic_rules.yaml"))

class RuleEngine:
    def __init__(self, rules_path: str = DEFAULT_RULES_PATH, version: str = "1.0.0"):
        self.version = version
        self.rules_path = rules_path
        self.rules = self.load_rules()

    def load_rules(self) -> List[Dict[str, Any]]:
        """Carga el conjunto de reglas desde el archivo YAML externo."""
        if os.path.exists(self.rules_path) and yaml is not None:
            try:
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, list):
                        return data
            except Exception as e:
                logger.error(f"Error cargando reglas YAML: {e}")
        return []

    def evaluate_session(self, df: pl.DataFrame, dtcs: Optional[List[Dict[str, Any]]] = None, powertrain_type: str = "gasoline") -> List[Dict[str, Any]]:
        """Evalúa las reglas deterministas sobre el DataFrame de telemetría de la sesión."""
        findings = []

        if df is None or df.is_empty():
            return findings

        # Failed OBD queries are intentionally stored as null so the application
        # never invents telemetry. Ignore those rows in diagnostic calculations.
        required_columns = {"pid", "value", "timestamp_monotonic"}
        if not required_columns.issubset(df.columns):
            logger.warning("Session is missing required telemetry columns.")
            return findings

        df = df.filter(
            pl.col("pid").is_not_null()
            & pl.col("value").is_not_null()
            & pl.col("value").is_finite()
            & pl.col("timestamp_monotonic").is_not_null()
            & pl.col("timestamp_monotonic").is_finite()
        )
        if df.is_empty():
            return findings

        # En vehículos 100% eléctricos (BEV / Tesla), omitir reglas de combustión de motor térmico
        if powertrain_type and powertrain_type.lower() in ["bev", "ev", "electric"]:
            logger.info("Vehículo 100% eléctrico (BEV) detectado. Omitiendo evaluación de reglas térmicas ICE.")
            return findings

        pids_available = set(df["pid"].unique().to_list())


        # Regla 1: Calentamiento defectuoso del termostato
        if "COOLANT_TEMP" in pids_available:
            coolant_df = df.filter(pl.col("pid") == "COOLANT_TEMP").sort("timestamp_monotonic")
            min_temp = float(coolant_df["value"].min())
            max_temp = float(coolant_df["value"].max())
            duration_min = float(coolant_df["timestamp_monotonic"].max() - coolant_df["timestamp_monotonic"].min()) / 60.0

            if duration_min > 10.0 and max_temp < 70.0:
                findings.append({
                    "rule_id": "coolant_low_stable_temperature",
                    "finding_type": "COOLING_SYSTEM_ANOMALY",
                    "severity": "warning",
                    "confidence": 0.85,
                    "evidence": {
                        "min_temp_c": round(min_temp, 1),
                        "max_temp_c": round(max_temp, 1),
                        "duration_min": round(duration_min, 1)
                    },
                    "message": "La temperatura del refrigerante se mantuvo por debajo de 70°C tras más de 10 minutos de circulación. Posible termostato abierto o defectuoso."
                })

        # Regla 2: Inestabilidad de ralentí
        if "RPM" in pids_available and "SPEED" in pids_available:
            idle_rpms = idle_rpm_series(df)
            if len(idle_rpms) > 10:
                rpm_std = float(idle_rpms.std())
                rpm_mean = float(idle_rpms.mean())
                if rpm_std > 80.0:
                    findings.append({
                        "rule_id": "idle_instability",
                        "finding_type": "IDLE_STABILITY_ANOMALY",
                        "severity": "warning",
                        "confidence": 0.90,
                        "evidence": {
                            "rpm_mean": round(rpm_mean, 1),
                            "rpm_std": round(rpm_std, 1)
                        },
                        "message": f"Inestabilidad de ralentí detectada (desviación estándar de RPM: {round(rpm_std, 1)} rpm)."
                    })

        # Regla 3: Desviación de Fuel Trims
        if "LONG_FUEL_TRIM_1" in pids_available:
            ltft_df = df.filter(pl.col("pid") == "LONG_FUEL_TRIM_1")
            mean_ltft = float(ltft_df["value"].mean())
            if mean_ltft > 12.0:
                findings.append({
                    "rule_id": "fuel_trim_lean",
                    "finding_type": "FUEL_TRIM_ANOMALY",
                    "severity": "warning",
                    "confidence": 0.88,
                    "evidence": {"mean_ltft_percent": round(mean_ltft, 1)},
                    "message": f"Ajuste de combustible a largo plazo elevadamente positivo (+{round(mean_ltft, 1)}%). Indica compensación por mezcla pobre."
                })

        return findings
