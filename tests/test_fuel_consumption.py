import polars as pl

from analysis.fuel_consumption import FuelConsumptionAnalyzer


def _sample(pid: str, value: float, timestamp: float):
    return {"pid": pid, "value": value, "timestamp_monotonic": timestamp}


def test_fuel_diagnosis_uses_only_warm_idle_for_injector_balance():
    rows = []
    for index in range(30):
        timestamp = float(index)
        rows.extend([
            _sample("RPM", 800.0, timestamp),
            _sample("SPEED", 0.0, timestamp),
            _sample("COOLANT_TEMP", 88.0, timestamp),
            _sample("VAG_INJECTION_QUANTITY", 5.0, timestamp),
            _sample("VAG_FUEL_RATE", 0.7, timestamp),
            _sample("VAG_TORSION_VALUE", 0.4, timestamp),
            _sample("VAG_INJECTOR_DEVIATION_1", 0.2, timestamp),
            _sample("VAG_INJECTOR_DEVIATION_2", -0.1, timestamp),
            _sample("VAG_INJECTOR_DEVIATION_3", 0.15, timestamp),
            _sample("VAG_INJECTOR_DEVIATION_4", -0.25, timestamp),
        ])

    result = FuelConsumptionAnalyzer.build(pl.DataFrame(rows), "diesel")

    assert not any("desequilibrio de inyectores" in item for item in result["summary"].splitlines())
    injector_metric = next(item for item in result["metrics"] if item["id"] == "injector_balance")
    assert injector_metric["status"] == "ok"


def test_fuel_diagnosis_flags_torsion_and_injector_imbalance_with_evidence():
    rows = []
    for index in range(30):
        timestamp = float(index)
        rows.extend([
            _sample("RPM", 800.0, timestamp),
            _sample("SPEED", 0.0, timestamp),
            _sample("COOLANT_TEMP", 90.0, timestamp),
            _sample("VAG_INJECTION_QUANTITY", 5.0, timestamp),
            _sample("VAG_TORSION_VALUE", 2.5, timestamp),
            _sample("VAG_INJECTOR_DEVIATION_1", 2.5, timestamp),
            _sample("VAG_INJECTOR_DEVIATION_2", -0.7, timestamp),
            _sample("VAG_INJECTOR_DEVIATION_3", -0.8, timestamp),
            _sample("VAG_INJECTOR_DEVIATION_4", -1.0, timestamp),
        ])

    result = FuelConsumptionAnalyzer.build(pl.DataFrame(rows), "diesel")

    assert result["status"] == "attention"
    assert "desequilibrio de inyectores" in result["summary"]
    assert "sincronización de distribución" in result["summary"]


def test_fuel_diagnosis_does_not_treat_start_control_as_bip_failure():
    rows = []
    for index, state in enumerate([0.0, 2.0, 0.0, 2.0]):
        rows.extend([
            _sample("VAG_INJECTOR_STATUS_1", 0.0, float(index)),
            _sample("VAG_INJECTOR_STATUS_2", state, float(index)),
            _sample("VAG_INJECTOR_STATUS_3", 0.0, float(index)),
            _sample("VAG_INJECTOR_STATUS_4", 0.0, float(index)),
        ])

    result = FuelConsumptionAnalyzer.build(pl.DataFrame(rows), "diesel")
    metric = next(item for item in result["metrics"] if item["id"] == "injector_status")

    assert metric["status"] == "ok"
    assert metric["value"] == 0


def test_fuel_diagnosis_requires_repeated_warm_idle_fuel_rate():
    rows = [
        _sample("RPM", 800.0, 0.0),
        _sample("SPEED", 0.0, 0.0),
        _sample("COOLANT_TEMP", 85.0, 0.0),
        _sample("VAG_FUEL_RATE", 1.5, 0.0),
    ]

    result = FuelConsumptionAnalyzer.build(pl.DataFrame(rows), "diesel")
    metric = next(item for item in result["metrics"] if item["id"] == "warm_idle_fuel_rate")

    assert metric["status"] == "insufficient"
    assert not any("supera 1,2" in item for item in result["priorities"])
