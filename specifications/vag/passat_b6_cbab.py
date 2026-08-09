"""
Especificación Técnica OEM Confirmada para Volkswagen Passat B6 2.0 TDI (Motor CBAB).
Motor: CBAB (2.0 TDI 16V 140 CV Common Rail DPF 2008+)
Sistema de inyección: Common Rail Piezo (1800 bar)
ECU: Bosch EDC17 CP14
"""
from typing import Dict, Any

VAG_PASSAT_B6_CBAB_SPEC: Dict[str, Any] = {
    "metadata": {
        "manufacturer": "Volkswagen",
        "model": "Passat",
        "generation": "B6 (3C)",
        "engine_code": "CBAB",
        "engine_family": "EA189 2.0 TDI Common Rail",
        "displacement_cc": 1968,
        "valves": 16,
        "power_hp": 140,
        "fuel_type": "Diésel",
        "powertrain_type": "diesel",
        "injection_type": "common_rail",
        "injection_system": "Bosch Common Rail Piezo Generation 3 (1800 bar)",
        "ecu_family": "Bosch EDC17 CP14",
        "turbocharger": "BorgWarner BV43 VGT",
        "dpf_fitted": True,
        "emissions_standard": "Euro 5",
        "production_years": [2008, 2009, 2010],
        "market": "EU",
        "source_type": "OEM_CONFIRMED",
        "source_document": "Volkswagen ElsaWin & SSP 403 (The 2.0l TDI Engine with Common Rail Injection System)"
    },
    "parameters": {
        "idle_rpm": {
            "parameter": "RPM",
            "unit": "RPM",
            "conditions": {"engine_state": "warm"},
            "minimum": 760,
            "target": 790,
            "maximum": 820,
            "source_type": "OEM_CONFIRMED",
            "document": "VW Workshop Manual Passat B6 CR Engine Group 01",
            "section": "01-18 Common Rail Idle Calibration"
        },
        "coolant_temperature": {
            "parameter": "COOLANT_TEMP",
            "unit": "°C",
            "conditions": {"operating_mode": "normal_driving"},
            "minimum": 85.0,
            "target": 90.0,
            "maximum": 95.0,
            "source_type": "OEM_CONFIRMED",
            "document": "VW Cooling Manual EA189",
            "section": "Group 19 Thermostat Control"
        },
        "common_rail_pressure_idle": {
            "parameter": "FUEL_RAIL_PRESSURE",
            "unit": "bar",
            "conditions": {"engine_state": "warm_idle"},
            "minimum": 270,
            "target": 300,
            "maximum": 330,
            "source_type": "OEM_CONFIRMED",
            "document": "Bosch EDC17 CP14 Technical Specification",
            "section": "High Pressure Rail Target Map"
        },
        "common_rail_pressure_max": {
            "parameter": "FUEL_RAIL_PRESSURE_WOT",
            "unit": "bar",
            "conditions": {"pedal_pct": 100, "min_rpm": 3000},
            "minimum": 1650,
            "target": 1800,
            "maximum": 1850,
            "source_type": "OEM_CONFIRMED",
            "document": "Bosch EDC17 CP14 Technical Specification",
            "section": "Maximum Rail Pressure Limit"
        },
        "dpf_soot_mass_limit": {
            "parameter": "DPF_SOOT_MASS",
            "unit": "g",
            "conditions": {"ecu_calculated_model": "EA189 DPF Model"},
            "warning_threshold": 24.0,
            "critical_threshold": 40.0,
            "service_limit_ash": 70.0,
            "source_type": "OEM_CONFIRMED",
            "document": "SSP 403 - EA189 DPF Regeneration & Ash Load Specs",
            "section": "Exhaust Gas Recirculation & DPF Regeneration"
        }
    }
}
