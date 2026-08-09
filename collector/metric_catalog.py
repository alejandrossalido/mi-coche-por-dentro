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


UNIVERSAL_DIAGNOSTIC_CANDIDATES: tuple[tuple[str, str, str, str, int], ...] = (
    # Motor, marcha y mandos
    ("RPM", "Revoluciones del motor", "Motor, marcha y mandos", "rpm", 100),
    ("SPEED", "Velocidad del vehículo", "Motor, marcha y mandos", "km/h", 98),
    ("ENGINE_LOAD", "Carga calculada del motor", "Motor, marcha y mandos", "%", 96),
    ("OEM_ENGINE_TORQUE", "Par real del motor", "Motor, marcha y mandos", "Nm", 94),
    ("OEM_DRIVER_TORQUE_REQUEST", "Par solicitado por el conductor", "Motor, marcha y mandos", "Nm", 92),
    ("OEM_SELECTED_GEAR", "Marcha seleccionada", "Motor, marcha y mandos", "gear", 90),
    ("OEM_ENGINE_STATE", "Estado de funcionamiento del motor", "Motor, marcha y mandos", "state", 88),
    ("OEM_CAMSHAFT_SPEED", "Velocidad del árbol de levas", "Motor, marcha y mandos", "rpm", 86),
    ("OEM_CAM_CRANK_SYNC", "Sincronización árbol de levas/cigüeñal", "Motor, marcha y mandos", "state", 84),
    ("OEM_OIL_PRESSURE", "Presión del aceite", "Motor, marcha y mandos", "kPa", 82),
    ("OEM_MISFIRE_COUNT_TOTAL", "Fallos de combustión totales", "Motor, marcha y mandos", "count", 80),
    ("OEM_CLUTCH_POSITION", "Posición del embrague", "Motor, marcha y mandos", "%", 66),
    # Temperaturas
    ("COOLANT_TEMP", "Temperatura del refrigerante", "Temperaturas y refrigeración", "°C", 100),
    ("OIL_TEMP", "Temperatura del aceite", "Temperaturas y refrigeración", "°C", 96),
    ("INTAKE_TEMP", "Temperatura del aire de admisión", "Temperaturas y refrigeración", "°C", 92),
    ("AMBIANT_AIR_TEMP", "Temperatura ambiente", "Temperaturas y refrigeración", "°C", 88),
    ("OEM_FUEL_TEMP", "Temperatura del combustible", "Temperaturas y refrigeración", "°C", 86),
    ("OEM_RADIATOR_OUTLET_TEMP", "Refrigerante a la salida del radiador", "Temperaturas y refrigeración", "°C", 84),
    ("OEM_TRANSMISSION_OIL_TEMP", "Temperatura del aceite de transmisión", "Temperaturas y refrigeración", "°C", 82),
    ("OEM_CHARGE_AIR_TEMP", "Temperatura del aire de sobrealimentación", "Temperaturas y refrigeración", "°C", 80),
    ("OEM_COOLING_FAN_COMMAND", "Mando del ventilador de refrigeración", "Temperaturas y refrigeración", "%", 78),
    # Admisión, aire, EGR y turbo
    ("MAF", "Caudal de aire MAF", "Admisión, aire, EGR y turbo", "g/s", 100),
    ("INTAKE_PRESSURE", "Presión del colector MAP", "Admisión, aire, EGR y turbo", "kPa", 98),
    ("BAROMETRIC_PRESSURE", "Presión barométrica", "Admisión, aire, EGR y turbo", "kPa", 92),
    ("THROTTLE_POS", "Posición de la mariposa", "Admisión, aire, EGR y turbo", "%", 90),
    ("OEM_BOOST_PRESSURE_REQUESTED", "Presión de turbo solicitada", "Admisión, aire, EGR y turbo", "kPa", 96),
    ("OEM_BOOST_PRESSURE_ACTUAL", "Presión de turbo real", "Admisión, aire, EGR y turbo", "kPa", 96),
    ("OEM_TURBO_ACTUATOR_COMMAND", "Mando del actuador del turbo", "Admisión, aire, EGR y turbo", "%", 86),
    ("OEM_EGR_REQUESTED", "EGR solicitada", "Admisión, aire, EGR y turbo", "%", 88),
    ("OEM_EGR_ACTUAL", "EGR real", "Admisión, aire, EGR y turbo", "%", 88),
    ("OEM_SWIRL_FLAP_POSITION", "Posición de las mariposas de admisión", "Admisión, aire, EGR y turbo", "%", 72),
    # Combustible, mezcla e inyección
    ("FUEL_RATE", "Caudal de combustible", "Combustible, mezcla e inyección", "L/h", 100),
    ("FUEL_PRESSURE", "Presión de combustible", "Combustible, mezcla e inyección", "kPa", 96),
    ("OEM_FUEL_RAIL_PRESSURE_REQUESTED", "Presión del rail solicitada", "Combustible, mezcla e inyección", "bar", 94),
    ("OEM_FUEL_RAIL_PRESSURE_ACTUAL", "Presión del rail real", "Combustible, mezcla e inyección", "bar", 94),
    ("OEM_INJECTION_QUANTITY", "Cantidad de inyección", "Combustible, mezcla e inyección", "mg/str", 98),
    ("OEM_INJECTION_DURATION", "Duración de inyección", "Combustible, mezcla e inyección", "°CA", 92),
    ("FUEL_INJECT_TIMING", "Inicio o avance de inyección", "Combustible, mezcla e inyección", "°", 90),
    ("COMMANDED_EQUIV_RATIO", "Relación equivalente solicitada", "Combustible, mezcla e inyección", "λ", 86),
    ("SHORT_FUEL_TRIM_1", "Corrección corta de combustible banco 1", "Combustible, mezcla e inyección", "%", 84),
    ("LONG_FUEL_TRIM_1", "Corrección larga de combustible banco 1", "Combustible, mezcla e inyección", "%", 84),
    ("OEM_INJECTOR_CORRECTION_1", "Corrección del inyector 1", "Combustible, mezcla e inyección", "mg/str", 82),
    ("OEM_INJECTOR_CORRECTION_2", "Corrección del inyector 2", "Combustible, mezcla e inyección", "mg/str", 82),
    ("OEM_INJECTOR_CORRECTION_3", "Corrección del inyector 3", "Combustible, mezcla e inyección", "mg/str", 82),
    ("OEM_INJECTOR_CORRECTION_4", "Corrección del inyector 4", "Combustible, mezcla e inyección", "mg/str", 82),
    # Escape, catalizador, DPF/GPF y SCR
    ("OEM_EGT_PRE_TURBO", "Temperatura de escape antes del turbo", "Escape, DPF/GPF y SCR", "°C", 100),
    ("OEM_EGT_PRE_DPF", "Temperatura de escape antes del DPF/GPF", "Escape, DPF/GPF y SCR", "°C", 98),
    ("OEM_EGT_POST_DPF", "Temperatura de escape después del DPF/GPF", "Escape, DPF/GPF y SCR", "°C", 96),
    ("OEM_DPF_DIFFERENTIAL_PRESSURE", "Presión diferencial del DPF/GPF", "Escape, DPF/GPF y SCR", "mbar", 100),
    ("OEM_DPF_SOOT_CALCULATED", "Masa de hollín calculada", "Escape, DPF/GPF y SCR", "g", 98),
    ("OEM_DPF_SOOT_MEASURED", "Masa de hollín medida", "Escape, DPF/GPF y SCR", "g", 96),
    ("OEM_DPF_ASH_MASS", "Masa de ceniza", "Escape, DPF/GPF y SCR", "g", 92),
    ("OEM_DPF_REGEN_STATUS", "Estado de regeneración", "Escape, DPF/GPF y SCR", "state", 94),
    ("OEM_DPF_DISTANCE_SINCE_REGEN", "Distancia desde la última regeneración", "Escape, DPF/GPF y SCR", "km", 88),
    ("OEM_DPF_TIME_SINCE_REGEN", "Tiempo desde la última regeneración", "Escape, DPF/GPF y SCR", "s", 86),
    ("OEM_NOX_UPSTREAM", "NOx antes del sistema SCR", "Escape, DPF/GPF y SCR", "ppm", 84),
    ("OEM_NOX_DOWNSTREAM", "NOx después del sistema SCR", "Escape, DPF/GPF y SCR", "ppm", 84),
    ("OEM_ADBLUE_LEVEL", "Nivel de AdBlue", "Escape, DPF/GPF y SCR", "%", 80),
    ("OEM_ADBLUE_PRESSURE", "Presión de AdBlue", "Escape, DPF/GPF y SCR", "kPa", 76),
    ("OEM_SCR_DOSING", "Dosificación de AdBlue/SCR", "Escape, DPF/GPF y SCR", "mg/s", 74),
    # Sistema eléctrico y comunicaciones
    ("CONTROL_MODULE_VOLTAGE", "Tensión del módulo de control", "Sistema eléctrico y comunicaciones", "V", 100),
    ("ELM_VOLTAGE", "Tensión del adaptador OBD", "Sistema eléctrico y comunicaciones", "V", 98),
    ("OEM_ALTERNATOR_LOAD", "Carga del alternador", "Sistema eléctrico y comunicaciones", "%", 96),
    ("OEM_ALTERNATOR_CURRENT", "Corriente del alternador", "Sistema eléctrico y comunicaciones", "A", 90),
    ("OEM_BATTERY_VOLTAGE", "Tensión de batería", "Sistema eléctrico y comunicaciones", "V", 98),
    ("OEM_BATTERY_CURRENT", "Corriente de batería", "Sistema eléctrico y comunicaciones", "A", 94),
    ("OEM_BATTERY_SOC", "Estado de carga de la batería", "Sistema eléctrico y comunicaciones", "%", 92),
    ("OEM_BATTERY_SOH", "Estado de salud de la batería", "Sistema eléctrico y comunicaciones", "%", 88),
    ("OEM_BATTERY_TEMP", "Temperatura de la batería", "Sistema eléctrico y comunicaciones", "°C", 84),
    ("OEM_STARTER_VOLTAGE", "Tensión durante el arranque", "Sistema eléctrico y comunicaciones", "V", 86),
    ("OEM_CAN_ENGINE_STATUS", "Comunicación CAN de la ECU de motor", "Sistema eléctrico y comunicaciones", "state", 78),
    ("OEM_CAN_TRANSMISSION_STATUS", "Comunicación CAN de la transmisión", "Sistema eléctrico y comunicaciones", "state", 76),
    ("OEM_CAN_ABS_STATUS", "Comunicación CAN del ABS/ESP", "Sistema eléctrico y comunicaciones", "state", 76),
)


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
            "importance": 95 if name in {"RPM", "SPEED", "COOLANT_TEMP", "ENGINE_LOAD", "MAF", "CONTROL_MODULE_VOLTAGE"} else 70,
            "source": "obd_standard_catalog",
            "status": "not_tested",
            "reason": "SE_COMPROBARA_AL_CONECTAR",
            "supported_reported": False,
            "supported_verified": False,
        }


