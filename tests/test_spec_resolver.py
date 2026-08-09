"""
Pruebas unitarias para SpecResolver, PhysicalCoherenceValidator y el nuevo sistema de Fichas Técnicas OEM.
"""
import pytest
import polars as pl
from analysis.spec_resolver import SpecResolver
from analysis.coherence_rules import PhysicalCoherenceValidator
from analysis.vehicle_baselines import VehicleBaselineManager

def test_oem_spec_resolution_for_user_fleet():
    # 1. Opel Vectra 1.9 CDTI Z19DTH Diésel
    vectra_spec = SpecResolver.resolve_spec("vectra", "Opel", "Vectra", "Z19DTH", "diesel")
    assert vectra_spec["confidence_tier"] == "OEM_CONFIRMED"
    assert vectra_spec["metadata"]["engine_code"] == "Z19DTH"

    # 2. Mazda 3 1.5 Skyactiv-D Diésel (VGT VNT Intercooler Agua)
    mazda_spec = SpecResolver.resolve_spec("mazda_3", "Mazda", "Mazda 3", "S5-DPTS", "diesel")
    assert mazda_spec["confidence_tier"] == "OEM_CONFIRMED"
    assert "Variable-Geometry Turbocharger" in mazda_spec["metadata"]["turbocharger"]

    # 3. Volkswagen Passat B6 2.0 TDI CBAB Diésel
    passat_spec = SpecResolver.resolve_spec("passat_b6", "Volkswagen", "Passat", "CBAB", "diesel")
    assert passat_spec["confidence_tier"] == "OEM_CONFIRMED"
    assert passat_spec["metadata"]["engine_code"] == "CBAB"

    # 4. Tesla Model 3 Highland BEV
    tesla_spec = SpecResolver.resolve_spec("tesla_model3", "Tesla", "Model 3", "BEV", "bev")
    assert tesla_spec["confidence_tier"] == "OEM_CONFIRMED"
    assert tesla_spec["metadata"]["hv_architecture_nominal_voltage"] == 370.0

def test_generic_fallback_for_new_unknown_car():
    new_car_spec = SpecResolver.resolve_spec("seat_leon_friend", "Seat", "Leon", "2.0 TSI", "gasoline")
    assert new_car_spec["confidence_tier"] == "GENERIC_ENGINEERING_RANGE"
    assert "No es Ficha Oficial OEM" in new_car_spec["resolved_source"]


def test_oem_resolution_accepts_common_generation_names():
    passat_spec = SpecResolver.resolve_spec(
        "new-vehicle", "Volkswagen", "Passat B6", "CBAB", "diesel"
    )
    assert passat_spec["confidence_tier"] == "OEM_CONFIRMED"
    assert passat_spec["metadata"]["engine_code"] == "CBAB"

def test_physical_coherence_validator():
    # Diésel no debe evaluar STFT/LTFT de gasolina
    assert not PhysicalCoherenceValidator.validate_pid_relevance("STFT", "diesel")
    assert not PhysicalCoherenceValidator.validate_pid_relevance("LTFT", "diesel")
    assert PhysicalCoherenceValidator.validate_pid_relevance("RPM", "diesel")

    # Eléctrico no debe evaluar ENGINE_RPM ni DPF_SOOT_MASS, pero SÍ DRIVE_UNIT_FRONT_RPM y BATTERY_COOLANT_TEMP
    assert not PhysicalCoherenceValidator.validate_pid_relevance("ENGINE_RPM", "bev")
    assert not PhysicalCoherenceValidator.validate_pid_relevance("DPF_SOOT_MASS", "bev")
    assert PhysicalCoherenceValidator.validate_pid_relevance("DRIVE_UNIT_FRONT_RPM", "bev")
    assert PhysicalCoherenceValidator.validate_pid_relevance("BATTERY_COOLANT_TEMP", "bev")


def test_learned_vehicle_baseline():
    df = pl.DataFrame({
        "timestamp_ms": [0, 1000, 2000, 3000, 4000, 5000],
        "RPM": [800, 810, 805, 820, 795, 800],
        "COOLANT_TEMP": [85.0, 85.5, 86.0, 86.2, 86.5, 87.0]
    })
    baseline = VehicleBaselineManager.calculate_learned_baseline(df)
    assert baseline["confidence_tier"] == "VEHICLE_BASELINE"
    assert "RPM" in baseline["signals"]
    assert baseline["signals"]["RPM"]["p50_median"] == 802.5
