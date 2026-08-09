"""Deterministic, evidence-backed session health and alert summaries."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import polars as pl

from analysis.operating_windows import idle_rpm_series
from analysis.fuel_consumption import FuelConsumptionAnalyzer
from analysis.trip_metrics import TripMetrics


SYSTEM_SIGNAL_MAP = {
    "engine": {"RPM", "ENGINE_LOAD", "THROTTLE_POS", "RUN_TIME"},
    "cooling": {"COOLANT_TEMP", "OIL_TEMP", "INTAKE_TEMP"},
    "intake": {
        "MAF", "INTAKE_PRESSURE", "BAROMETRIC_PRESSURE",
        "VAG_AIR_MASS_ACTUAL", "VAG_BOOST_PRESSURE_REQUESTED",
        "VAG_BOOST_PRESSURE_ACTUAL", "VAG_EGR_COMMAND", "VAG_EGR_ACTUAL",
    },
    "fuel": {
        "SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "FUEL_PRESSURE",
        "VAG_INJECTION_QUANTITY", "VAG_INJECTION_DURATION", "VAG_INJECTION_TIMING",
        "VAG_TORSION_VALUE", "VAG_FUEL_RATE", "VAG_FUEL_TEMP",
        "VAG_INJECTOR_DEVIATION_1", "VAG_INJECTOR_DEVIATION_2",
        "VAG_INJECTOR_DEVIATION_3", "VAG_INJECTOR_DEVIATION_4",
        "VAG_INJECTOR_STATUS_1", "VAG_INJECTOR_STATUS_2",
        "VAG_INJECTOR_STATUS_3", "VAG_INJECTOR_STATUS_4",
        "VAG_INJECTOR_SWITCH_TIME_1", "VAG_INJECTOR_SWITCH_TIME_2",
        "VAG_INJECTOR_SWITCH_TIME_3", "VAG_INJECTOR_SWITCH_TIME_4",
    },
    "electrical": {"CONTROL_MODULE_VOLTAGE", "VAG_ECU_VOLTAGE"},
    "emissions": {"O2_B1S1", "CATALYST_TEMP"},
}

SYSTEM_LABELS = {
    "engine": "Motor y ralentí",
    "cooling": "Refrigeración",
    "intake": "Admisión y turbo",
    "fuel": "Combustible y mezcla",
    "electrical": "Batería y alternador",
    "emissions": "Emisiones / ITV",
}


def _valid_rows(df: Optional[pl.DataFrame]) -> Optional[pl.DataFrame]:
    if df is None or df.is_empty():
        return None
    needed = {"pid", "value", "timestamp_monotonic"}
    if not needed.issubset(df.columns):
        return None
    clean = df.filter(
        pl.col("pid").is_not_null()
        & pl.col("value").is_not_null()
        & pl.col("value").is_finite()
        & pl.col("timestamp_monotonic").is_not_null()
        & pl.col("timestamp_monotonic").is_finite()
    )
    return None if clean.is_empty() else clean


def _signal_values(df: Optional[pl.DataFrame], pid: str) -> List[float]:
    if df is None:
        return []
    return [float(value) for value in df.filter(pl.col("pid") == pid)["value"].to_list()]


def _add_alert(
    alerts: List[Dict[str, Any]],
    *,
    alert_id: str,
    system: str,
    severity: str,
    message: str,
    recommendation: str,
    pid: Optional[str] = None,
    value: Optional[float] = None,
    timestamp_sec: Optional[float] = None,
) -> None:
    alerts.append(
        {
            "id": alert_id,
            "system": system,
            "severity": severity,
            "message": message,
            "recommendation": recommendation,
            "pid": pid,
            "value": value,
            "timestamp_sec": timestamp_sec,
        }
    )


class DiagnosticSummary:
    """Builds dashboard-ready conclusions without claiming unsupported facts."""

    @staticmethod
    def build(
        df: Optional[pl.DataFrame],
        stats: Dict[str, Any],
        findings: Iterable[Dict[str, Any]],
        dtcs: Iterable[Dict[str, Any]],
        quality: Dict[str, Any],
        powertrain_type: str = "gasoline",
    ) -> Dict[str, Any]:
        clean = _valid_rows(df)
        findings = list(findings)
        dtcs = list(dtcs)
        alerts: List[Dict[str, Any]] = []

        if clean is None:
            _add_alert(
                alerts,
                alert_id="capture_no_valid_data",
                system="capture",
                severity="critical",
                message="La sesión no contiene ninguna lectura OBD válida.",
                recommendation="Comprueba contacto, puerto y adaptador antes de repetir la prueba.",
            )
        else:
            DiagnosticSummary._threshold_alerts(clean, alerts, powertrain_type)

        fuel_diagnosis = FuelConsumptionAnalyzer.build(clean, powertrain_type)
        trip_metrics = TripMetrics.calculate(clean)
        if fuel_diagnosis.get("status") == "attention":
            priorities = fuel_diagnosis.get("priorities") or []
            _add_alert(
                alerts,
                alert_id="diesel_fuel_consumption_evidence",
                system="fuel",
                severity="warning",
                message=str(fuel_diagnosis.get("summary") or "Hay indicios relacionados con el consumo."),
                recommendation=str(priorities[0] if priorities else "Revisa las métricas del diagnóstico de consumo."),
            )

        for index, finding in enumerate(findings):
            severity = str(finding.get("severity", "warning")).lower()
            _add_alert(
                alerts,
                alert_id=str(finding.get("rule_id", f"rule_{index}")),
                system=DiagnosticSummary._system_for_finding(finding),
                severity=severity if severity in {"info", "warning", "critical"} else "warning",
                message=str(finding.get("message", "Hallazgo diagnóstico")),
                recommendation="Revisa la evidencia del informe y confirma la causa con una prueba específica.",
            )

        for dtc in dtcs:
            code = str(dtc.get("code", "DTC"))
            _add_alert(
                alerts,
                alert_id=f"dtc_{code}",
                system="emissions",
                severity="warning",
                message=f"{code}: {dtc.get('description') or 'Código de avería registrado'}",
                recommendation="Lee el estado y freeze frame del DTC antes de borrar cualquier código.",
            )

        severity_order = {"critical": 0, "warning": 1, "info": 2}
        alerts.sort(key=lambda item: (severity_order.get(item["severity"], 3), item.get("timestamp_sec") or 0))
        health = DiagnosticSummary._health_by_system(clean, alerts)
        conclusion = DiagnosticSummary._conclusion(clean, alerts, health, quality)
        timeline = DiagnosticSummary._timeline(alerts)

        return {
            "health": health,
            "alerts": alerts,
            "timeline": timeline,
            "conclusion": conclusion,
            "quality": quality,
            "stats": stats,
            "fuel_diagnosis": fuel_diagnosis,
            "trip_metrics": trip_metrics,
        }

    @staticmethod
    def _threshold_alerts(df: pl.DataFrame, alerts: List[Dict[str, Any]], powertrain_type: str) -> None:
        checks = [
            ("COOLANT_TEMP", 110.0, "critical", "cooling", "Temperatura de refrigerante peligrosamente alta.", "Detén el vehículo con seguridad y revisa el sistema de refrigeración."),
            ("COOLANT_TEMP", 103.0, "warning", "cooling", "Temperatura de refrigerante elevada.", "Reduce carga y comprueba ventiladores, nivel y termostato."),
            ("CONTROL_MODULE_VOLTAGE", 15.2, "warning", "electrical", "Tensión de carga excesiva.", "Comprueba regulador y alternador con un multímetro."),
        ]
        for pid, threshold, severity, system, message, recommendation in checks:
            rows = df.filter((pl.col("pid") == pid) & (pl.col("value") >= threshold)).sort("timestamp_monotonic")
            if not rows.is_empty():
                row = rows.row(0, named=True)
                _add_alert(
                    alerts,
                    alert_id=f"{pid.lower()}_high_{threshold}",
                    system=system,
                    severity=severity,
                    message=message,
                    recommendation=recommendation,
                    pid=pid,
                    value=round(float(row["value"]), 2),
                    timestamp_sec=round(float(row["timestamp_monotonic"]), 2),
                )

        voltage_low = df.filter(
            (pl.col("pid") == "CONTROL_MODULE_VOLTAGE")
            & (pl.col("value") > 0)
            & (pl.col("value") < 11.8)
        ).sort("timestamp_monotonic")
        if not voltage_low.is_empty():
            row = voltage_low.row(0, named=True)
            _add_alert(
                alerts,
                alert_id="control_module_voltage_low",
                system="electrical",
                severity="warning",
                message="Tensión eléctrica baja durante la captura.",
                recommendation="Prueba batería, bornes, masas y carga del alternador.",
                pid="CONTROL_MODULE_VOLTAGE",
                value=round(float(row["value"]), 2),
                timestamp_sec=round(float(row["timestamp_monotonic"]), 2),
            )

        rpm_series = idle_rpm_series(df)
        if len(rpm_series) >= 20:
            idle_std = float(rpm_series.std() or 0)
            if idle_std > 150:
                _add_alert(
                    alerts,
                    alert_id="idle_rpm_instability",
                    system="engine",
                    severity="warning",
                    message="Las RPM presentan una variación elevada durante la sesión.",
                    recommendation="Repite la prueba de ralentí caliente y revisa admisión, EGR e inyección.",
                    pid="RPM",
                    value=round(idle_std, 1),
                )

        if powertrain_type.lower() not in {"diesel", "bev", "ev", "electric"}:
            trims = _signal_values(df, "LONG_FUEL_TRIM_1")
            if trims:
                mean_trim = sum(trims) / len(trims)
                if abs(mean_trim) > 12:
                    _add_alert(
                        alerts,
                        alert_id="long_fuel_trim_out_of_range",
                        system="fuel",
                        severity="warning",
                        message="La corrección de combustible a largo plazo está fuera del rango habitual.",
                        recommendation="Comprueba fugas de admisión, presión de combustible y medición MAF.",
                        pid="LONG_FUEL_TRIM_1",
                        value=round(mean_trim, 2),
                    )

    @staticmethod
    def _health_by_system(
        df: Optional[pl.DataFrame], alerts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        available = set()
        if df is not None:
            # Una señal aislada al principio de una ruta no basta para declarar
            # sano un sistema. Exigimos repetición y cobertura temporal mínima.
            for pid in df["pid"].unique().to_list():
                rows = df.filter(pl.col("pid") == pid)
                if rows.height < 5:
                    continue
                timestamps = rows["timestamp_monotonic"].to_list()
                if timestamps and float(max(timestamps)) - float(min(timestamps)) >= 10.0:
                    available.add(pid)
        result = []
        for system, signals in SYSTEM_SIGNAL_MAP.items():
            relevant = [alert for alert in alerts if alert["system"] == system]
            measured = sorted(signals.intersection(available))
            if any(alert["severity"] == "critical" for alert in relevant):
                status = "red"
                reason = relevant[0]["message"]
            elif relevant:
                status = "amber"
                reason = relevant[0]["message"]
            elif measured:
                status = "green"
                reason = f"Sin anomalías deterministas en {len(measured)} señales medidas."
            else:
                status = "unknown"
                reason = "Sin señales suficientes para evaluar este sistema."
            result.append(
                {
                    "id": system,
                    "label": SYSTEM_LABELS[system],
                    "status": status,
                    "reason": reason,
                    "signals": measured,
                }
            )
        return result

    @staticmethod
    def _conclusion(
        df: Optional[pl.DataFrame],
        alerts: List[Dict[str, Any]],
        health: List[Dict[str, Any]],
        quality: Dict[str, Any],
    ) -> Dict[str, Any]:
        if df is None:
            verdict, title = "invalid", "Prueba no válida"
        elif any(alert["severity"] == "critical" for alert in alerts):
            verdict, title = "urgent", "Revisión urgente"
        elif any(alert["severity"] == "warning" for alert in alerts):
            verdict, title = "attention", "Revisión recomendada"
        elif float(quality.get("overall_score", 0)) < 70:
            verdict, title = "limited", "Resultado limitado"
        else:
            verdict, title = "ok", "Sin anomalías evidentes"

        unknown_count = sum(item["status"] == "unknown" for item in health)
        summary = {
            "invalid": "No se puede diagnosticar porque la ECU no entregó datos válidos.",
            "urgent": "Se detectó al menos una condición que requiere atención inmediata.",
            "attention": "Hay evidencias que justifican comprobaciones mecánicas dirigidas.",
            "limited": "La captura contiene datos, pero su calidad o cobertura no permite una conclusión sólida.",
            "ok": "Las señales medidas no muestran anomalías deterministas.",
        }[verdict]
        if unknown_count:
            summary += f" {unknown_count} sistemas quedaron sin cobertura suficiente."

        next_steps = [alert["recommendation"] for alert in alerts[:3]]
        if not next_steps:
            next_steps = (
                ["Repite la prueba cuando la conexión con la ECU sea estable; esta sesión no tiene cobertura suficiente para diagnosticar."]
                if verdict == "limited"
                else ["Conserva esta sesión como referencia para futuras comparaciones antes/después."]
            )
        return {"verdict": verdict, "title": title, "summary": summary, "next_steps": next_steps}

    @staticmethod
    def _timeline(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "id": alert["id"],
                "timestamp_sec": alert.get("timestamp_sec"),
                "severity": alert["severity"],
                "system": alert["system"],
                "title": alert["message"],
                "evidence": (
                    f"{alert['pid']} = {alert['value']}"
                    if alert.get("pid") and alert.get("value") is not None
                    else "Evidencia de sesión"
                ),
            }
            for alert in alerts
        ]

    @staticmethod
    def _system_for_finding(finding: Dict[str, Any]) -> str:
        text = " ".join(
            str(finding.get(key, "")).lower()
            for key in ("finding_type", "rule_id", "message")
        )
        if "cool" in text or "temperat" in text:
            return "cooling"
        if "fuel" in text or "mezcla" in text:
            return "fuel"
        if "intake" in text or "turbo" in text or "maf" in text:
            return "intake"
        if "volt" in text or "bater" in text:
            return "electrical"
        if "emission" in text or "catal" in text:
            return "emissions"
        return "engine"
