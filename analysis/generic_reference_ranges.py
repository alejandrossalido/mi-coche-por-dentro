"""
Reglas Genéricas Conservadoras de Ingeniería automotriz para vehículos sin especificación OEM confirmada.
Categoría de Confianza: GENERIC_ENGINEERING_RANGE
"""
from typing import Dict, Any

GENERIC_CONSERVATIVE_RANGES: Dict[str, Dict[str, Any]] = {
    "diesel": {
        "confidence_tier": "GENERIC_ENGINEERING_RANGE",
        "description": "Rangos genéricos conservadores para motores turbodiésel de turismos.",
        "parameters": {
            "idle_rpm": {"min": 700, "max": 900, "unit": "RPM", "confidence": "GENERIC_ENGINEERING_RANGE"},
            "coolant_temp": {"min": 75, "max": 100, "unit": "°C", "confidence": "GENERIC_ENGINEERING_RANGE"},
            "boost_pressure_relative": {"min": 0.8, "max": 1.6, "unit": "bar", "confidence": "GENERIC_ENGINEERING_RANGE"},
            "battery_voltage": {"min": 13.5, "max": 14.8, "unit": "V", "confidence": "GENERIC_ENGINEERING_RANGE"}
        }
    },
    "gasoline": {
        "confidence_tier": "GENERIC_ENGINEERING_RANGE",
        "description": "Rangos genéricos conservadores para motores de gasolina de turismos.",
        "parameters": {
            "idle_rpm": {"min": 650, "max": 900, "unit": "RPM", "confidence": "GENERIC_ENGINEERING_RANGE"},
            "coolant_temp": {"min": 80, "max": 105, "unit": "°C", "confidence": "GENERIC_ENGINEERING_RANGE"},
            "stft_pct": {"min": -10.0, "max": 10.0, "unit": "%", "confidence": "GENERIC_ENGINEERING_RANGE"},
            "ltft_pct": {"min": -10.0, "max": 10.0, "unit": "%", "confidence": "GENERIC_ENGINEERING_RANGE"},
            "battery_voltage": {"min": 13.5, "max": 14.8, "unit": "V", "confidence": "GENERIC_ENGINEERING_RANGE"}
        }
    },
    "bev": {
        "confidence_tier": "GENERIC_ENGINEERING_RANGE",
        "description": "Rangos genéricos conservadores para vehículos eléctricos de batería (BEV).",
        "parameters": {
            "hv_battery_voltage": {"min": 250.0, "max": 450.0, "unit": "V", "confidence": "GENERIC_ENGINEERING_RANGE"},
            "hv_cell_temp_c": {"min": -20.0, "max": 55.0, "unit": "°C", "confidence": "GENERIC_ENGINEERING_RANGE"},
            "aux_battery_voltage": {"min": 12.0, "max": 16.0, "unit": "V", "confidence": "GENERIC_ENGINEERING_RANGE"}
        }
    }
}

def get_generic_reference_ranges(powertrain_type: str = "gasoline") -> Dict[str, Any]:
    """Retorna las tolerancias genéricas conservadoras marcadas explícitamente como GENERIC_ENGINEERING_RANGE."""
    pt = powertrain_type.lower()
    if "diesel" in pt:
        return GENERIC_CONSERVATIVE_RANGES["diesel"]
    elif "electric" in pt or "bev" in pt:
        return GENERIC_CONSERVATIVE_RANGES["bev"]
    else:
        return GENERIC_CONSERVATIVE_RANGES["gasoline"]
