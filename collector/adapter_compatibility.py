"""Capacidades de adaptadores, separando hardware anunciado y soporte de la app."""
from __future__ import annotations

from typing import Any, Dict


def build_adapter_compatibility(adapter_status: Dict[str, Any]) -> Dict[str, Any]:
    description = " ".join(
        str(value or "")
        for value in (
            adapter_status.get("port"),
            adapter_status.get("protocol"),
        )
    ).lower()
    detected_as_vlinker = "vlinker" in description
    protocol = str(adapter_status.get("protocol") or "")
    can_protocol = any(
        token in protocol.upper()
        for token in ("CAN", "ISO 15765")
    )
    return {
        "adapter_family": "Vgate vLinker FS USB",
        "detected_as_vlinker": detected_as_vlinker,
        "connected": bool(adapter_status.get("is_connected")),
        "active_port": adapter_status.get("port"),
        "active_protocol": adapter_status.get("protocol"),
        "hardware": [
            {
                "capability": "Conexión USB serie",
                "status": "supported",
                "detail": "El vLinker FS se comunica por USB y aparece como puerto COM.",
            },
            {
                "capability": "OBD-II genérico",
                "status": "supported",
                "detail": "Compatible con vehículos de 12/24 V que cumplen OBD-II.",
            },
            {
                "capability": "HS-CAN y MS-CAN",
                "status": "supported",
                "detail": "El hardware incorpora conmutación electrónica automática para buses Ford.",
            },
        ],
        "application": [
            {
                "capability": "PIDs genéricos en tiempo real",
                "status": "ready",
                "detail": "Lectura, validación y guardado de señales OBD estándar.",
            },
            {
                "capability": "DTC y freeze frame estándar",
                "status": "ready",
                "detail": "Lectura real de Modo 03 y parámetros disponibles de Modo 02.",
            },
            {
                "capability": "Modo 06",
                "status": "ready" if can_protocol else "requires_vehicle",
                "detail": (
                    "Se consultan únicamente monitores que la ECU declara compatibles; "
                    "python-OBD limita el Modo 06 a protocolos CAN."
                ),
            },
            {
                "capability": "PIDs OEM / Modo 22",
                "status": "not_configured",
                "detail": (
                    "No hay paquetes OEM verificados instalados. La aplicación no "
                    "inventará definiciones propietarias."
                ),
            },
            {
                "capability": "Programación de módulos",
                "status": "out_of_scope",
                "detail": (
                    "El adaptador puede utilizarse con software especializado, pero "
                    "esta aplicación es de captura y diagnóstico y no programa ECUs."
                ),
            },
        ],
        "sources": [
            {
                "label": "Ficha oficial Vgate vLinker FS USB",
                "url": "https://vgatemall.com/products-detail/i-19/",
            }
        ],
        "message": (
            "La compatibilidad final depende del vehículo, del protocolo negociado y "
            "de los PIDs que cada ECU declare y responda realmente."
        ),
    }
