"""Descripciones en castellano para códigos DTC genéricos frecuentes."""

from typing import Optional


DTC_DESCRIPTIONS_ES = {
    "P0100": "Fallo en el circuito del caudalímetro de aire.",
    "P0101": "Rango o funcionamiento incorrecto del caudalímetro de aire.",
    "P0102": "Señal baja del caudalímetro de aire.",
    "P0103": "Señal alta del caudalímetro de aire.",
    "P0115": "Fallo en el circuito del sensor de temperatura del refrigerante.",
    "P0128": "La temperatura del refrigerante está por debajo de la regulada por el termostato.",
    "P0171": "Mezcla demasiado pobre en el banco 1.",
    "P0172": "Mezcla demasiado rica en el banco 1.",
    "P0200": "Fallo en el circuito de los inyectores.",
    "P0234": "Presión de sobrealimentación excesiva.",
    "P0299": "Presión de sobrealimentación insuficiente.",
    "P0300": "Fallos de combustión aleatorios o en varios cilindros.",
    "P0301": "Fallo de combustión detectado en el cilindro 1.",
    "P0302": "Fallo de combustión detectado en el cilindro 2.",
    "P0303": "Fallo de combustión detectado en el cilindro 3.",
    "P0304": "Fallo de combustión detectado en el cilindro 4.",
    "P0400": "Fallo en el sistema de recirculación de gases de escape.",
    "P0401": "Caudal insuficiente en la recirculación de gases de escape.",
    "P0402": "Caudal excesivo en la recirculación de gases de escape.",
    "P0420": "Eficiencia del catalizador por debajo del umbral en el banco 1.",
    "P0562": "Tensión del sistema demasiado baja.",
    "P0563": "Tensión del sistema demasiado alta.",
}


def describe_dtc_in_spanish(code: str, original: Optional[str] = None) -> str:
    """Devuelve una descripción castellana y evita exponer textos ingleses sin traducir."""
    normalized = str(code or "").strip().upper()
    if normalized in DTC_DESCRIPTIONS_ES:
        return DTC_DESCRIPTIONS_ES[normalized]
    if original and not any("a" <= char.lower() <= "z" for char in original):
        return original
    return "Código de diagnóstico registrado por la ECU; descripción específica no disponible en castellano."
