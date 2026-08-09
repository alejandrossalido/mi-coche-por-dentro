"""
Especificación Técnica OEM Confirmada para Tesla Model 3 (2024+ Highland BEV).
Arquitectura: 370V Nominal High Voltage System (Batería LFP o NMC según variante RWD / Long Range / Performance)
Baja Tensión: Sistema Auxiliar que requiere detección entre 16.0V Li-Ion (PCS) y 14.4V AGM según configuración de fábrica.
"""
from typing import Dict, Any

TESLA_MODEL3_HIGHLAND_SPEC: Dict[str, Any] = {
    "metadata": {
        "manufacturer": "Tesla",
        "model": "Model 3",
        "generation": "Highland (2024+)",
        "powertrain_type": "bev",
        "fuel_type": "Eléctrico",
        "hv_architecture_nominal_voltage": 370.0,
        "lv_system_variants": [16.0, 14.4],
        "lv_variant_status": "detect_required",
        "thermal_system": "Octovalve Heat Pump & Cell Thermal Conditioning",
        "emissions_standard": "Zero Emissions (BEV)",
        "production_years": [2024, 2025, 2026],
        "market": "Global",
        "source_type": "OEM_CONFIRMED",
        "source_document": "Tesla Model 3 2024+ Official Service Manual (GUID-4E657067-4201-4B84-9463-D05E88007436)"
    },
    "parameters": {
        "hv_battery_voltage": {
            "parameter": "HV_BATTERY_VOLTAGE",
            "unit": "V",
            "conditions": {"soc_range_pct": [10.0, 100.0]},
            "minimum": 320.0,
            "nominal": 370.0,
            "maximum": 405.0,
            "source_type": "OEM_CONFIRMED",
            "document": "Tesla Service Manual - Electrical System & HV Battery",
            "section": "High Voltage Pack Nominal Operating Range"
        },
        "hv_cell_operating_temp_driving": {
            "parameter": "HV_CELL_TEMP_DRIVING",
            "unit": "°C",
            "conditions": {"operating_mode": "normal_or_sport_driving"},
            "minimum": -30.0,
            "target": 30.0,
            "maximum": 60.0,
            "source_type": "OEM_CONFIRMED",
            "document": "Tesla Service Manual - Battery Thermal Conditioning",
            "section": "HV Cell Thermal Limits in Driving Mode"
        },
        "hv_cell_operating_temp_supercharging": {
            "parameter": "HV_CELL_TEMP_SUPERCHARGING",
            "unit": "°C",
            "conditions": {"operating_mode": "preconditioned_supercharging"},
            "minimum": 35.0,
            "target": 45.0,
            "maximum": 55.0,
            "source_type": "OEM_CONFIRMED",
            "document": "Tesla Service Manual - DC Fast Charging Thermal Strategy",
            "section": "Supercharger Preconditioning Target Temperature"
        },
        "drive_unit_motor_temp_max": {
            "parameter": "REAR_DRIVE_UNIT_MOTOR_TEMP",
            "unit": "°C",
            "conditions": {"operating_mode": "continuous_load"},
            "warning_threshold": 85.0,
            "critical_threshold": 105.0,
            "source_type": "OEM_CONFIRMED",
            "document": "Tesla Drive Unit Diagnostics - Inverter & Motor Stator",
            "section": "Stator Thermal Limit Pre-Derating"
        }
    }
}
