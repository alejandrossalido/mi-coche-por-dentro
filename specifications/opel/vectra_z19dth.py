"""
Especificación Técnica OEM Confirmada para Opel Vectra C 1.9 CDTI (Motor Z19DTH).
Motor: Z19DTH (1.9 CDTI 16V 150 CV con Swirl Flaps / Mariposas de Turbulencia en Admisión)
ECU: Bosch EDC16C39
"""
from typing import Dict, Any

OPEL_VECTRA_Z19DTH_SPEC: Dict[str, Any] = {
    "metadata": {
        "manufacturer": "Opel",
        "model": "Vectra",
        "generation": "C",
        "engine_code": "Z19DTH",
        "engine_family": "1.9 CDTI Ecotec 16V",
        "displacement_cc": 1910,
        "valves": 16,
        "power_hp": 150,
        "fuel_type": "Diésel",
        "powertrain_type": "diesel",
        "swirl_flaps_fitted": True,
        "ecu_family": "Bosch EDC16C39",
        "turbocharger": "Garrett GT1749MV VNT",
        "emissions_standard": "Euro 4",
        "production_years": [2004, 2005, 2006, 2007, 2008],
        "market": "EU",
        "source_type": "OEM_CONFIRMED",
        "source_document": "Opel TIS2000 & Bosch EDC16 Documentation Z19DTH"
    },
    "parameters": {
        "idle_rpm": {
            "parameter": "RPM",
            "unit": "RPM",
            "conditions": {"engine_state": "warm"},
            "minimum": 780,
            "target": 830,
            "maximum": 860,
            "source_type": "OEM_CONFIRMED",
            "document": "Opel TIS2000 Tech2 Data List Z19DTH",
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
            "section": "Thermostat Inspection Z19DTH"
        },
        "boost_pressure_relative": {
            "parameter": "BOOST_PRESSURE_REL",
            "unit": "bar",
            "conditions": {"gear": 3, "min_rpm": 2200, "pedal_pct": 100},
            "minimum": 1.15,
            "target": 1.35,
            "maximum": 1.45,
            "source_type": "OEM_CONFIRMED",
            "document": "Bosch EDC16C39 Boost Map Z19DTH",
            "section": "Charge Pressure Control WOT"
        },
        "swirl_actuator_duty": {
            "parameter": "SWIRL_FLAP_DUTY",
            "unit": "%",
            "conditions": {"rpm_range": [1500, 2800]},
            "minimum": 10.0,
            "target": 50.0,
            "maximum": 90.0,
            "source_type": "OEM_CONFIRMED",
            "document": "Opel TIS2000 Swirl Flap Actuator Calibration",
            "section": "Variable Swirl Control Solenoid"
        }
    }
}
