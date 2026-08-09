import polars as pl

from analysis.trip_metrics import TripMetrics


def test_trip_average_consumption_integrates_fuel_and_distance():
    rows = []
    # 60 km/h durante 120 s = 2 km; 6 L/h durante 120 s = 0,2 L.
    # Resultado esperado: 10 L/100 km.
    for timestamp in range(0, 121, 10):
        rows.append({"pid": "SPEED", "value": 60.0, "timestamp_monotonic": float(timestamp)})
        rows.append({"pid": "VAG_FUEL_RATE", "value": 6.0, "timestamp_monotonic": float(timestamp)})

    result = TripMetrics.calculate(pl.DataFrame(rows))

    assert result["available"] is True
    assert result["average_l_per_100km"] == 10.0
    assert result["distance_km"] == 2.0


def test_trip_average_requires_distance():
    rows = []
    for timestamp in (0.0, 10.0, 20.0):
        rows.append({"pid": "SPEED", "value": 0.0, "timestamp_monotonic": timestamp})
        rows.append({"pid": "VAG_FUEL_RATE", "value": 0.8, "timestamp_monotonic": timestamp})

    result = TripMetrics.calculate(pl.DataFrame(rows))

    assert result["available"] is False
    assert "distancia suficiente" in result["reason"]
