"""
Especificaciones Técnicas Confirmadas OEM para Volkswagen Passat B6 2.0 TDI.
Motorizaciones soportadas:
- BMP: 2.0 TDI 8V 140 CV DPF (Bomba-Inyector PD)
- BKP: 2.0 TDI 16V 140 CV Sin DPF (Bomba-Inyector Piezo PD)
- CBAB / CBBB: 2.0 TDI 140/170 CV Common Rail DPF (2008+)
ECU: Bosch EDC16U31 / EDC17 CP14
"""
from typing import Dict, Any

VAG_PASSAT_B6_20_TDI_SPEC: Dict[str, Any] = {
    "metadata": {
        "manufacturer": "Volkswagen",
        "model": "Passat B6 (3C2 / 3C5)",
        "engine_code_variants": ["BMP", "BKP", "CBAB", "CBBB"],
        "engine_family": "2.0 TDI EA188 (PD) / EA189 (CR)",
        "displacement_cc": 1968,
        "fuel_type": "Diésel",
        "powertrain_type": "diesel",
        "injection_system": "Pumpe-Düse (Bomba-Inyector) o Common Rail según código",
        "ecu_variants": ["Bosch EDC16U31", "Bosch EDC16U34", "Bosch EDC17 CP14"],
        "turbocharger": "Garrett GT1749VA / BorgWarner KKK VGT",
        "emissions_standard": "Euro 4 / Euro 5 con DPF opcional/estándar",
        "confidence_tier": "OEM_CONFIRMED",
        "source_reference": "VAG ElsaWin & SSP 316/403 (Self-Study Program 2.0 TDI)"
    },
    "parameters": {
        "idle_rpm": {
            "parameter": "RPM",
            "unit": "RPM",
            "condition": "Motor a temperatura de servicio (>80°C)",
            "min": 780,
            "max": 840,
            "confidence": "OEM_CONFIRMED"
        },
        "coolant_temp": {
            "parameter": "COOLANT_TEMP",
            "unit": "°C",
            "condition": "Termostato abierto / Régimen normal",
            "min": 85,
            "max": 95,
            "confidence": "OEM_CONFIRMED"
        },
        "map_intake_pressure_idle": {
            "parameter": "INTAKE_PRESSURE",
            "unit": "kPa",
            "condition": "Ralentí sin carga a nivel del mar",
            "min": 96,
            "max": 104,
            "confidence": "OEM_CONFIRMED"
        },
        "boost_pressure_relative_max": {
            "parameter": "BOOST_PRESSURE_REL",
            "unit": "bar",
            "condition": "Presión de sobrealimentación relativa máxima en WOT (3ª marcha >2500 RPM)",
            "min": 1.15,
            "max": 1.45,
            "confidence": "OEM_CONFIRMED"
        },
        "dpf_soot_mass_limit": {
            "parameter": "DPF_SOOT_MASS",
            "unit": "g",
            "condition": "Carga máxima de cenizas/hollín estimada pre-bloqueo DPF",
            "warning_threshold": 30.0,
            "critical_threshold": 45.0,
            "max_service_limit": 60.0,
            "confidence": "OEM_CONFIRMED"
        },
        "common_rail_pressure_idle": {
            "parameter": "FUEL_RAIL_PRESSURE",
            "unit": "bar",
            "condition": "Variantes Common Rail (CBAB/CBBB) en ralentí",
            "min": 270,
            "max": 330,
            "confidence": "OEM_CONFIRMED"
        },
        "control_module_voltage": {
            "parameter": "CONTROL_MODULE_VOLTAGE",
            "unit": "V",
            "condition": "Alternador regulado de 140A/180A en funcionamiento",
            "min": 13.8,
            "max": 14.5,
            "confidence": "OEM_CONFIRMED"
        }
    }
}
