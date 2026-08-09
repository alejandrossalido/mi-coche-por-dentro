"""
Reglas de Coherencia Semántica y Física de Telemetría (PhysicalCoherenceValidator).
Evalúa la aplicabilidad semántica exacta de las señales según motorización y sistema de alimentación.
"""
from typing import Dict, Any, List

class PhysicalCoherenceValidator:
    NON_APPLICABLE_SIGNALS_BY_POWERTRAIN = {
        "bev": [
            "ENGINE_RPM",
            "ENGINE_COOLANT_TEMP",
            "ENGINE_OIL_TEMP",
            "STFT",
            "LTFT",
            "SHORT_FUEL_TRIM_1",
            "LONG_FUEL_TRIM_1",
            "EGR_DUTY",
            "DPF_SOOT_MASS",
            "GPF_SOOT_LOAD",
            "EXHAUST_GAS_TEMP",
            "TURBO_BOOST_REL",
            "INTAKE_MANIFOLD_PRESSURE"
        ],
        "diesel": [
            "STFT",
            "LTFT",
            "SHORT_FUEL_TRIM_1",
            "LONG_FUEL_TRIM_1",
            "SPARK_ADVANCE",
            "GPF_SOOT_LOAD"
        ],
        "gasoline_pfi": [
            "FUEL_RAIL_PRESSURE_HIGH",
            "DPF_SOOT_MASS",
            "EGR_DUTY"
        ],
        "gasoline_gdi": [
            "DPF_SOOT_MASS"
        ]
    }

    @classmethod
    def validate_pid_relevance(cls, pid_name: str, powertrain_type: str, injection_type: str = "") -> bool:
        """Determina si un PID es físicamente aplicable y semánticamente coherente."""
        pt = powertrain_type.lower()
        pid_upper = pid_name.upper()

        if "bev" in pt or "electric" in pt:
            # En BEV, las revoluciones de la unidad motriz (DRIVE_UNIT_RPM) y temps de refrigeración de batería/inversor SÍ son válidas
            if pid_upper in ("DRIVE_UNIT_FRONT_RPM", "DRIVE_UNIT_REAR_RPM", "MOTOR_RPM", "BATTERY_COOLANT_TEMP", "INVERTER_COOLANT_TEMP"):
                return True
            return pid_upper not in cls.NON_APPLICABLE_SIGNALS_BY_POWERTRAIN["bev"]

        elif "diesel" in pt:
            # En Diésel, la sonda lambda de escape (EXHAUST_LAMBDA_RATIO) SÍ es válida, pero STFT/LTFT de mezcla estequiométrica no
            if pid_upper in ("EXHAUST_LAMBDA_RATIO", "WIDEBAND_LAMBDA", "LAMBDA"):
                return True
            return pid_upper not in cls.NON_APPLICABLE_SIGNALS_BY_POWERTRAIN["diesel"]

        else: # Gasolina
            if "direct" in injection_type.lower() or "gdi" in injection_type.lower() or "tsi" in injection_type.lower():
                return pid_upper not in cls.NON_APPLICABLE_SIGNALS_BY_POWERTRAIN["gasoline_gdi"]
            return pid_upper not in cls.NON_APPLICABLE_SIGNALS_BY_POWERTRAIN["gasoline_pfi"]

    @classmethod
    def filter_coherent_signals(cls, signals: Dict[str, Any], powertrain_type: str, injection_type: str = "") -> Dict[str, Any]:
        """Filtra y devuelve únicamente las señales semánticamente coherentes."""
        return {
            pid: val for pid, val in signals.items()
            if cls.validate_pid_relevance(pid, powertrain_type, injection_type)
        }
