"""
Especificación Técnica OEM Confirmada para Volkswagen Passat B6 2.0 TDI (Motor BKP).
Motor: BKP (2.0 TDI 16V 140 CV Sin DPF)
Sistema de inyección: Piezo Bomba-Inyector (Siemens/VDO PPD 1.5)
ECU verificada: Siemens/VDO PPD1.5, referencia 03G 906 018 FG
"""
from typing import Dict, Any

VAG_PASSAT_B6_BKP_SPEC: Dict[str, Any] = {
    "metadata": {
        "manufacturer": "Volkswagen",
        "model": "Passat",
        "generation": "B6 (3C)",
        "engine_code": "BKP",
        "engine_family": "EA188 2.0 TDI 16V",
        "displacement_cc": 1968,
        "valves": 16,
        "power_hp": 140,
        "fuel_type": "Diésel",
        "powertrain_type": "diesel",
        "injection_type": "piezo_pumpe_duese",
        "injection_system": "Piezo-Bomba Inyector Siemens/VDO (PPD 1.5)",
        "ecu_family": "Siemens/VDO PPD1.5 (03G 906 018 FG)",
        "turbocharger": "Garrett GT1749VA VNT",
        "dpf_fitted": False,
        "emissions_standard": "Euro 4 sin DPF",
        "production_years": [2005, 2006, 2007, 2008],
        "market": "EU",
        "source_type": "OEM_CONFIRMED",
        "source_document": "Volkswagen ElsaWin & SSP 352 (The Passat 2006 Electrical System & PPD Injection)"
    },
    "parameters": {
        "idle_rpm": {
            "parameter": "RPM",
            "unit": "RPM",
            "conditions": {"engine_state": "warm"},
            "minimum": 800,
            "target": 830,
            "maximum": 860,
            "source_type": "OEM_CONFIRMED",
            "document": "VW Manual PPD1.5 Diagnostics",
            "section": "MVB 001 Idle Speed Control"
        },
        "coolant_temperature": {
            "parameter": "COOLANT_TEMP",
            "unit": "°C",
            "conditions": {"operating_mode": "normal_driving"},
            "minimum": 85.0,
            "target": 90.0,
            "maximum": 96.0,
            "source_type": "OEM_CONFIRMED",
            "document": "VW Cooling System Group 19",
            "section": "Thermostat Specifications BKP"
        },
        "boost_pressure_relative": {
            "parameter": "BOOST_PRESSURE_REL",
            "unit": "bar",
            "conditions": {"gear": 3, "min_rpm": 2200, "pedal_pct": 100},
            "minimum": 1.15,
            "target": 1.38,
            "maximum": 1.48,
            "source_type": "OEM_CONFIRMED",
            "document": "VW PPD1.5 Technical Diagnostics",
            "section": "MVB 011 Charge Air Pressure"
        }
    }
}