def _universal_candidate_catalog(_: Dict[str, Any]) -> Iterable[MetricRow]:
    """Expose useful OEM concepts even before a vehicle-specific mapping exists.

    These rows are deliberately *not* executable PIDs.  They make the complete
    diagnostic surface visible and give an importing agent an explicit checklist
    without ever pretending that a vehicle supports a signal.
    """
    for pid_name, label, category, unit, importance in UNIVERSAL_DIAGNOSTIC_CANDIDATES:
        yield {
            "pid_name": pid_name,
            "label": label,
            "category": category,
            "mode": "OEM",
            "pid": "",
            "unit": unit,
            "importance": importance,
            "source": "universal_diagnostic_candidate",
            "status": "mapping_required",
            "reason": "EL_AGENTE_DEBE_INVESTIGAR_IDENTIFICADOR_Y_FORMULA",
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
            "importance": 90 if any(token in definition.pid_name for token in ("RPM", "SPEED", "COOLANT", "OIL_TEMP", "BOOST", "DPF", "INJECTION", "VOLTAGE")) else 65,
            "source": "vag_kwp2000_catalog",
            "status": "not_tested",
            "reason": "SE_COMPROBARA_EN_LA_PROXIMA_IDENTIFICACION",
            "supported_reported": False,
            "supported_verified": False,
        }


# Los agentes que integren nuevas familias deben añadir un proveedor específico
# aquí, en vez de seleccionar solo las métricas que parezcan interesantes.
CATALOG_PROVIDERS: tuple[CatalogProvider, ...] = (
    _universal_candidate_catalog,
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
            pid_name = str(item["pid_name"])
            base = merged.get(pid_name, {})
            # Providers later in the list may add vehicle-specific identifiers,
            # while empty fields must not erase an executable standard mapping.
            merged[pid_name] = {
                **base,
                **{key: value for key, value in item.items() if value not in (None, "")},
                "pid_name": pid_name,
            }
            merged[pid_name]["importance"] = max(
                int(base.get("importance") or 0),
                int(item.get("importance") or 0),
            )

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
            -int(item.get("importance") or 0),
            int(item.get("group_number") or 9999),
            int(item.get("position") or 9999),
            str(item.get("pid_name", "")),
        ),
    )


__all__ = ["CATALOG_PROVIDERS", "metric_catalog_for_vehicle"]
