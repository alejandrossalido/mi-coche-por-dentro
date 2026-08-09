"""
Especificación Técnica OEM Confirmada para Opel Vectra C 1.9 CDTI (Motor Z19DT).
Motor: Z19DT (1.9 CDTI 8V 120 CV)
ECU: Bosch EDC16C39
"""
from typing import Dict, Any

OPEL_VECTRA_Z19DT_SPEC: Dict[str, Any] = {
    "metadata": {
        "manufacturer": "Opel",
        "model": "Vectra",
        "generation": "C",
        "engine_code": "Z19DT",
        "engine_family": "1.9 CDTI Ecotec 8V",
        "displacement_cc": 1910,
        "valves": 8,
        "power_hp": 120,
        "fuel_type": "Diésel",
        "powertrain_type": "diesel",
        "swirl_flaps_fitted": False,
        "ecu_family": "Bosch EDC16C39",
        "turbocharger": "Garrett GT1749V VNT",
        "emissions_standard": "Euro 4",
        "production_years": [2004, 2005, 2006, 2007, 2008],
        "market": "EU",
        "source_type": "OEM_CONFIRMED",
        "source_document": "Opel TIS2000 & Bosch EDC16 Documentation Z19DT"
    },
    "parameters": {
        "idle_rpm": {
            "parameter": "RPM",
            "unit": "RPM",
            "conditions": {"engine_state": "warm"},
            "minimum": 800,
            "target": 850,
            "maximum": 880,
            "source_type": "OEM_CONFIRMED",
            "document": "Opel TIS2000 Tech2 Data List Z19DT",
            "section": "Engine Idle Speed Regulation"
        },
        "coolant_temperature": {
            "parameter": "COOLANT_TEMP",
            "unit": "°C",
            "conditions": {"operating_mode": "normal_driving"},
            "minimum": 82.0,
            "target": 88.0,
            "maximum": 95.0,
            "source_type": "OEM_CONFIRMED",
            "document": "Opel TIS2000 Engine Cooling Group K",
            "section": "Thermostat Inspection Z19DT"
        },
        "boost_pressure_relative": {
            "parameter": "BOOST_PRESSURE_REL",
            "unit": "bar",
            "conditions": {"gear": 3, "min_rpm": 2000, "pedal_pct": 100},
            "minimum": 1.05,
            "target": 1.25,
            "maximum": 1.35,
            "source_type": "OEM_CONFIRMED",
            "document": "Bosch EDC16C39 Boost Map Z19DT",
            "section": "Charge Pressure Control"
        }
    }
}
