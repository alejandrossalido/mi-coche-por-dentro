"""
Especificaciones Técnicas Confirmadas OEM para Mazda 3 1.5 Skyactiv-D.
Motor: S5-DPTS (1.5 Turbodiésel Skyactiv-D)
Compresión: 14.8:1 (Baja compresión diésel)
Turbo: Turbocompresor de Geometría Variable (VGT) con sensor de velocidad e Intercooler de agua
ECU: Denso Skyactiv-D
"""
from typing import Dict, Any

MAZDA3_15_SKYACTIV_D_SPEC: Dict[str, Any] = {
    "metadata": {
        "manufacturer": "Mazda",
        "model": "Mazda 3",
        "generation": "BM / BN",
        "engine_code": "S5-DPTS",
        "engine_family": "SKYACTIV-D 1.5",
        "displacement_cc": 1499,
        "compression_ratio": "14.8:1",
        "valves": 16,
        "power_hp": 105,
        "fuel_type": "Diésel",
        "powertrain_type": "diesel",
        "injection_system": "Piezo-Common Rail Inyección Múltiple Directa Solenoide",
        "turbocharger": "Variable-Geometry Turbocharger (VGT) con sensor de velocidad de turbina",
        "intercooler": "Water-cooled Charge Air Cooler (Intercooler de Agua)",
        "ecu_family": "Denso Skyactiv Engine Control Module",
        "emissions_standard": "Euro 6b con DPF y Catalizador DeNOx NSC",
        "production_years": [2014, 2015, 2016, 2017, 2018],
        "market": "EU",
        "source_type": "OEM_CONFIRMED",
        "source_document": "Mazda Official Technical Release & Workshop Manual S5-DPTS"
    },
    "parameters": {
        "idle_rpm": {
            "parameter": "RPM",
            "unit": "RPM",
            "conditions": {"engine_state": "warm", "min_coolant_temp_c": 80},
            "minimum": 700,
            "target": 750,
            "maximum": 800,
            "source_type": "OEM_CONFIRMED",
            "document": "Mazda Workshop Service Manual S5-DPTS - Engine Group",
            "section": "Idle Speed Inspection S5 Engine"
        },
        "coolant_temperature": {
            "parameter": "COOLANT_TEMP",
            "unit": "°C",
            "conditions": {"operating_mode": "normal_driving"},
            "minimum": 82.0,
            "target": 88.0,
            "maximum": 93.0,
            "source_type": "OEM_CONFIRMED",
            "document": "Mazda Cooling System Specifications S5-DPTS",
            "section": "Thermostat Operation Range"
        },
        "boost_pressure_relative": {
            "parameter": "BOOST_PRESSURE_REL",
            "unit": "bar",
            "conditions": {"gear": 3, "min_rpm": 2200, "pedal_pct": 100},
            "minimum": 1.15,
            "target": 1.35,
            "maximum": 1.50,
            "source_type": "OEM_CONFIRMED",
            "document": "Mazda Powertrain Diagnostics S5-DPTS",
            "section": "VGT Boost Pressure Control"
        },
        "rail_pressure_idle": {
            "parameter": "FUEL_RAIL_PRESSURE",
            "unit": "bar",
            "conditions": {"engine_state": "warm_idle"},
            "minimum": 300,
            "target": 340,
            "maximum": 380,
            "source_type": "OEM_CONFIRMED",
            "document": "Denso Common Rail System Specification S5",
            "section": "Fuel High Pressure Target Map"
        }
    }
}
