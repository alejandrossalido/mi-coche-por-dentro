"""
Especificaciones Técnicas Confirmadas OEM / Base Profesional para Opel Vectra 1.9 CDTI.
Motor: Z19DTH / Z19DT (1.9 CDTI Turbodiésel Common Rail)
ECU: Bosch EDC16C39
"""
from typing import Dict, Any

OPEL_VECTRA_19_CDTI_SPEC: Dict[str, Any] = {
    "metadata": {
        "manufacturer": "Opel",
        "model": "Vectra C",
        "engine_code": "Z19DTH / Z19DT",
        "engine_family": "1.9 CDTI Ecotec",
        "displacement_cc": 1910,
        "fuel_type": "Diésel",
        "powertrain_type": "diesel",
        "injection_system": "Bosch Common Rail Multijet (1600 bar)",
        "ecu": "Bosch EDC16C39",
        "turbocharger": "Garrett GT1749MV (Geometría Variable VNT)",
        "emissions_standard": "Euro 4 con DPF / Filtro de Partículas",
        "confidence_tier": "OEM_CONFIRMED",
        "source_reference": "Opel TIS2000 & Bosch Technical Manual EDC16"
    },
    "parameters": {
        "idle_rpm": {
            "parameter": "RPM",
            "unit": "RPM",
            "condition": "Motor caliente (>80°C) en ralentí",
            "min": 780,
            "max": 880,
            "confidence": "OEM_CONFIRMED"
        },
        "coolant_temp": {
            "parameter": "COOLANT_TEMP",
            "unit": "°C",
            "condition": "Temperatura de servicio normal",
            "min": 82,
            "max": 95,
            "confidence": "OEM_CONFIRMED"
        },
        "map_intake_pressure": {
            "parameter": "INTAKE_PRESSURE",
            "unit": "kPa",
            "condition": "Ralentí a nivel del mar",
            "min": 96,
            "max": 104,
            "confidence": "OEM_CONFIRMED"
        },
        "boost_pressure_relative": {
            "parameter": "BOOST_PRESSURE_REL",
            "unit": "bar",
            "condition": "Aceleración WOT (>3000 RPM en carga)",
            "min": 1.15,
            "max": 1.45,
            "confidence": "OEM_CONFIRMED"
        },
        "rail_pressure": {
            "parameter": "FUEL_RAIL_PRESSURE",
            "unit": "bar",
            "condition": "Ralentí sin carga",
            "min": 260,
            "max": 340,
            "confidence": "OEM_CONFIRMED"
        },
        "rail_pressure_max": {
            "parameter": "FUEL_RAIL_PRESSURE_WOT",
            "unit": "bar",
            "condition": "Aceleración plena WOT",
            "min": 1350,
            "max": 1600,
            "confidence": "OEM_CONFIRMED"
        },
        "maf_idle": {
            "parameter": "MAF",
            "unit": "g/s",
            "condition": "Ralentí con EGR cerrada",
            "min": 11.0,
            "max": 16.0,
            "confidence": "TECHNICAL_DATABASE"
        },
        "control_module_voltage": {
            "parameter": "CONTROL_MODULE_VOLTAGE",
            "unit": "V",
            "condition": "Alternador en marcha",
            "min": 13.6,
            "max": 14.5,
            "confidence": "OEM_CONFIRMED"
        }
    }
}
