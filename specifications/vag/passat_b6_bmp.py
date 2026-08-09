"""
Especificación Técnica OEM Confirmada para Volkswagen Passat B6 2.0 TDI (Motor BMP).
Motor: BMP (2.0 TDI 8V 140 CV con DPF)
Sistema de inyección: Bomba-Inyector (Pumpe-Düse Bosch)
ECU: Bosch EDC16U31
"""
from typing import Dict, Any

VAG_PASSAT_B6_BMP_SPEC: Dict[str, Any] = {
    "metadata": {
        "manufacturer": "Volkswagen",
        "model": "Passat",
        "generation": "B6 (3C)",
        "engine_code": "BMP",
        "engine_family": "EA188 2.0 TDI 8V",
        "displacement_cc": 1968,
        "valves": 8,
        "power_hp": 140,
        "fuel_type": "Diésel",
        "powertrain_type": "diesel",
        "injection_type": "pumpe_duese",
        "injection_system": "Bomba-Inyector Solenoide Bosch (1400-2000 bar en elemento)",
        "ecu_family": "Bosch EDC16U31",
        "turbocharger": "Garrett GT1749VA (Geometría Variable VNT)",
        "dpf_fitted": True,
        "emissions_standard": "Euro 4",
        "production_years": [2005, 2006, 2007, 2008, 2009],
        "market": "EU",
        "source_type": "OEM_CONFIRMED",
        "source_document": "Volkswagen ElsaWin & SSP 316 (The 2.0l TDI Engine with 8-Valve Technology)"
    },
    "parameters": {
        "idle_rpm": {
            "parameter": "RPM",
            "unit": "RPM",
            "conditions": {"engine_state": "warm", "min_coolant_temp_c": 80},
            "minimum": 780,
            "target": 810,
            "maximum": 840,
            "source_type": "OEM_CONFIRMED",
            "document": "VW Workshop Manual Passat B6 - Engine Repair Group 01",
            "section": "01-15 Idle Speed Inspection"
        },
        "coolant_temperature": {
            "parameter": "COOLANT_TEMP",
            "unit": "°C",
            "conditions": {"operating_mode": "normal_driving"},
            "minimum": 85.0,
            "target": 90.0,
            "maximum": 98.0,
            "source_type": "OEM_CONFIRMED",
            "document": "VW Workshop Manual Passat B6 - Cooling System Group 19",
            "section": "19-02 Thermostat Opening Ranges"
        },
        "boost_pressure_relative": {
            "parameter": "BOOST_PRESSURE_REL",
            "unit": "bar",
            "conditions": {"gear": 3, "min_rpm": 2200, "pedal_pct": 100},
            "minimum": 1.15,
            "target": 1.35,
            "maximum": 1.45,
            "source_type": "OEM_CONFIRMED",
            "document": "VW Diagnostics Manual EDC16U31",
            "section": "MVB 011 Boost Pressure Control"
        },
        "dpf_soot_mass_limit": {
            "parameter": "DPF_SOOT_MASS",
            "unit": "g",
            "conditions": {"ecu_calculated_model": "Bosch DPF Ash/Soot Load"},
            "warning_threshold": 30.0,
            "critical_threshold": 45.0,
            "service_limit_ash": 60.0,
            "source_type": "OEM_CONFIRMED",
            "document": "SSP 336 - The Diesel Particulate Filter System with Additive",
            "section": "Ash Saturation Calculation Model"
        }
    }
}
