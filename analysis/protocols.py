"""
Módulo de protocolos de prueba repetibles para 'Mi Coche por Dentro'.
Proporciona instrucciones normalizadas y listas de verificación antes de iniciar capturas.
"""
from typing import Dict, Any

TEST_PROTOCOLS: Dict[str, Dict[str, Any]] = {
    "COLD_START": {
        "title": "Protocolo de Arranque en Frío",
        "checklist": [
            "El vehículo debe llevar al menos 6 horas sin arrancar (motor a temperatura ambiente).",
            "Conectar el OBDLink LX y dar al contacto ANTES de girar la llave para arrancar.",
            "Iniciar la captura de sesión en la aplicación.",
            "Arrancar el motor sin accionar el acelerador.",
            "Mantener el vehículo al ralentí hasta que las RPM se estabilicen."
        ]
    },
    "WARMUP": {
        "title": "Protocolo de Calentamiento y Termostato",
        "checklist": [
            "Iniciar la prueba desde temperatura ambiente o tibia.",
            "Circular en un trayecto mixto (urbano o carretera secundaria) sin aceleraciones bruscas.",
            "Registrar hasta que la temperatura alcance ~90°C y se mantenga estable.",
            "Anotar la temperatura exterior estimada."
        ]
    },
    "ACCELERATION": {
        "title": "Protocolo de Aceleración en Lugar Seguro",
        "checklist": [
            "Comprobar que el motor esté a temperatura normal de servicio (80-90°C).",
            "Realizar la prueba con un acompañante manejando el portátil (NUNCA el conductor).",
            "En 3ª velocidad desde 1500 RPM, acelerar a fondo hasta 4000 RPM en lugar seguro.",
            "Pulsar el botón 'PÉRDIDA POTENCIA' o 'TIRÓN' inmediatamente si se observa una anomalía."
        ]
    }
}

class ProtocolManager:
    @staticmethod
    def get_protocol(protocol_id: str) -> Dict[str, Any]:
        return TEST_PROTOCOLS.get(protocol_id, {
            "title": "Protocolo Estándar",
            "checklist": ["Verificar conexión del adaptador.", "Arrancar la sesión antes de iniciar la marcha."]
        })
