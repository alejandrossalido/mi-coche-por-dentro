"""
Perfiles de captura predefinidos y personalizados para 'Mi Coche por Dentro'.
Optimiza los PIDs solicitados según el objetivo de la prueba.
"""
from typing import List, Dict, Any

PREDEFINED_PROFILES: Dict[str, Dict[str, Any]] = {
    "COMPLETE_DIAGNOSTIC": {
        "id": "COMPLETE_DIAGNOSTIC",
        "name": "Diagnóstico completo guiado",
        "description": "Recorrido reproducible para evaluar conexión, ralentí, calentamiento, carga y desaceleración.",
        "pids": [
            "RPM", "SPEED", "ENGINE_LOAD", "THROTTLE_POS", "MAF", "INTAKE_PRESSURE",
            "THROTTLE_ACTUATOR", "ACCELERATOR_POS_D", "ACCELERATOR_POS_E", "RELATIVE_ACCEL_POS",
            "COOLANT_TEMP", "INTAKE_TEMP", "OIL_TEMP", "AMBIANT_AIR_TEMP",
            "CATALYST_TEMP_B1S1", "CATALYST_TEMP_B2S1", "CATALYST_TEMP_B1S2", "CATALYST_TEMP_B2S2",
            "BAROMETRIC_PRESSURE", "COMMANDED_EGR", "EGR_ERROR",
            "CONTROL_MODULE_VOLTAGE", "ELM_VOLTAGE", "RUN_TIME", "FUEL_STATUS",
            "SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "FUEL_PRESSURE",
            "FUEL_RAIL_PRESSURE_DIRECT", "FUEL_RAIL_PRESSURE_ABS",
            "COMMANDED_EQUIV_RATIO", "FUEL_INJECT_TIMING", "FUEL_RATE",
            "VAG_OIL_TEMP", "VAG_AMBIENT_TEMP", "VAG_EXHAUST_TEMP_1", "VAG_EXHAUST_TEMP_2",
            "VAG_BAROMETRIC_PRESSURE", "VAG_ACCELERATOR_POSITION", "VAG_EGR_COMMAND", "VAG_EGR_ACTUAL",
            "VAG_RAIL_PRESSURE_REQUESTED", "VAG_RAIL_PRESSURE_ACTUAL",
            "VAG_BOOST_PRESSURE_REQUESTED", "VAG_BOOST_PRESSURE_ACTUAL",
            "VAG_INJECTION_TIMING", "VAG_INJECTION_DURATION", "VAG_INJECTION_DURATION_2",
            "VAG_TORSION_VALUE", "VAG_FUEL_TEMP", "VAG_FUEL_RATE", "VAG_ENGINE_TORQUE",
            "VAG_DRIVER_TORQUE_REQUEST", "VAG_INJECTOR_DEVIATION_1",
            "VAG_INJECTOR_DEVIATION_2", "VAG_INJECTOR_DEVIATION_3", "VAG_INJECTOR_DEVIATION_4",
            "VAG_INJECTOR_STATUS_1", "VAG_INJECTOR_STATUS_2", "VAG_INJECTOR_STATUS_3", "VAG_INJECTOR_STATUS_4",
            "VAG_INJECTOR_SWITCH_TIME_1", "VAG_INJECTOR_SWITCH_TIME_2", "VAG_INJECTOR_SWITCH_TIME_3", "VAG_INJECTOR_SWITCH_TIME_4",
            "VAG_DPF_SOOT_CALCULATED", "VAG_DPF_SOOT_MEASURED", "VAG_DPF_DIFFERENTIAL_PRESSURE",
            "VAG_DPF_DISTANCE_SINCE_REGEN", "VAG_DPF_TIME_SINCE_REGEN", "VAG_DPF_REGEN_STATUS",
            "VAG_ECU_VOLTAGE", "VAG_AIR_MASS_ACTUAL", "VAG_EGR_DUTY_CYCLE",
            "VAG_INJECTION_QUANTITY", "VAG_DPF_SOOT_PERCENT", "VAG_DPF_ASH_MASS"
        ],
        "recommended_duration_sec": 600,
        "steps": [
            {"at_sec": 0, "title": "Ralentí estable", "instruction": "Mantén el coche parado y sin acelerar durante 60 segundos."},
            {"at_sec": 60, "title": "Circulación suave", "instruction": "Inicia la marcha de forma progresiva y evita aceleraciones bruscas."},
            {"at_sec": 180, "title": "Velocidad constante", "instruction": "Mantén una velocidad estable durante aproximadamente 2 minutos."},
            {"at_sec": 300, "title": "Carga controlada", "instruction": "Acelera progresivamente en un lugar seguro, sin superar los límites legales."},
            {"at_sec": 420, "title": "Retención", "instruction": "Suelta el acelerador y deja que el vehículo desacelere con normalidad."},
            {"at_sec": 540, "title": "Ralentí final", "instruction": "Detente con seguridad y mantén 60 segundos de ralentí antes de finalizar."},
        ],
    },
    "COLD_START": {
        "id": "COLD_START",
        "name": "Arranque en Frío",
        "description": "Estudia tensión de batería, arranque, temperatura ambiental/refrigerante y estabilización inicial.",
        "pids": ["CONTROL_MODULE_VOLTAGE", "ELM_VOLTAGE", "VAG_ECU_VOLTAGE", "RPM", "COOLANT_TEMP", "INTAKE_TEMP", "OIL_TEMP", "VAG_OIL_TEMP", "AMBIANT_AIR_TEMP", "VAG_AMBIENT_TEMP", "MAF", "VAG_AIR_MASS_ACTUAL", "INTAKE_PRESSURE", "BAROMETRIC_PRESSURE", "VAG_BAROMETRIC_PRESSURE", "SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "RUN_TIME"],
        "recommended_duration_sec": 300
    },
    "IDLE_STABILITY": {
        "id": "IDLE_STABILITY",
        "name": "Estabilidad de Ralentí",
        "description": "Analiza oscilaciones de RPM, carga calculada y correcciones de mezcla en parado.",
        "pids": ["RPM", "ENGINE_LOAD", "MAF", "VAG_AIR_MASS_ACTUAL", "INTAKE_PRESSURE", "COMMANDED_EGR", "EGR_ERROR", "VAG_EGR_COMMAND", "VAG_EGR_ACTUAL", "VAG_EGR_DUTY_CYCLE", "VAG_INJECTION_QUANTITY", "VAG_INJECTOR_DEVIATION_1", "VAG_INJECTOR_DEVIATION_2", "VAG_INJECTOR_DEVIATION_3", "VAG_INJECTOR_DEVIATION_4", "FUEL_RAIL_PRESSURE_DIRECT", "SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "THROTTLE_POS", "ACCELERATOR_POS_D", "RELATIVE_ACCEL_POS", "VAG_ACCELERATOR_POSITION", "CONTROL_MODULE_VOLTAGE", "VAG_ECU_VOLTAGE", "ELM_VOLTAGE"],
        "recommended_duration_sec": 180
    },
    "CONTROLLED_ACCELERATION": {
        "id": "CONTROLLED_ACCELERATION",
        "name": "Aceleración Controlada",
        "description": "Observa la respuesta dinámica de aire, presión de admisión y carga bajo aceleración.",
        "pids": ["RPM", "SPEED", "THROTTLE_POS", "ACCELERATOR_POS_D", "ACCELERATOR_POS_E", "RELATIVE_ACCEL_POS", "VAG_ACCELERATOR_POSITION", "ENGINE_LOAD", "MAF", "VAG_AIR_MASS_ACTUAL", "INTAKE_PRESSURE", "VAG_BOOST_PRESSURE_REQUESTED", "VAG_BOOST_PRESSURE_ACTUAL", "BAROMETRIC_PRESSURE", "VAG_BAROMETRIC_PRESSURE", "COMMANDED_EGR", "EGR_ERROR", "VAG_EGR_COMMAND", "VAG_EGR_ACTUAL", "FUEL_RAIL_PRESSURE_DIRECT", "FUEL_RAIL_PRESSURE_ABS"],
        "recommended_duration_sec": 120
    },
    "WARMUP_CURVE": {
        "id": "WARMUP_CURVE",
        "name": "Curva de Calentamiento",
        "description": "Estudia el tiempo de subida de temperatura del refrigerante y termostato.",
        "pids": ["COOLANT_TEMP", "INTAKE_TEMP", "OIL_TEMP", "VAG_OIL_TEMP", "AMBIANT_AIR_TEMP", "VAG_AMBIENT_TEMP", "SPEED", "ENGINE_LOAD", "RUN_TIME", "RPM"],
        "recommended_duration_sec": 600
    },
    "CUSTOM": {
        "id": "CUSTOM",
        "name": "Perfil Personalizado",
        "description": "Selección libre de sensores por el usuario.",
        "pids": ["RPM", "SPEED", "COOLANT_TEMP", "INTAKE_PRESSURE"],
        "recommended_duration_sec": 300
    },
    "BATTERY_CHARGING": {
        "id": "BATTERY_CHARGING",
        "name": "Batería y alternador",
        "description": "Comprueba caída de tensión, recuperación y estabilidad del sistema de carga.",
        "pids": ["CONTROL_MODULE_VOLTAGE", "VAG_ECU_VOLTAGE", "ELM_VOLTAGE", "RPM", "ENGINE_LOAD", "RUN_TIME"],
        "recommended_duration_sec": 180,
        "steps": [
            {"at_sec": 0, "title": "Ralentí sin consumidores", "instruction": "Mantén el motor al ralentí con luces y climatización apagados."},
            {"at_sec": 60, "title": "Carga eléctrica", "instruction": "Enciende luces, luneta térmica y ventilador durante un minuto."},
            {"at_sec": 120, "title": "Recuperación", "instruction": "Apaga los consumidores y observa la recuperación de tensión."},
        ],
    },
    "COOLING_SYSTEM": {
        "id": "COOLING_SYSTEM",
        "name": "Termostato y refrigeración",
        "description": "Evalúa velocidad de calentamiento, temperatura máxima y estabilidad térmica.",
        "pids": ["COOLANT_TEMP", "INTAKE_TEMP", "OIL_TEMP", "VAG_OIL_TEMP", "AMBIANT_AIR_TEMP", "VAG_AMBIENT_TEMP", "RPM", "SPEED", "ENGINE_LOAD", "RUN_TIME"],
        "recommended_duration_sec": 600,
        "steps": [
            {"at_sec": 0, "title": "Inicio térmico", "instruction": "Registra la temperatura inicial con el motor frío o templado."},
            {"at_sec": 60, "title": "Calentamiento suave", "instruction": "Circula sin carga elevada hasta alcanzar temperatura de servicio."},
            {"at_sec": 480, "title": "Estabilización", "instruction": "Mantén circulación constante y observa si la temperatura se estabiliza."},
        ],
    },
    "INTAKE_TURBO": {
        "id": "INTAKE_TURBO",
        "name": "Turbo y admisión",
        "description": "Relaciona acelerador, carga, MAF y MAP durante una aceleración segura.",
        "pids": ["RPM", "SPEED", "THROTTLE_POS", "ACCELERATOR_POS_D", "ACCELERATOR_POS_E", "RELATIVE_ACCEL_POS", "VAG_ACCELERATOR_POSITION", "ENGINE_LOAD", "MAF", "VAG_AIR_MASS_ACTUAL", "INTAKE_PRESSURE", "VAG_BOOST_PRESSURE_REQUESTED", "VAG_BOOST_PRESSURE_ACTUAL", "BAROMETRIC_PRESSURE", "VAG_BAROMETRIC_PRESSURE", "COMMANDED_EGR", "EGR_ERROR", "VAG_EGR_COMMAND", "VAG_EGR_ACTUAL", "VAG_EGR_DUTY_CYCLE"],
        "recommended_duration_sec": 180,
        "steps": [
            {"at_sec": 0, "title": "Referencia", "instruction": "Mantén velocidad y carga constantes."},
            {"at_sec": 60, "title": "Aceleración progresiva", "instruction": "Acelera de forma continua en una vía segura y legal."},
            {"at_sec": 120, "title": "Retención", "instruction": "Suelta el acelerador para registrar la respuesta de descarga."},
        ],
    },
    "FUEL_MIXTURE": {
        "id": "FUEL_MIXTURE",
        "name": "Consumo e inyección",
        "description": "Diagnóstico dirigido del consumo: calentamiento, cantidad y duración de inyección, sincronización, inyectores, aire, EGR y turbo.",
        "pids": ["RPM", "SPEED", "COOLANT_TEMP", "VAG_FUEL_TEMP", "VAG_OIL_TEMP", "VAG_ACCELERATOR_POSITION", "MAF", "VAG_AIR_MASS_ACTUAL", "VAG_EGR_COMMAND", "VAG_EGR_ACTUAL", "VAG_EGR_DUTY_CYCLE", "VAG_BOOST_PRESSURE_REQUESTED", "VAG_BOOST_PRESSURE_ACTUAL", "FUEL_STATUS", "SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "FUEL_PRESSURE", "FUEL_RAIL_PRESSURE_DIRECT", "FUEL_RAIL_PRESSURE_ABS", "COMMANDED_EQUIV_RATIO", "FUEL_INJECT_TIMING", "VAG_INJECTION_TIMING", "VAG_INJECTION_DURATION", "VAG_INJECTION_DURATION_2", "VAG_TORSION_VALUE", "FUEL_RATE", "VAG_FUEL_RATE", "VAG_ENGINE_TORQUE", "VAG_DRIVER_TORQUE_REQUEST", "VAG_INJECTION_QUANTITY", "VAG_INJECTOR_DEVIATION_1", "VAG_INJECTOR_DEVIATION_2", "VAG_INJECTOR_DEVIATION_3", "VAG_INJECTOR_DEVIATION_4", "VAG_INJECTOR_STATUS_1", "VAG_INJECTOR_STATUS_2", "VAG_INJECTOR_STATUS_3", "VAG_INJECTOR_STATUS_4", "VAG_INJECTOR_SWITCH_TIME_1", "VAG_INJECTOR_SWITCH_TIME_2", "VAG_INJECTOR_SWITCH_TIME_3", "VAG_INJECTOR_SWITCH_TIME_4"],
        "recommended_duration_sec": 720,
        "steps": [
            {"at_sec": 0, "title": "Ralentí inicial", "instruction": "Con el motor ya caliente, mantén 90 segundos de ralentí sin climatizador ni consumidores importantes."},
            {"at_sec": 90, "title": "Circulación urbana estable", "instruction": "Circula con suavidad durante 3 minutos, evitando aceleraciones bruscas."},
            {"at_sec": 270, "title": "Velocidad constante", "instruction": "Mantén una velocidad legal y estable durante 3 minutos, preferiblemente por encima de 60 km/h."},
            {"at_sec": 450, "title": "Carga progresiva", "instruction": "En una vía segura, acelera progresivamente entre unas 1.500 y 3.000 rpm sin superar los límites legales."},
            {"at_sec": 570, "title": "Retención", "instruction": "Suelta el acelerador y deja desacelerar el vehículo con una marcha engranada."},
            {"at_sec": 630, "title": "Ralentí final", "instruction": "Detente con seguridad y registra 90 segundos de ralentí con el motor caliente."},
        ],
    },
    "EMISSIONS_ITV": {
        "id": "EMISSIONS_ITV",
        "name": "Emisiones / ITV",
        "description": "Captura señales y códigos útiles para evaluar la preparación OBD previa a ITV.",
        "pids": ["RPM", "SPEED", "COOLANT_TEMP", "OIL_TEMP", "VAG_OIL_TEMP", "ENGINE_LOAD", "COMMANDED_EGR", "EGR_ERROR", "VAG_EGR_COMMAND", "VAG_EGR_ACTUAL", "VAG_EGR_DUTY_CYCLE", "CATALYST_TEMP_B1S1", "CATALYST_TEMP_B2S1", "CATALYST_TEMP_B1S2", "CATALYST_TEMP_B2S2", "VAG_EXHAUST_TEMP_1", "VAG_EXHAUST_TEMP_2", "VAG_DPF_DIFFERENTIAL_PRESSURE", "VAG_DPF_SOOT_PERCENT", "VAG_DPF_ASH_MASS", "VAG_DPF_REGEN_STATUS", "FUEL_STATUS", "SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "RUN_TIME"],
        "recommended_duration_sec": 600,
        "steps": [
            {"at_sec": 0, "title": "Motor caliente", "instruction": "Confirma que el motor está a temperatura normal de servicio."},
            {"at_sec": 60, "title": "Ciclo mixto", "instruction": "Combina circulación urbana y velocidad constante de forma segura."},
            {"at_sec": 540, "title": "Lectura final", "instruction": "Detente y realiza el escaneo final de DTC y monitores."},
        ],
    }
}

class CaptureProfileManager:
    @staticmethod
    def list_profiles() -> List[Dict[str, Any]]:
        return list(PREDEFINED_PROFILES.values())

    @staticmethod
    def get_profile(profile_id: str) -> Dict[str, Any]:
        return PREDEFINED_PROFILES.get(profile_id, PREDEFINED_PROFILES["CUSTOM"])
