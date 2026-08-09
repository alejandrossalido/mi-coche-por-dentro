"""
Fichas Técnicas y Especificaciones Oficiales de Fábrica para 'Mi Coche por Dentro'.
Almacena tolerancias y valores de referencia de fábrica para Opel Vectra, Passat B6, Mazda 3, Tesla Model 3 y vehículos personalizados.
"""
from typing import Dict, Any, Optional

FACTORY_SPECS: Dict[str, Dict[str, Any]] = {
    "vectra": {
        "display_name": "Opel Vectra (2.0 Turbo / 1.8 16V)",
        "make": "Opel",
        "model": "Vectra",
        "year": 2006,
        "engine": "2.0 Turbo / 1.8 16V",
        "fuel_type": "Gasolina",
        "powertrain_type": "gasoline",
        "specs": {
            "idle_rpm": {"min": 750, "max": 850, "unit": "RPM"},
            "max_rpm": {"max": 6500, "unit": "RPM"},
            "boost_pressure_bar": {"min": 0.55, "max": 0.85, "unit": "bar"},
            "coolant_temp_c": {"min": 85, "max": 98, "unit": "°C"},
            "oil_temp_c": {"min": 85, "max": 105, "unit": "°C"},
            "intake_pressure_kpa": {"idle_min": 30, "idle_max": 40, "wot_max": 185, "unit": "kPa"},
            "stft_pct": {"min": -5.0, "max": 5.0, "unit": "%"},
            "ltft_pct": {"min": -5.0, "max": 5.0, "unit": "%"},
            "lambda_ratio": {"min": 0.98, "max": 1.02, "unit": "λ"},
            "battery_voltage": {"min": 13.8, "max": 14.5, "unit": "V"}
        },
        "description": "Ficha Técnica Oficial: Motor gasolina turbo de 4 cilindros. Tolerancia estricta de mezcla estequiométrica Lambda 1.00."
    },
    "passat_b6": {
        "display_name": "Volkswagen Passat B6 (2.0 TDI)",
        "make": "Volkswagen",
        "model": "Passat B6",
        "year": 2008,
        "engine": "2.0 TDI (Pump Duse / Common Rail)",
        "fuel_type": "Diésel",
        "powertrain_type": "diesel",
        "specs": {
            "idle_rpm": {"min": 780, "max": 830, "unit": "RPM"},
            "max_rpm": {"max": 4500, "unit": "RPM"},
            "boost_pressure_bar": {"min": 1.1, "max": 1.45, "unit": "bar"},
            "coolant_temp_c": {"min": 87, "max": 95, "unit": "°C"},
            "rail_pressure_bar": {"idle_min": 280, "idle_max": 350, "wot_max": 1600, "unit": "bar"},
            "intake_pressure_kpa": {"idle_min": 95, "idle_max": 105, "wot_max": 245, "unit": "kPa"},
            "egr_duty_pct": {"min": 0, "max": 85, "unit": "%"},
            "dpf_soot_load_g": {"max_allowed": 30.0, "critical": 45.0, "unit": "g"},
            "battery_voltage": {"min": 13.8, "max": 14.4, "unit": "V"}
        },
        "description": "Ficha Técnica Oficial: Motor diésel turboalimentado 2.0 TDI. Soplado máximo nominal de turbo entre 1.20 bar y 1.45 bar."
    },
    "mazda_3": {
        "display_name": "Mazda 3 (2.0 Skyactiv-G)",
        "make": "Mazda",
        "model": "Mazda 3",
        "year": 2015,
        "engine": "2.0 Skyactiv-G (Alta Compresión 14:1)",
        "fuel_type": "Gasolina",
        "powertrain_type": "gasoline",
        "specs": {
            "idle_rpm": {"min": 620, "max": 720, "unit": "RPM"},
            "max_rpm": {"max": 6800, "unit": "RPM"},
            "coolant_temp_c": {"min": 82, "max": 93, "unit": "°C"},
            "maf_g_s": {"idle_min": 2.0, "idle_max": 3.2, "unit": "g/s"},
            "intake_pressure_kpa": {"idle_min": 28, "idle_max": 36, "unit": "kPa"},
            "stft_pct": {"min": -3.5, "max": 3.5, "unit": "%"},
            "ltft_pct": {"min": -3.5, "max": 3.5, "unit": "%"},
            "lambda_ratio": {"min": 0.99, "max": 1.01, "unit": "λ"},
            "battery_voltage": {"min": 13.9, "max": 14.6, "unit": "V"}
        },
        "description": "Ficha Técnica Oficial: Motor atmosférico de inyección directa de alta compresión (14:1). Ralentí ultraestable y baja varianza MAF."
    },
    "tesla_model3": {
        "display_name": "Tesla Model 3 (2025 Highland BEV)",
        "make": "Tesla",
        "model": "Model 3 Highland",
        "year": 2025,
        "engine": "Dual Motor / RWD (100% Eléctrico)",
        "fuel_type": "Eléctrico",
        "powertrain_type": "bev",
        "specs": {
            "hv_battery_voltage": {"min": 350.0, "max": 405.0, "unit": "V"},
            "hv_cell_temp_c": {"min": 20.0, "max": 45.0, "unit": "°C"},
            "aux_battery_voltage": {"min": 13.5, "max": 15.5, "unit": "V (Li-Ion 16V)"},
            "motor_temp_c": {"max": 85.0, "unit": "°C"},
            "inverter_temp_c": {"max": 75.0, "unit": "°C"},
            "soh_pct": {"min": 85.0, "max": 100.0, "unit": "%"}
        },
        "description": "Ficha Técnica Oficial: Vehículo 100% Eléctrico de alta tensión (400V). Monitorización de balanceado de celdas y circuitos térmicos."
    }
}

