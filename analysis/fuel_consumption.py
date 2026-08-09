"""Diagnóstico determinista de consumo para motores diésel Volkswagen.

El analizador separa datos medidos de hipótesis. Solo eleva una prioridad
cuando la sesión contiene la ventana operativa necesaria (por ejemplo,
ralentí con motor caliente o carga sostenida).
"""

from __future__ import annotations

from bisect import bisect_left
from statistics import median
from typing import Any, Dict, Iterable, List, Optional, Tuple

import polars as pl


FUEL_DIAGNOSTIC_SIGNALS = (
    "COOLANT_TEMP",
    "VAG_FUEL_TEMP",
    "VAG_INJECTION_QUANTITY",
    "VAG_INJECTION_DURATION",
    "VAG_INJECTION_TIMING",
    "VAG_TORSION_VALUE",
    "VAG_FUEL_RATE",
    "VAG_AIR_MASS_ACTUAL",
    "VAG_EGR_COMMAND",
    "VAG_EGR_ACTUAL",
    "VAG_BOOST_PRESSURE_REQUESTED",
    "VAG_BOOST_PRESSURE_ACTUAL",
    "VAG_INJECTOR_DEVIATION_1",
    "VAG_INJECTOR_DEVIATION_2",
    "VAG_INJECTOR_DEVIATION_3",
    "VAG_INJECTOR_DEVIATION_4",
    "VAG_INJECTOR_STATUS_1",
    "VAG_INJECTOR_STATUS_2",
    "VAG_INJECTOR_STATUS_3",
    "VAG_INJECTOR_STATUS_4",
    "VAG_INJECTOR_SWITCH_TIME_1",
    "VAG_INJECTOR_SWITCH_TIME_2",
    "VAG_INJECTOR_SWITCH_TIME_3",
    "VAG_INJECTOR_SWITCH_TIME_4",
)


def _rows(df: pl.DataFrame, pid: str) -> List[Tuple[float, float]]:
    subset = (
        df.filter(
            (pl.col("pid") == pid)
            & pl.col("value").is_not_null()
            & pl.col("value").is_finite()
            & pl.col("timestamp_monotonic").is_not_null()
            & pl.col("timestamp_monotonic").is_finite()
        )
        .select("timestamp_monotonic", "value")
        .sort("timestamp_monotonic")
    )
    return [(float(t), float(v)) for t, v in subset.iter_rows()]


def _nearest(rows: List[Tuple[float, float]], timestamp: float, tolerance: float) -> Optional[float]:
    if not rows:
        return None
    times = [item[0] for item in rows]
    index = bisect_left(times, timestamp)
    candidates = []
    if index < len(rows):
        candidates.append(rows[index])
    if index:
        candidates.append(rows[index - 1])
    nearest = min(candidates, key=lambda item: abs(item[0] - timestamp))
    return nearest[1] if abs(nearest[0] - timestamp) <= tolerance else None


def _context_values(
    df: pl.DataFrame,
    pid: str,
    *,
    warm_idle: bool = False,
    under_load: bool = False,
) -> List[float]:
    target = _rows(df, pid)
    if not warm_idle and not under_load:
        return [value for _, value in target]
    rpm = _rows(df, "RPM")
    speed = _rows(df, "SPEED")
    coolant = _rows(df, "COOLANT_TEMP")
    result: List[float] = []
    for timestamp, value in target:
        rpm_value = _nearest(rpm, timestamp, 2.0)
        speed_value = _nearest(speed, timestamp, 2.0)
        coolant_value = _nearest(coolant, timestamp, 15.0)
        if rpm_value is None or speed_value is None:
            continue
        if warm_idle and (
            not 650 <= rpm_value <= 1000
            or speed_value > 1
            or coolant_value is None
            or coolant_value < 75
        ):
            continue
        if under_load and not (1400 <= rpm_value <= 3400 and speed_value >= 30):
            continue
        result.append(value)
    return result


