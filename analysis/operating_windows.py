"""Selección conservadora de ventanas de funcionamiento del motor."""

from __future__ import annotations

import polars as pl


def idle_rpm_series(
    df: pl.DataFrame,
    *,
    max_speed_kmh: float = 1.0,
    min_running_rpm: float = 600.0,
    max_idle_rpm: float = 1100.0,
) -> pl.Series:
    """Devuelve RPM de ralentí real, excluyendo motor parado y acelerones."""
    required = {"pid", "value", "timestamp_monotonic"}
    if df is None or df.is_empty() or not required.issubset(df.columns):
        return pl.Series("rpm", [], dtype=pl.Float64)

    rpm = df.filter(pl.col("pid") == "RPM").select(
        "timestamp_monotonic", pl.col("value").cast(pl.Float64).alias("rpm")
    )
    speed = df.filter(pl.col("pid") == "SPEED").select(
        "timestamp_monotonic", pl.col("value").cast(pl.Float64).alias("speed")
    )
    if rpm.is_empty() or speed.is_empty():
        return pl.Series("rpm", [], dtype=pl.Float64)

    return (
        rpm.join(speed, on="timestamp_monotonic", how="inner")
        .filter(
            (pl.col("speed") <= max_speed_kmh)
            & pl.col("rpm").is_between(min_running_rpm, max_idle_rpm, closed="both")
        )["rpm"]
    )
