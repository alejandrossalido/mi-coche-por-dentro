"""Métricas de trayecto calculadas a partir de telemetría sincronizada."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

import polars as pl


def _points(df: pl.DataFrame, pid_names: Iterable[str]) -> list[tuple[float, float]]:
    for pid in pid_names:
        rows = (
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
        if rows.height < 3:
            continue
        # Una misma respuesta física puede generar varias filas con la misma
        # marca temporal. Para integrar solo necesitamos un valor por instante.
        collapsed = rows.group_by("timestamp_monotonic", maintain_order=True).agg(pl.col("value").last())
        return [(float(row[0]), float(row[1])) for row in collapsed.iter_rows()]
    return []


def _interpolate(points: list[tuple[float, float]], timestamp: float) -> float:
    if timestamp <= points[0][0]:
        return points[0][1]
    if timestamp >= points[-1][0]:
        return points[-1][1]
    for index in range(1, len(points)):
        right_t, right_v = points[index]
        if right_t < timestamp:
            continue
        left_t, left_v = points[index - 1]
        if right_t == left_t:
            return right_v
        ratio = (timestamp - left_t) / (right_t - left_t)
        return left_v + ratio * (right_v - left_v)
    return points[-1][1]


def _integral(points: list[tuple[float, float]], start: float, end: float) -> float:
    clipped = [(start, _interpolate(points, start))]
    clipped.extend((t, v) for t, v in points if start < t < end)
    clipped.append((end, _interpolate(points, end)))
    return sum(
        (clipped[index - 1][1] + clipped[index][1]) / 2.0
        * (clipped[index][0] - clipped[index - 1][0])
        for index in range(1, len(clipped))
    )


class TripMetrics:
    @staticmethod
    def calculate(df: Optional[pl.DataFrame]) -> Dict[str, Any]:
        empty = {
            "available": False,
            "average_l_per_100km": None,
            "distance_km": 0.0,
            "fuel_liters": 0.0,
            "duration_sec": 0.0,
            "confidence": "insufficient",
            "reason": "Se necesitan velocidad y caudal de combustible repetidos durante la marcha.",
        }
        if df is None or df.is_empty() or not {"pid", "value", "timestamp_monotonic"}.issubset(df.columns):
            return empty

        speed = _points(df, ("SPEED",))
        fuel_rate = _points(df, ("VAG_FUEL_RATE", "FUEL_RATE"))
        if len(speed) < 3 or len(fuel_rate) < 3:
            return empty

        start = max(speed[0][0], fuel_rate[0][0])
        end = min(speed[-1][0], fuel_rate[-1][0])
        duration = end - start
        if duration < 10:
            return {**empty, "duration_sec": round(max(0.0, duration), 1)}

        distance_km = _integral(speed, start, end) / 3600.0
        fuel_liters = _integral(fuel_rate, start, end) / 3600.0
        if distance_km < 0.1:
            return {
                **empty,
                "fuel_liters": round(max(0.0, fuel_liters), 4),
                "duration_sec": round(duration, 1),
                "reason": "Todavía no se ha recorrido distancia suficiente para calcular L/100 km.",
            }

        average = max(0.0, fuel_liters / distance_km * 100.0)
        confidence = "good" if duration >= 120 and distance_km >= 1.0 and len(fuel_rate) >= 20 else "provisional"
        return {
            "available": True,
            "average_l_per_100km": round(average, 2),
            "distance_km": round(distance_km, 3),
            "fuel_liters": round(fuel_liters, 4),
            "duration_sec": round(duration, 1),
            "speed_samples": len(speed),
            "fuel_samples": len(fuel_rate),
            "confidence": confidence,
            "reason": (
                "Promedio integrado con velocidad y caudal medidos durante el trayecto."
                if confidence == "good"
                else "Estimación provisional: ganará precisión al prolongar el trayecto."
            ),
        }