def _paired_error_percent(
    df: pl.DataFrame,
    requested_pid: str,
    actual_pid: str,
    *,
    under_load: bool = False,
) -> List[float]:
    requested = _rows(df, requested_pid)
    actual = _rows(df, actual_pid)
    rpm = _rows(df, "RPM")
    speed = _rows(df, "SPEED")
    errors: List[float] = []
    for timestamp, requested_value in requested:
        actual_value = _nearest(actual, timestamp, 2.0)
        if actual_value is None or abs(requested_value) < 1:
            continue
        if under_load:
            rpm_value = _nearest(rpm, timestamp, 2.0)
            speed_value = _nearest(speed, timestamp, 2.0)
            if rpm_value is None or speed_value is None or not (1400 <= rpm_value <= 3400 and speed_value >= 30):
                continue
        errors.append(abs(actual_value - requested_value) / abs(requested_value) * 100.0)
    return errors


def _metric(
    metric_id: str,
    label: str,
    value: float,
    unit: str,
    status: str,
    interpretation: str,
) -> Dict[str, Any]:
    return {
        "id": metric_id,
        "label": label,
        "value": round(float(value), 2),
        "unit": unit,
        "status": status,
        "interpretation": interpretation,
    }


class FuelConsumptionAnalyzer:
    """Resume evidencias relacionadas con consumo sin diagnosticar por descarte."""

    @staticmethod
    def build(df: Optional[pl.DataFrame], powertrain_type: str) -> Dict[str, Any]:
        if powertrain_type.lower() not in {"diesel", "hybrid", "phev"}:
            return {"applicable": False, "status": "not_applicable"}
        if df is None or df.is_empty() or not {"pid", "value", "timestamp_monotonic"}.issubset(df.columns):
            return {
                "applicable": True,
                "status": "no_data",
                "title": "Consumo sin datos suficientes",
                "summary": "Todavía no existe una captura válida para evaluar el sistema de inyección.",
                "metrics": [],
                "priorities": ["Realiza la prueba guiada «Consumo e inyección»."],
                "coverage": {"captured": 0, "total": len(FUEL_DIAGNOSTIC_SIGNALS), "missing": list(FUEL_DIAGNOSTIC_SIGNALS)},
            }

        available = set(df.filter(pl.col("value").is_not_null())["pid"].unique().to_list())
        captured = [pid for pid in FUEL_DIAGNOSTIC_SIGNALS if pid in available]
        missing = [pid for pid in FUEL_DIAGNOSTIC_SIGNALS if pid not in available]
        metrics: List[Dict[str, Any]] = []
        priorities: List[str] = []
        evidence_issues: List[str] = []

        timestamps = [float(value) for value in df["timestamp_monotonic"].drop_nulls().to_list()]
        duration_sec = max(timestamps) - min(timestamps) if timestamps else 0.0
        coolant = _context_values(df, "COOLANT_TEMP")
        if coolant:
            maximum = max(coolant)
            status = "warning" if duration_sec >= 600 and maximum < 75 else "ok"
            explanation = (
                "No alcanzó temperatura de servicio; un termostato abierto puede aumentar claramente el consumo."
                if status == "warning"
                else "Temperatura máxima registrada; solo se considera concluyente con al menos 10 minutos de circulación."
            )
            metrics.append(_metric("coolant_max", "Refrigerante máximo", maximum, "°C", status, explanation))
            if status == "warning":
                priorities.append("Comprobar termostato y sensor de temperatura del refrigerante.")
                evidence_issues.append("temperatura de servicio insuficiente")

        injection_quantity = _context_values(df, "VAG_INJECTION_QUANTITY", warm_idle=True)
        if injection_quantity:
            quantity = median(injection_quantity)
            status = "warning" if quantity < 3 or quantity > 10 else "ok"
            metrics.append(_metric(
                "warm_idle_injection_quantity",
                "Cantidad de inyección al ralentí caliente",
                quantity,
                "mg/str",
                status,
                "En esta familia PPD, 3–10 mg/str es la referencia del bloque de medida en ralentí.",
            ))
            if status == "warning":
                priorities.append("Revisar sincronización, medición de aire y equilibrio de inyectores por cantidad de inyección anómala.")
                evidence_issues.append("cantidad de inyección fuera de referencia")

        fuel_rate = _context_values(df, "VAG_FUEL_RATE", warm_idle=True)
        if fuel_rate:
            rate = median(fuel_rate)
            enough_idle_samples = len(fuel_rate) >= 3
            rate_status = "insufficient" if not enough_idle_samples else ("reference" if rate <= 1.2 else "warning")
            metrics.append(_metric(
                "warm_idle_fuel_rate",
                "Consumo al ralentí caliente",
                rate,
                "L/h",
                rate_status,
                (
                    "Solo hay una o dos lecturas válidas en ralentí caliente; no bastan para valorar el consumo."
                    if not enough_idle_samples
                    else "Sirve para comparar sesiones equivalentes; climatizador, alternador y temperatura cambian este valor."
                ),
            ))
            if enough_idle_samples and rate > 1.2:
                priorities.append("Repetir el ralentí sin climatizador y comprobar por qué la carga de combustible supera 1,2 L/h.")
                evidence_issues.append("consumo alto al ralentí caliente")

        torsion_values = _context_values(df, "VAG_TORSION_VALUE", warm_idle=True)
        if torsion_values:
            torsion = median(torsion_values)
            status = "warning" if abs(torsion) > 1.5 else "ok"
            metrics.append(_metric(
                "torsion_value",
                "Torsión de distribución al ralentí",
                torsion,
                "°CA",
                status,
                "La referencia específica del bloque es −1,5 a +1,5 °CA al ralentí.",
            ))
            if status == "warning":
                priorities.append("Comprobar calado de distribución y valor de torsión antes de culpar a los inyectores.")
                evidence_issues.append("sincronización de distribución fuera de referencia")

        injector_medians: List[float] = []
        for cylinder in range(1, 5):
            values = _context_values(df, f"VAG_INJECTOR_DEVIATION_{cylinder}", warm_idle=True)
            if values:
                injector_medians.append(median(values))
        if len(injector_medians) == 4:
            quantity_reference = median(injection_quantity) if injection_quantity else 7.0
            allowed = min(3.8, max(1.9, quantity_reference * 0.38))
            worst = max(abs(value) for value in injector_medians)
            status = "warning" if worst > allowed else "ok"
            metrics.append(_metric(
                "injector_balance",
                "Mayor corrección de inyector",
                worst,
                "mg/str",
                status,
                f"Límite adaptado a la cantidad de inyección registrada: ±{allowed:.2f} mg/str.",
            ))
            if status == "warning":
                priorities.append("Comprobar el cilindro con mayor corrección: inyector, cableado, compresión y asiento.")
                evidence_issues.append("desequilibrio de inyectores")

        status_values: List[float] = []
        for cylinder in range(1, 5):
            status_values.extend(_context_values(df, f"VAG_INJECTOR_STATUS_{cylinder}"))
        # En el bloque 018, 2 significa regulación durante el arranque y 4
        # cantidad muy pequeña/válvula desconectada: son estados operativos,
        # no fallos BIP por sí solos. Los bits 16/32/64/128 sí requieren aviso.
        fault_statuses = [value for value in status_values if int(value) & (16 | 32 | 64 | 128)]
        operational_statuses = [value for value in status_values if value != 0 and value not in fault_statuses]
        if status_values:
            metrics.append(_metric(
                "injector_status",
                "Estados BIP de inyector con fallo",
                len(fault_statuses),
                "eventos",
                "warning" if fault_statuses else "ok",
                f"Los estados operativos de arranque o corte no se cuentan como fallo ({len(operational_statuses)} observados).",
            ))
            if fault_statuses:
                priorities.append("Revisar los códigos de estado BIP de los inyectores y el mazo eléctrico de la culata.")
                evidence_issues.append("estado de inyector distinto de cero")

        switch_time_medians: List[float] = []
        for cylinder in range(1, 5):
            values = _context_values(df, f"VAG_INJECTOR_SWITCH_TIME_{cylinder}")
            if values:
                switch_time_medians.append(median(values))
        if len(switch_time_medians) == 4:
            outside = [value for value in switch_time_medians if not 0.18 <= value <= 0.25]
            metrics.append(_metric(
                "injector_switch_time",
                "Peor tiempo de conmutación de inyector",
                max(switch_time_medians, key=lambda value: abs(value - 0.215)),
                "ms",
                "warning" if outside else "ok",
                "La etiqueta específica de la ECU 03G-906-018 establece 0,18–0,25 ms para los cuatro cilindros.",
            ))
            if outside:
                priorities.append("Revisar el inyector o cableado del cilindro cuyo tiempo de conmutación quede fuera de 0,18–0,25 ms.")
                evidence_issues.append("tiempo de conmutación de inyector fuera de referencia")

        egr_errors = _paired_error_percent(df, "VAG_EGR_COMMAND", "VAG_EGR_ACTUAL")
        if len(egr_errors) >= 10:
            egr_error = median(egr_errors)
            status = "warning" if egr_error > 25 else "ok"
            metrics.append(_metric(
                "egr_tracking_error",
                "Error medio de seguimiento EGR",
                egr_error,
                "%",
                status,
                "Compara masa de aire solicitada y real; una desviación persistente puede señalar EGR, MAF o admisión.",
            ))
            if status == "warning":
                priorities.append("Comprobar EGR, caudalímetro y fugas/obstrucciones de admisión.")
                evidence_issues.append("seguimiento EGR/masa de aire deficiente")

        boost_errors = _paired_error_percent(
            df,
            "VAG_BOOST_PRESSURE_REQUESTED",
            "VAG_BOOST_PRESSURE_ACTUAL",
            under_load=True,
        )
        if len(boost_errors) >= 10:
            boost_error = median(boost_errors)
            status = "warning" if boost_error > 20 else "ok"
            metrics.append(_metric(
                "boost_tracking_error",
                "Error medio de presión de turbo bajo carga",
                boost_error,
                "%",
                status,
                "Un error sostenido puede aumentar el combustible necesario para obtener la misma potencia.",
            ))
            if status == "warning":
                priorities.append("Comprobar vacío, geometría del turbo, manguitos e intercooler.")
                evidence_issues.append("presión de turbo no sigue la solicitada")

        if evidence_issues:
            status = "attention"
            title = "Hay indicios relacionados con el consumo"
            summary = "La captura señala: " + ", ".join(evidence_issues) + "."
        elif len(captured) >= 12 and injection_quantity and len(injector_medians) == 4:
            status = "ok"
            title = "Inyección sin anomalías deterministas"
            summary = "Los canales medidos no explican por sí solos el consumo alto; conviene revisar rodadura, frenos, neumáticos, trayectos y comparar el consumo real de depósito a depósito."
        else:
            status = "insufficient"
            title = "Faltan datos para explicar el consumo"
            summary = f"Esta sesión contiene {len(captured)} de {len(FUEL_DIAGNOSTIC_SIGNALS)} señales prioritarias. La prueba anterior no registró todavía los bloques PPD ampliados."
            priorities.insert(0, "Realiza la prueba guiada «Consumo e inyección» con el motor caliente.")

        return {
            "applicable": True,
            "status": status,
            "title": title,
            "summary": summary,
            "metrics": metrics,
            "priorities": list(dict.fromkeys(priorities))[:6],
            "coverage": {"captured": len(captured), "total": len(FUEL_DIAGNOSTIC_SIGNALS), "missing": missing},
        }


__all__ = ["FUEL_DIAGNOSTIC_SIGNALS", "FuelConsumptionAnalyzer"]
