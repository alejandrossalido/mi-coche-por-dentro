"""Catálogo exhaustivo y extensible de métricas candidatas por vehículo.

Una entrada en este catálogo significa "debe investigarse", no "el coche la
soporta". La evidencia real guardada en ``vehicle_capabilities`` prevalece y
decide si queda confirmada, pendiente, no disponible o no aplicable.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List

from collector.pid_discovery import STANDARD_PIDS, obd
from collector.vag_bkp_catalog import category_for_group
from collector.vag_kwp2000 import ALL_KWP_SIGNALS


MetricRow = Dict[str, Any]
CatalogProvider = Callable[[Dict[str, Any]], Iterable[MetricRow]]


def _standard_category(pid_name: str) -> str:
    if pid_name in {"RPM", "SPEED", "ENGINE_LOAD", "RUN_TIME", "THROTTLE_POS", "THROTTLE_ACTUATOR", "ACCELERATOR_POS_D", "ACCELERATOR_POS_E", "RELATIVE_ACCEL_POS"}:
        return "Motor, marcha y mandos"
    if "TEMP" in pid_name or pid_name == "AMBIANT_AIR_TEMP":
        return "Temperaturas y refrigeración"
    if pid_name in {"MAF", "INTAKE_PRESSURE", "BAROMETRIC_PRESSURE", "COMMANDED_EGR", "EGR_ERROR"}:
        return "Admisión, aire, EGR y turbo"
    if "VOLTAGE" in pid_name:
        return "Sistema eléctrico"
    return "Combustible, mezcla y emisiones"


def _standard_unit(pid_name: str, description: str) -> str:
    known = {name: unit for name, _, _, _, unit in STANDARD_PIDS}
    if pid_name in known:
        return known[pid_name]
    text = f"{pid_name} {description}".upper()
    if "TEMP" in text:
        return "°C"
    if "PRESSURE" in text:
        return "kPa"
    if "DISTANCE" in text:
        return "km"
    if "TIME" in text or "RUN_TIME" in text:
        return "s"
    if "RPM" in text:
        return "rpm"
    if "SPEED" in text:
        return "km/h"
    if "VOLTAGE" in text:
        return "V"
    if "CURRENT" in text:
        return "mA"
    if "MAF" in text or "AIR FLOW" in text:
        return "g/s"
    if "ADVANCE" in text or "TIMING" in text:
        return "°"
    if any(token in text for token in ("TRIM", "POSITION", "LOAD", "PERCENT", "PURGE", "FUEL LEVEL", "BATTERY")):
        return "%"
    if "WARM-UP" in text or "COUNT" in text:
        return "count"
    return "state"


def _standard_catalog(_: Dict[str, Any]) -> Iterable[MetricRow]:
    rows: Dict[str, tuple[str, str, str, str]] = {
        name: (mode, pid, label, unit)
        for name, mode, pid, label, unit in STANDARD_PIDS
    }
    # python-OBD 0.7.3 contiene la tabla completa que esta aplicación puede
    # consultar y decodificar de Mode 01. Se cataloga entera; STANDARD_PIDS
    # sigue siendo el subconjunto ligero usado por la importación manual.
    if obd is not None:
        for command in obd.commands[1]:
            if command is None:
                continue
            request = bytes(command.command).decode("ascii", errors="ignore")
            if len(request) < 4:
                continue
            rows[command.name] = (
                request[:2],
                request[2:4],
                command.desc,
                _standard_unit(command.name, command.desc),
            )
    # La tensión del adaptador es un dato AT adicional y no forma parte de
    # Mode 01, pero sí puede obtenerse con el hardware conectado.
    for name, (mode, pid, label, unit) in rows.items():
        yield {
            "pid_name": name,
            "label": label,
            "category": _standard_category(name),
            "mode": mode,
            "pid": pid,
            "unit": unit,
            "source": "obd_standard_catalog",
            "status": "not_tested",
            "reason": "SE_COMPROBARA_AL_CONECTAR",
            "supported_reported": False,
            "supported_verified": False,
        }


def _passat_b6_bkp_catalog(vehicle: Dict[str, Any]) -> Iterable[MetricRow]:
    make = str(vehicle.get("make", "")).strip().lower()
    engine_code = str(vehicle.get("engine_code", "")).strip().upper()
    if make not in {"volkswagen", "vw", "audi", "seat", "skoda", "škoda"}:
        return
    if engine_code not in {"BKP", "BMP", "BMN", "BMR", "BUY", "BUZ"}:
        return
    for definition in ALL_KWP_SIGNALS:
        yield {
            "pid_name": definition.pid_name,
            "label": definition.label,
            "category": category_for_group(definition.group),
            "group_number": definition.group,
            "position": definition.position + 1,
            "mode": "KWP_21",
            "pid": f"{definition.group:03d}.{definition.position + 1}",
            "unit": definition.unit,
            "source": "vag_kwp2000_catalog",
            "status": "not_tested",
            "reason": "SE_COMPROBARA_EN_LA_PROXIMA_IDENTIFICACION",
            "supported_reported": False,
            "supported_verified": False,
        }


# Los agentes que integren nuevas familias deben añadir un proveedor específico
# aquí, en vez de seleccionar solo las métricas que parezcan interesantes.
CATALOG_PROVIDERS: tuple[CatalogProvider, ...] = (
    _standard_catalog,
    _passat_b6_bkp_catalog,
)


def metric_catalog_for_vehicle(
    vehicle: Dict[str, Any],
    observed_capabilities: Iterable[MetricRow] = (),
) -> List[MetricRow]:
    """Combina todos los candidatos conocidos con la evidencia de este coche."""
    merged: Dict[str, MetricRow] = {}
    for provider in CATALOG_PROVIDERS:
        for item in provider(vehicle):
            merged[str(item["pid_name"])] = dict(item)

    for observed in observed_capabilities:
        pid_name = str(observed.get("pid_name", "")).strip()
        if not pid_name:
            continue
        base = merged.get(pid_name, {})
        # Campos vacíos de una captura nunca deben borrar la etiqueta, categoría
        # o identificador documentados por el catálogo del agente.
        merged[pid_name] = {
            **base,
            **{key: value for key, value in observed.items() if value not in (None, "")},
            "pid_name": pid_name,
        }

    return sorted(
        merged.values(),
        key=lambda item: (
            str(item.get("category", "Sin clasificar")),
            int(item.get("group_number") or 9999),
            int(item.get("position") or 9999),
            str(item.get("pid_name", "")),
        ),
    )


__all__ = ["CATALOG_PROVIDERS", "metric_catalog_for_vehicle"]