def get_factory_spec(vehicle_id: str, make: str = "", model: str = "", powertrain_type: str = "gasoline") -> Dict[str, Any]:
    """Obtiene la ficha técnica oficial del vehículo o genera una plantilla dinámica de fábrica para coches nuevos de amigos."""
    if vehicle_id in FACTORY_SPECS:
        return FACTORY_SPECS[vehicle_id]
    
    # Generación automática de Ficha Técnica estándar para coches nuevos añadidos
    powertrain = powertrain_type.lower()
    if "electric" in powertrain or "bev" in powertrain:
        specs = {
            "hv_battery_voltage": {"min": 320.0, "max": 420.0, "unit": "V"},
            "hv_cell_temp_c": {"min": 15.0, "max": 45.0, "unit": "°C"},
            "aux_battery_voltage": {"min": 12.5, "max": 14.8, "unit": "V"}
        }
    elif "diesel" in powertrain:
        specs = {
            "idle_rpm": {"min": 750, "max": 850, "unit": "RPM"},
            "boost_pressure_bar": {"min": 1.0, "max": 1.5, "unit": "bar"},
            "coolant_temp_c": {"min": 85, "max": 96, "unit": "°C"},
            "battery_voltage": {"min": 13.8, "max": 14.5, "unit": "V"}
        }
    else:
        specs = {
            "idle_rpm": {"min": 700, "max": 850, "unit": "RPM"},
            "coolant_temp_c": {"min": 85, "max": 98, "unit": "°C"},
            "stft_pct": {"min": -5.0, "max": 5.0, "unit": "%"},
            "ltft_pct": {"min": -5.0, "max": 5.0, "unit": "%"},
            "battery_voltage": {"min": 13.8, "max": 14.5, "unit": "V"}
        }
        
    return {
        "display_name": f"{make} {model}".strip() or "Vehículo Personalizado",
        "make": make,
        "model": model,
        "powertrain_type": powertrain_type,
        "specs": specs,
        "description": f"Ficha Técnica Generada por IA para {make} {model}. Tolerancias calculadas para motor {powertrain_type}."
    }
