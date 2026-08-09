"""Catálogo de lectura para la ECU Siemens/VDO PPD1.5 03G 906 018 FG.

El catálogo describe únicamente bloques de medida KWP2000 de solo lectura.
Que un campo figure aquí significa que está documentado para la familia de
centralitas; solo se considera disponible cuando la ECU concreta lo devuelve.
"""

from __future__ import annotations

from typing import Dict, Tuple


# Título del bloque y nombres de sus cuatro posiciones documentadas. Una cadena
# vacía representa una posición que la documentación de la familia no nombra.
DOCUMENTED_GROUPS: Dict[int, Tuple[str, Tuple[str, str, str, str]]] = {
    1: ("Cantidad de inyección", ("Revoluciones del motor", "Cantidad de inyección", "Duración de inyección solicitada", "Temperatura del refrigerante")),
    2: ("Ralentí", ("Revoluciones del motor", "Posición del pedal del acelerador", "Estado de funcionamiento", "Temperatura del refrigerante")),
    3: ("Recirculación de gases EGR", ("Revoluciones del motor", "Masa de aire EGR solicitada", "Masa de aire EGR real", "Mando de la EGR")),
    4: ("Sistema inyector-bomba", ("Revoluciones del motor", "Inicio de inyección solicitado", "Duración de inyección solicitada", "Valor de torsión de la distribución")),
    5: ("Condiciones del último arranque", ("Revoluciones del motor", "Par de arranque", "Sincronización de arranque", "Temperatura del refrigerante")),
    6: ("Control de crucero", ("Velocidad real", "Supervisión de pedales", "Posición del pedal del acelerador", "Supervisión de mandos")),
    7: ("Temperaturas", ("Temperatura del combustible", "", "Temperatura del aire de admisión", "Temperatura del refrigerante")),
    8: ("Límites de inyección I", ("Revoluciones del motor", "Par solicitado por el conductor", "Límite de par", "Límite de humo")),
    9: ("Límites de inyección II", ("Revoluciones del motor", "Par solicitado por el control de crucero", "Límite de la transmisión", "Restricción de par")),
    10: ("Control de sobrealimentación I", ("Masa de aire real", "Presión atmosférica", "Presión de turbo real", "Posición del pedal del acelerador")),
    11: ("Control de sobrealimentación II", ("Revoluciones del motor", "Presión de turbo solicitada", "Presión de turbo real", "Mando del turbo")),
    12: ("Precalentamiento", ("Estado de calentadores", "Tiempo de precalentamiento", "Tensión de alimentación", "Temperatura del refrigerante")),
    13: ("Equilibrado de inyectores", ("Corrección del inyector 1", "Corrección del inyector 2", "Corrección del inyector 3", "Corrección del inyector 4")),
    15: ("Consumo y par", ("Revoluciones del motor", "Par calculado del motor", "Caudal de combustible", "Par solicitado por el conductor")),
    16: ("Calefacción auxiliar y alternador", ("Carga del alternador", "", "", "Tensión de alimentación")),
    17: ("Disponibilidad EOBD", ("Estado EOBD A", "Estado EOBD B", "Estado EOBD C", "Estado EOBD D")),
    18: ("Estado eléctrico de inyectores", ("Estado del inyector 1", "Estado del inyector 2", "Estado del inyector 3", "Estado del inyector 4")),
    20: ("Límites de par solicitados por ABS", ("Revoluciones del motor", "Par del motor", "Límite ASR", "Límite MSR")),
    21: ("Estado del bus CAN del tren motriz", ("Electrónica del motor", "Electrónica de la transmisión", "Electrónica de frenos", "Control de estabilidad ESP")),
    22: ("Motivos de desconexión", ("Desconexión del control de crucero", "Mandos del control de crucero", "Desconexión del control de turbo", "Desconexión del climatizador")),
    23: ("Conmutación de los inyectores", ("Tiempo de conmutación del inyector 1", "Tiempo de conmutación del inyector 2", "Tiempo de conmutación del inyector 3", "Tiempo de conmutación del inyector 4")),
    25: ("Arranque y salida", ("Revoluciones del motor", "Estado del terminal 50", "Estado del motor", "Motivo de salida abortada")),
    26: ("Suma de comprobación", ("Suma de comprobación", "", "", "")),
    27: ("Limitador de velocidad", ("", "", "Velocidad", "Límite de velocidad")),
    28: ("Sensores del pedal del acelerador", ("Sensor 1 del pedal", "Sensor 2 del pedal", "Estado de funcionamiento", "Posición calculada del pedal")),
    29: ("Aceite del motor", ("Temperatura del aceite", "Nivel de aceite", "Índice de desgaste", "Índice de hollín")),
    30: ("Control de oxígeno I", ("Calibración de la sonda", "Tensión de compensación", "Concentración de oxígeno", "Estado de regulación")),
    31: ("Control de oxígeno II", ("Caudal total de aire", "Control de calefacción", "Señal de temperatura", "Señal de tensión de oxígeno")),
    32: ("Control de oxígeno III", ("Caudal total de aire", "Temperatura exterior", "Presión de aire de la sonda", "Señal de tensión de oxígeno")),
    33: ("Control de oxígeno IV", ("Revoluciones del motor", "Temperatura de escape", "Contrapresión de escape", "Caudal másico de escape")),
    34: ("Diagnóstico de la sonda de oxígeno", ("Señal de oxígeno", "Electrónica de la sonda", "Plausibilidad de la sonda", "Diagnóstico de la sonda")),
    40: ("Sonda de oxígeno", ("Revoluciones del motor", "Cantidad de inyección", "Estado de calefacción de la sonda", "Valor de oxígeno")),
    41: ("EGR y colector de admisión I", ("Posición solicitada del colector", "Posición solicitada de EGR", "Posición real de EGR", "Mando de EGR")),
    42: ("EGR y colector de admisión II", ("Aprendizaje de cierre de EGR", "Adaptación de EGR", "Posición real del colector", "Posición real de EGR")),
    43: ("Compuerta de sobrealimentación", ("Mando de la compuerta", "Posición de la compuerta", "", "")),
    44: ("Colector y enfriador EGR", ("Revoluciones del motor", "Masa de aire real", "Enfriador EGR", "Válvula del colector")),
    45: ("Presión y masa de admisión", ("", "Presión del volumen de admisión", "Masa de aire real", "Presión de turbo real")),
    46: ("Colector de admisión I", ("Posición solicitada", "Regulador de posición", "Posición real", "Mando del colector")),
    47: ("Colector de admisión II", ("Aprendizaje de posición cerrada", "Aprendizaje de posición abierta", "Mando del colector", "Posición real")),
    51: ("Reconocimiento de giro", ("Revoluciones del motor", "Velocidad del árbol de levas", "Sincronización de arranque", "Corte de la secuencia de inyección")),
    62: ("Temperaturas de refrigeración", ("Refrigerante a la salida del motor", "Refrigerante a la salida del radiador", "Temperatura ambiente", "Temperatura del aire de admisión")),
    63: ("Refrigeración y climatización", ("Presión del refrigerante del climatizador", "Par de carga del climatizador", "Petición de refrigeración", "Desconexión del climatizador")),
    64: ("Refrigeración del motor", ("Temperatura del refrigerante", "Refrigerante a la salida del radiador", "Mando del ventilador 1", "")),
    67: ("DPF: temperaturas y presión", ("Temperatura antes del turbo", "Temperatura en el DPF", "Presión diferencial del DPF", "Compensación de presión diferencial")),
    68: ("DPF: hollín y ceniza", ("Carga de hollín", "Masa de ceniza", "Aprendizaje de ceniza", "")),
    69: ("DPF: estado de regeneración I", ("Estado de regeneración 1", "", "", "Estado de regeneración 4")),
    70: ("DPF: estado de regeneración II", ("Estado de regeneración", "Tiempo de regeneración", "Regeneraciones fallidas", "Regeneraciones correctas")),
    71: ("DPF: postinyección", ("Revoluciones del motor", "Cantidad de postinyección", "Habilitación de la inyección", "Periodo de alimentación")),
    73: ("DPF: datos desde regeneración", ("Consumo desde la regeneración", "Distancia desde la regeneración", "Tiempo desde la regeneración", "")),
    74: ("DPF: emisiones III", ("Revoluciones del motor", "Temperatura antes del turbo", "Valor de oxígeno", "Compensación de inyección")),
    75: ("DPF: emisiones IV", ("Temperatura antes del turbo", "Temperatura antes del DPF", "Carga de hollín", "Temperatura después del DPF")),
    80: ("Identificación avanzada de la ECU I", ("", "", "", "")),
    81: ("Identificación avanzada de la ECU II", ("Número VIN", "Identificador del inmovilizador", "", "")),
    82: ("Identificación avanzada de la ECU III", ("", "", "", "")),
    86: ("Datos EOBD I", ("", "", "", "")),
    87: ("Datos EOBD II", ("", "", "", "")),
    89: ("Datos EOBD III", ("", "", "", "")),
    90: ("EOBD de la EGR I", ("Revoluciones del motor", "Cantidad de inyección", "EGR solicitada", "Estado de desviación")),
    91: ("EOBD de la EGR II", ("", "", "", "")),
    110: ("Control del motor de arranque I", ("Estado del terminal 50", "", "", "")),
    111: ("Control del motor de arranque II", ("", "Condición de corte 1", "Condición de corte 2", "Tensión de servicios")),
    125: ("Comunicación CAN I", ("Transmisión", "Electrónica de frenos", "Cuadro de instrumentos", "Airbag")),
    126: ("Comunicación CAN II", ("Climatizador", "", "Central eléctrica", "")),
    127: ("Comunicación CAN III", ("", "", "", "Electrónica del volante")),
    128: ("Comunicación CAN IV", ("Pasarela CAN", "", "", "")),
    225: ("Tiempo de espera CAN I", ("Transmisión", "Electrónica de frenos", "Cuadro de instrumentos", "Airbag")),
    226: ("Tiempo de espera CAN II", ("Climatizador", "", "Central eléctrica", "")),
    227: ("Tiempo de espera CAN III", ("", "", "Electrónica del volante", "")),
    228: ("Tiempo de espera CAN IV", ("Pasarela CAN", "", "", "")),
}


def category_for_group(group: int) -> str:
    if group in {1, 4, 8, 9, 13, 15, 18, 23, 30, 31, 32, 33, 34, 40, 67, 68, 69, 70, 71, 73, 74, 75, 90, 91}:
        return "Combustible, mezcla y emisiones"
    if group in {3, 10, 11, 41, 42, 43, 44, 45, 46, 47}:
        return "Admisión, EGR y turbo"
    if group in {7, 29, 62, 63, 64}:
        return "Temperaturas y refrigeración"
    if group in {12, 16, 17, 21, 22, 26, 80, 81, 82, 86, 87, 89, 110, 111, 125, 126, 127, 128, 225, 226, 227, 228}:
        return "Sistema eléctrico, ECU y comunicaciones"
    return "Motor, marcha y mandos"


def documented_field_count() -> int:
    return sum(sum(bool(label) for label in fields) for _, fields in DOCUMENTED_GROUPS.values())


__all__ = ["DOCUMENTED_GROUPS", "category_for_group", "documented_field_count"]
