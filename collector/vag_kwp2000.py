"""Lectura VAG KWP2000/TP2.0 estrictamente de solo lectura.

Los motores Volkswagen de la familia 03G-906-018 (entre ellos varios Passat
B6 con EDC16) no usan UDS para sus valores ampliados. Exponen bloques de
medida KWP2000 a traves del transporte CAN propietario TP2.0. Este modulo
solo abre una sesion diagnostica y usa ReadDataByLocalIdentifier (0x21).
"""

from __future__ import annotations

import logging
import math
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from collector.vag_bkp_catalog import (
    DOCUMENTED_GROUPS,
    category_for_group,
    documented_field_count,
)

logger = logging.getLogger(__name__)

ENGINE_MODULE_ADDRESS = 0x01


def normalize_vag_part_number(value: Any) -> str:
    if isinstance(value, (bytes, bytearray)):
        text = bytes(value).decode("ascii", errors="ignore")
    elif isinstance(value, (list, tuple)):
        text = " ".join(normalize_vag_part_number(item) for item in value)
    else:
        text = str(value or "")
    text = re.sub(r"bytearray\(b?['\"]|[b]?['\"]\)$", "", text)
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def is_legacy_kwp_calibration(value: Any) -> bool:
    """Reconoce la familia EDC16 03G-906-018 aun si Mode 09 omite el cero."""
    normalized = normalize_vag_part_number(value)
    return "03G906018" in normalized or normalized.startswith("3G906018")


@dataclass(frozen=True)
class KwpSignalDefinition:
    pid_name: str
    label: str
    unit: str
    group: int
    position: int
    accepted_types: tuple[int, ...]
    scale: float = 1.0
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    allow_all_zero_fields: bool = False
    value_from_b: bool = False


# Posiciones contrastadas con la familia de etiquetas 03G-906-018. La propia
# ECU debe devolver ademas un tipo binario compatible y un valor plausible;
# si no lo hace, la senal no se declara verificada.
KWP_SIGNALS: tuple[KwpSignalDefinition, ...] = (
    KwpSignalDefinition("RPM", "Revoluciones del motor", "rpm", 1, 0, (0x01,), 1.0, 0, 8000),
    KwpSignalDefinition("VAG_INJECTION_QUANTITY", "Cantidad de inyección", "mg/str", 1, 1, (0x27,), 1.0, 0, 100),
    KwpSignalDefinition("VAG_INJECTION_DURATION", "Duración de inyección solicitada", "°CA", 1, 2, (0x22,), 1.0, -5, 60),
    KwpSignalDefinition("COOLANT_TEMP", "Temperatura del refrigerante", "°C", 1, 3, (0x1A,), 1.0, -40, 150),
    KwpSignalDefinition("SPEED", "Velocidad del vehículo", "km/h", 6, 0, (0x07,), 1.0, 0, 350),
    KwpSignalDefinition("INTAKE_TEMP", "Temperatura del aire de admisión", "°C", 7, 2, (0x1A,), 1.0, -40, 120),
    KwpSignalDefinition("VAG_FUEL_TEMP", "Temperatura del combustible", "°C", 7, 0, (0x1A,), 1.0, -40, 140),
    KwpSignalDefinition("VAG_OIL_TEMP", "Temperatura del aceite", "°C", 29, 0, (0x1A,), 1.0, -40, 180),
    # La PPD1.5 03G 906 018 FG devuelve este campo como tipo KWP 0x05
    # (temperatura escalada), no como el 0x1A usado por otros bloques.
    KwpSignalDefinition("VAG_AMBIENT_TEMP", "Temperatura ambiente", "°C", 62, 2, (0x05, 0x1A), 1.0, -50, 80),
    KwpSignalDefinition("VAG_EXHAUST_TEMP_1", "Temperatura antes del turbo", "°C", 67, 0, (0x1A,), 1.0, -40, 1000),
    KwpSignalDefinition("VAG_EXHAUST_TEMP_2", "Temperatura en el DPF", "°C", 67, 1, (0x1A,), 1.0, -40, 1000),
    KwpSignalDefinition("VAG_BAROMETRIC_PRESSURE", "Presión barométrica", "kPa", 10, 1, (0x12,), 0.1, 70, 120),
    KwpSignalDefinition("VAG_ACCELERATOR_POSITION", "Posición del pedal", "%", 2, 1, (0x14, 0x17, 0x21), 1.0, 0, 100),
    KwpSignalDefinition("VAG_AIR_MASS_ACTUAL", "Masa de aire real", "mg/str", 10, 0, (0x31,), 1.0, 0, 2000),
    KwpSignalDefinition("VAG_EGR_COMMAND", "Masa de aire objetivo EGR", "mg/str", 3, 1, (0x31,), 1.0, 0, 2000),
    KwpSignalDefinition("VAG_EGR_ACTUAL", "Masa de aire real EGR", "mg/str", 3, 2, (0x31,), 1.0, 0, 2000),
    KwpSignalDefinition("VAG_EGR_DUTY_CYCLE", "Mando de la EGR", "%", 3, 3, (0x14, 0x17, 0x21), 1.0, -5, 105),
    KwpSignalDefinition("VAG_BOOST_PRESSURE_REQUESTED", "Presión de turbo solicitada", "kPa", 11, 1, (0x12,), 0.1, 50, 350),
    KwpSignalDefinition("VAG_BOOST_PRESSURE_ACTUAL", "Presión de turbo real", "kPa", 11, 2, (0x12,), 0.1, 50, 350),
    KwpSignalDefinition("VAG_INJECTION_TIMING", "Inicio de inyección solicitado", "°", 4, 1, (0x04,), 1.0, -30, 40),
    KwpSignalDefinition("VAG_INJECTION_DURATION_2", "Duración de inyección solicitada (bloque 4)", "°CA", 4, 2, (0x22,), 1.0, -5, 60),
    KwpSignalDefinition("VAG_TORSION_VALUE", "Valor de torsión de la distribución", "°CA", 4, 3, (0x04, 0x51), 1.0, -100, 100),
    KwpSignalDefinition("VAG_FUEL_RATE", "Consumo de combustible", "L/h", 15, 2, (0x23,), 1.0, 0, 80),
    KwpSignalDefinition("VAG_ENGINE_TORQUE", "Par calculado del motor", "Nm", 15, 1, (0x5E,), 1.0, -100, 600),
    KwpSignalDefinition("VAG_DRIVER_TORQUE_REQUEST", "Par solicitado por el conductor", "Nm", 15, 3, (0x5E,), 1.0, -100, 600),
    KwpSignalDefinition("VAG_INJECTOR_DEVIATION_1", "Corrección del inyector 1", "mg/str", 13, 0, (0x33,), 1.0, -10, 10),
    KwpSignalDefinition("VAG_INJECTOR_DEVIATION_2", "Corrección del inyector 2", "mg/str", 13, 1, (0x33,), 1.0, -10, 10),
    KwpSignalDefinition("VAG_INJECTOR_DEVIATION_3", "Corrección del inyector 3", "mg/str", 13, 2, (0x33,), 1.0, -10, 10),
    KwpSignalDefinition("VAG_INJECTOR_DEVIATION_4", "Corrección del inyector 4", "mg/str", 13, 3, (0x33,), 1.0, -10, 10),
    KwpSignalDefinition("VAG_INJECTOR_STATUS_1", "Estado del inyector 1", "state_code", 18, 0, (0x08, 0x10, 0x25), 1.0, 0, 255, True, True),
    KwpSignalDefinition("VAG_INJECTOR_STATUS_2", "Estado del inyector 2", "state_code", 18, 1, (0x08, 0x10, 0x25), 1.0, 0, 255, True, True),
    KwpSignalDefinition("VAG_INJECTOR_STATUS_3", "Estado del inyector 3", "state_code", 18, 2, (0x08, 0x10, 0x25), 1.0, 0, 255, True, True),
    KwpSignalDefinition("VAG_INJECTOR_STATUS_4", "Estado del inyector 4", "state_code", 18, 3, (0x08, 0x10, 0x25), 1.0, 0, 255, True, True),
    KwpSignalDefinition("VAG_INJECTOR_SWITCH_TIME_1", "Desviación de conmutación del inyector 1", "ms", 23, 0, (0x16, 0x33), 1.0, -5, 5),
    KwpSignalDefinition("VAG_INJECTOR_SWITCH_TIME_2", "Desviación de conmutación del inyector 2", "ms", 23, 1, (0x16, 0x33), 1.0, -5, 5),
    KwpSignalDefinition("VAG_INJECTOR_SWITCH_TIME_3", "Desviación de conmutación del inyector 3", "ms", 23, 2, (0x16, 0x33), 1.0, -5, 5),
    KwpSignalDefinition("VAG_INJECTOR_SWITCH_TIME_4", "Desviación de conmutación del inyector 4", "ms", 23, 3, (0x16, 0x33), 1.0, -5, 5),
    KwpSignalDefinition("VAG_DPF_DIFFERENTIAL_PRESSURE", "Presión diferencial del DPF", "mbar", 67, 2, (0x12,), 1.0, -20, 500),
    KwpSignalDefinition("VAG_DPF_SOOT_PERCENT", "Carga de hollín del DPF", "%", 68, 0, (0x14, 0x17, 0x21), 1.0, 0, 100),
    KwpSignalDefinition("VAG_DPF_ASH_MASS", "Masa de ceniza del DPF", "g", 68, 1, (0x27, 0x31, 0x36), 1.0, 0, 200),
    KwpSignalDefinition("VAG_DPF_REGEN_STATUS", "Estado de regeneración del DPF", "state_code", 69, 3, (0x08, 0x10, 0x25), 1.0, 0, 65535),
    KwpSignalDefinition("VAG_ECU_VOLTAGE", "Tensión medida por la ECU", "V", 12, 2, (0x15,), 1.0, 5, 18),
)


SUPPORTED_BLOCK_TYPES = (
    0x01, 0x04, 0x05, 0x07, 0x08, 0x10, 0x12, 0x14, 0x15, 0x16, 0x17,
    0x1A, 0x21, 0x22, 0x23, 0x25, 0x27, 0x31, 0x33, 0x36, 0x37, 0x51, 0x5E,
)


def _unit_for_label(label: str) -> str:
    text = label.lower()
    if "revoluciones" in text or "árbol de levas" in text:
        return "rpm"
    if "temperatura" in text:
        return "°C"
    if "presión" in text or "contrapresión" in text:
        return "mbar"
    if "cantidad de inyección" in text or "postinyección" in text or "masa de aire" in text:
        return "mg/str"
    if "duración de inyección" in text or "inicio de inyección" in text or "torsión de la distribución" in text:
        return "°CA"
    if "tiempo de conmutación" in text:
        return "ms"
    if "tensión" in text:
        return "V"
    if "par" in text:
        return "Nm"
    if "velocidad" in text:
        return "km/h"
    if "distancia" in text:
        return "km"
    if "tiempo" in text or "periodo" in text:
        return "s"
    if "ceniza" in text:
        return "g"
    if any(word in text for word in ("mando", "carga", "posición", "hollín", "caudal", "consumo")):
        return "%"
    return "valor"


def _catalog_signal_definitions() -> tuple[KwpSignalDefinition, ...]:
    canonical_positions = {(item.group, item.position) for item in KWP_SIGNALS}
    definitions: List[KwpSignalDefinition] = []
    for group, (_, labels) in DOCUMENTED_GROUPS.items():
        for position, label in enumerate(labels):
            if not label or (group, position) in canonical_positions:
                continue
            definitions.append(
                KwpSignalDefinition(
                    f"VAG_MWB_{group:03d}_{position + 1}",
                    label,
                    _unit_for_label(label),
                    group,
                    position,
                    SUPPORTED_BLOCK_TYPES,
                )
            )
    return tuple(definitions)


CATALOG_KWP_SIGNALS = _catalog_signal_definitions()
ALL_KWP_SIGNALS = KWP_SIGNALS + CATALOG_KWP_SIGNALS
AUXILIARY_KWP_SIGNALS = tuple(
    KwpSignalDefinition(
        f"VAG_MWB_{group:03d}_{position + 1}",
        f"Campo auxiliar {position + 1} del bloque {group:03d}",
        "valor",
        group,
        position,
        SUPPORTED_BLOCK_TYPES,
    )
    for group in DOCUMENTED_GROUPS
    for position in range(4, 8)
)
RUNTIME_KWP_SIGNALS = ALL_KWP_SIGNALS + AUXILIARY_KWP_SIGNALS


def _decode_block_value(type_id: int, a: int, b: int) -> float:
    """Decodifica los tipos de bloque KWP usados por estas senales."""
    if type_id == 0x01:
        return a * b / 5.0
    if type_id == 0x04:
        return (127 - b) * 0.01 * a
    if type_id == 0x05:
        return a * (b - 100) / 10.0
    if type_id == 0x07:
        return 0.01 * a * b
    if type_id in (0x08, 0x10, 0x25):
        return float((a << 8) | b)
    if type_id == 0x12:
        return a * b / 25.0
    if type_id == 0x14:
        return a * b / 128.0 - 1.0
    if type_id == 0x15:
        return a * b / 1000.0
    if type_id == 0x16:
        return 0.001 * a * b
    if type_id == 0x17:
        return b * a / 256.0
    if type_id == 0x1A:
        return float(b - a)
    if type_id == 0x21:
        return 100.0 * b if a == 0 else 100.0 * b / a
    if type_id == 0x22:
        return (b - 128) * 0.01 * a
    if type_id == 0x23:
        return a * b / 100.0
    if type_id == 0x27:
        return a * b / 256.0
    if type_id == 0x31:
        return a * b / 40.0
    if type_id == 0x33:
        return ((b - 128) / 255.0) * a
    if type_id == 0x36:
        return float(a * 256 + b)
    if type_id == 0x37:
        return a * b / 200.0
    if type_id == 0x5E:
        return a * (b / 50.0 - 1.0)
    if type_id == 0x51:
        raw_signed = ((a << 8) | b)
        if raw_signed >= 0x8000:
            raw_signed -= 0x10000
        return raw_signed * 0.00436
    raise ValueError(f"Tipo KWP no reconocido: {type_id:02X}")


class Tp20Transport:
    """Transporte minimo TP2.0 sobre el puerto ya abierto por python-OBD."""

    def __init__(self, connection: Any):
        self.connection = connection
        self.interface = getattr(connection, "interface", None)
        self._send_raw = getattr(self.interface, "_ELM327__send", None)
        self.tx_sequence = 0
        self.rx_sequence = 0
        self.block_size = 0x0F
        self.is_open = False
        self.transcript: List[Dict[str, Any]] = []

    def _send(self, command: str, timeout: float = 2.0) -> List[str]:
        if not callable(self._send_raw):
            raise RuntimeError("El controlador serie no permite comandos TP2.0")
        port = getattr(self.interface, "_ELM327__port", None)
        previous_timeout = getattr(port, "timeout", None)
        if port is not None:
            port.timeout = timeout
        try:
            lines = self._send_raw(command.encode("ascii")) or []
        finally:
            if port is not None and previous_timeout is not None:
                port.timeout = previous_timeout
        clean = [str(line).strip() for line in lines if str(line).strip()]
        self.transcript.append({"tx": command, "rx": clean})
        return clean

    def _expect_ok(self, command: str) -> None:
        lines = self._send(command)
        if not any(line.upper() == "OK" for line in lines):
            raise RuntimeError(f"El adaptador rechazó {command}: {' | '.join(lines)}")

    @staticmethod
    def _can_frames(lines: Iterable[str]) -> List[tuple[int, bytes]]:
        frames: List[tuple[int, bytes]] = []
        for line in lines:
            compact = re.sub(r"\s+", "", line).upper()
            if compact in {"OK", "NODATA", "STOPPED", "CANERROR", "?"}:
                continue
            match = re.fullmatch(r"([0-9A-F]{3})([0-8])([0-9A-F]*)", compact)
            if not match:
                continue
            can_id = int(match.group(1), 16)
            length = int(match.group(2), 16)
            data_hex = match.group(3)
            if len(data_hex) != length * 2:
                continue
            frames.append((can_id, bytes.fromhex(data_hex)))
        return frames

    def open(self) -> None:
        # El adaptador puede conservar un canal personalizado medio abierto
        # tras una pérdida de trama. Cerrarlo evita heredar sus secuencias.
        try:
            self._send("ATPC", 0.7)
        except Exception:
            pass
        self.is_open = False
        self._send("ATE0")
        for command in ("ATE0", "ATPB C0 01", "ATSPB", "ATH1", "ATD1", "ATL0"):
            self._expect_ok(command)
        self._expect_ok("ATSH200")
        self._expect_ok("ATCRA201")
        setup_frames = self._can_frames(self._send("01C00010000301", 3.0))
        # Algunos vLinker entregan dos veces la misma respuesta del gateway.
        # Es una unica contestacion CAN duplicada por el adaptador, no dos
        # canales distintos, por lo que se debe validar tras deduplicarla.
        unique_setup_frames = list(dict.fromkeys(setup_frames))
        if len(unique_setup_frames) != 1 or len(unique_setup_frames[0][1]) != 7:
            raise RuntimeError("La pasarela Volkswagen no abrió el canal TP2.0 del motor")
        setup = unique_setup_frames[0][1]
        if setup[1] != 0xD0:
            raise RuntimeError(f"Respuesta de canal TP2.0 inesperada: {setup.hex().upper()}")
        rx_id = ((setup[3] & 0x0F) << 8) | setup[2]
        tx_id = ((setup[5] & 0x0F) << 8) | setup[4]
        if rx_id != 0x300:
            raise RuntimeError(f"Canal de recepción TP2.0 inesperado: {rx_id:03X}")
        self._expect_ok(f"ATSH{tx_id:03X}")
        self._expect_ok(f"ATCRA{rx_id:03X}")
        # Solicitud TP2.0: T3=0x0A (1 ms). La ECU suele contestar 0x4A;
        # usar por error ese valor de respuesta en la solicitud hacía que el
        # canal PPD se volviese inestable tras unas decenas de lecturas.
        params_frames = self._can_frames(self._send("A00F8AFF0AFF", 3.0))
        if len(params_frames) != 1 or len(params_frames[0][1]) != 6 or params_frames[0][1][0] != 0xA1:
            raise RuntimeError("La ECU no negoció los parámetros TP2.0")
        self.block_size = max(1, params_frames[0][1][1] & 0x0F)
        self.tx_sequence = 0
        self.rx_sequence = 0
        self.is_open = True
        response = self.request(bytes((0x10, 0x89)))
        if len(response) < 2 or response[:2] != bytes((0x50, 0x89)):
            raise RuntimeError(f"La ECU rechazó la sesión KWP2000: {response.hex().upper()}")

    def _ack(self, expect_data: bool) -> List[tuple[int, bytes]]:
        lines = self._send(f"{0xB0 | (self.rx_sequence & 0x0F):02X}", 2.0 if expect_data else 0.7)
        return self._can_frames(lines)

    def _assemble_response(self, frames: List[tuple[int, bytes]]) -> bytes:
        data_frames = [data for _, data in frames if data and (data[0] >> 4) <= 0x3]
        if not data_frames:
            raise RuntimeError("La ECU no devolvió datos KWP2000")
        payload = bytearray()
        expected_length: Optional[int] = None
        index = 0
        while index < len(data_frames):
            frame = data_frames[index]
            control = frame[0]
            opcode = control >> 4
            sequence = control & 0x0F
            if sequence != (self.rx_sequence & 0x0F):
                raise RuntimeError("Secuencia TP2.0 fuera de orden")
            self.rx_sequence += 1
            if expected_length is None:
                if len(frame) < 3:
                    raise RuntimeError("Primera trama TP2.0 demasiado corta")
                expected_length = ((frame[1] << 8) | frame[2]) & 0x7FFF
                payload.extend(frame[3:])
            else:
                payload.extend(frame[1:])
            last = bool(opcode & 0x01)
            requires_ack = not bool(opcode & 0x02)
            if requires_ack:
                continuation = self._ack(expect_data=not last)
                if not last:
                    data_frames.extend(data for _, data in continuation if data and (data[0] >> 4) <= 0x3)
            if last:
                break
            index += 1
        if expected_length is None:
            raise RuntimeError("Longitud TP2.0 ausente")
        return bytes(payload[:expected_length])

    def request(self, payload: bytes) -> bytes:
        if not self.is_open:
            raise RuntimeError("El canal TP2.0 no está abierto")
        if not payload or len(payload) > 5:
            raise ValueError("Esta implementación segura solo admite peticiones KWP cortas")
        packet = bytes((0x10 | (self.tx_sequence & 0x0F), 0x00, len(payload))) + payload
        self.tx_sequence += 1
        frames = self._can_frames(self._send(packet.hex().upper(), 3.0))
        expected_ack = 0xB0 | (self.tx_sequence & 0x0F)
        if not any(data and data[0] == expected_ack for _, data in frames):
            raise RuntimeError("La ECU no confirmó la petición TP2.0")
        return self._assemble_response(frames)

    def close(self) -> None:
        if self.is_open:
            try:
                self._send("A8", 0.7)
            except Exception:
                logger.debug("No se pudo cerrar explícitamente el canal TP2.0", exc_info=True)
        self.is_open = False


class VagKwp2000Client:
    """Cliente de bloques de medida para la ECU motor VAG EDC16."""

    transport_requires_reconnect = True

    def __init__(self, connection: Any, enabled_signal_names: Optional[set[str]] = None):
        self.transport = Tp20Transport(connection)
        self.definition_by_name = {item.pid_name: item for item in RUNTIME_KWP_SIGNALS}
        self._enabled_signal_names = enabled_signal_names
        self._block_cache: Dict[int, tuple[float, Dict[str, Any]]] = {}
        self.identity: Dict[str, str] = {}
        self.recovery_count = 0
        self.last_transport_error = ""
        self._last_recovery_attempt = 0.0

    @property
    def signal_names(self) -> set[str]:
        names = set(self.definition_by_name)
        return names & self._enabled_signal_names if self._enabled_signal_names is not None else names

    def open(self) -> None:
        self.transport.open()

    def close(self) -> None:
        self.transport.close()

    def _read_identity(self) -> Dict[str, str]:
        identity: Dict[str, str] = {}
        for name, parameter in (("long_identification", 0x9B), ("short_identification", 0x91)):
            try:
                response = self.transport.request(bytes((0x1A, parameter)))
                if len(response) >= 2 and response[:2] == bytes((0x5A, parameter)):
                    identity[name] = response[2:].decode("ascii", errors="replace").strip(" \x00\xff")
            except Exception as exc:
                identity[name] = f"No disponible: {exc}"
        self.identity = identity
        return identity

    def read_group(self, group: int, use_cache: bool = True) -> Dict[str, Any]:
        cached = self._block_cache.get(group)
        if use_cache and cached and time.monotonic() - cached[0] < 0.2:
            return cached[1]
        started = time.monotonic()
        try:
            response = self.transport.request(bytes((0x21, group)))
            latency = round((time.monotonic() - started) * 1000.0, 2)
            if len(response) >= 3 and response[0] == 0x7F:
                result = {"success": False, "status": "negative_response", "reason": f"KWP_NRC_{response[2]:02X}", "latency_ms": latency, "raw_response": response.hex().upper()}
            elif (
                len(response) < 14
                or (len(response) - 2) % 3 != 0
                or response[:2] != bytes((0x61, group))
            ):
                result = {"success": False, "status": "unexpected_response", "reason": "RESPUESTA_DE_BLOQUE_NO_RECONOCIDA", "latency_ms": latency, "raw_response": response.hex().upper()}
            else:
                fields = []
                # EDC16 suele devolver cuatro campos. La Siemens/VDO PPD1.5
                # 03G 906 018 FG comprobada devuelve ocho: los cuatro primeros
                # mantienen el formato de los bloques VCDS y los restantes son
                # auxiliares. Ambos tamaños son respuestas válidas.
                for position in range((len(response) - 2) // 3):
                    type_id, a, b = response[2 + position * 3:5 + position * 3]
                    try:
                        value = _decode_block_value(type_id, a, b)
                    except ValueError:
                        value = None
                    fields.append({"type_id": type_id, "a": a, "b": b, "value": value})
                result = {
                    "success": True,
                    "status": "compatible",
                    "fields": fields,
                    "field_count": len(fields),
                    "all_placeholders": all(
                        field["type_id"] == 0x25 and field["a"] == 0 and field["b"] == 0
                        for field in fields
                    ),
                    "latency_ms": latency,
                    "raw_response": response.hex().upper(),
                }
        except Exception as exc:
            first_error = str(exc)
            self.last_transport_error = first_error
            if time.monotonic() - self._last_recovery_attempt < 2.0:
                result = {
                    "success": False,
                    "status": "transport_error",
                    "reason": first_error,
                    "latency_ms": round((time.monotonic() - started) * 1000.0, 2),
                    "raw_response": "",
                }
                self._block_cache[group] = (time.monotonic(), result)
                return result
            self._last_recovery_attempt = time.monotonic()
            # Una trama perdida deja desincronizados los contadores TP2.0. La
            # recuperación correcta es cerrar y negociar de nuevo, no seguir
            # acumulando lecturas vacías durante el resto de la ruta.
            try:
                self.transport.close()
                time.sleep(0.12)
                self.transport.open()
                self.recovery_count += 1
                self._block_cache.clear()
                response = self.transport.request(bytes((0x21, group)))
                latency = round((time.monotonic() - started) * 1000.0, 2)
                if len(response) < 14 or (len(response) - 2) % 3 != 0 or response[:2] != bytes((0x61, group)):
                    raise RuntimeError("Respuesta inválida tras recuperar el canal TP2.0")
                fields = []
                for position in range((len(response) - 2) // 3):
                    type_id, a, b = response[2 + position * 3:5 + position * 3]
                    try:
                        value = _decode_block_value(type_id, a, b)
                    except ValueError:
                        value = None
                    fields.append({"type_id": type_id, "a": a, "b": b, "value": value})
                result = {
                    "success": True,
                    "status": "compatible_recovered",
                    "fields": fields,
                    "field_count": len(fields),
                    "all_placeholders": all(
                        field["type_id"] == 0x25 and field["a"] == 0 and field["b"] == 0
                        for field in fields
                    ),
                    "latency_ms": latency,
                    "raw_response": response.hex().upper(),
                }
            except Exception as recovery_exc:
                self.last_transport_error = f"{first_error}; recuperación: {recovery_exc}"
                result = {
                    "success": False,
                    "status": "transport_error",
                    "reason": self.last_transport_error,
                    "latency_ms": round((time.monotonic() - started) * 1000.0, 2),
                    "raw_response": "",
                }
        # Marca el instante real al terminar cada petición física. Una vuelta
        # completa puede tardar muchos segundos, por lo que no es correcto
        # asignar a todos los bloques la hora de inicio de la vuelta.
        result["captured_monotonic"] = time.monotonic()
        self._block_cache[group] = (time.monotonic(), result)
        return result

    def _decode_signal_from_group(
        self,
        definition: KwpSignalDefinition,
        group: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Convierte un campo usando una respuesta de bloque ya obtenida."""
        pid_name = definition.pid_name
        if not group.get("success"):
            return {"pid": pid_name, "unit": definition.unit, **group}
        if group.get("all_placeholders") and not definition.allow_all_zero_fields:
            return {
                "pid": pid_name,
                "unit": definition.unit,
                "success": False,
                "status": "unsupported",
                "reason": "BLOQUE_SIN_DATOS_EN_ESTA_ECU",
                "latency_ms": group["latency_ms"],
                "raw_response": group["raw_response"],
            }
        if definition.position >= len(group.get("fields", [])):
            return {
                "pid": pid_name,
                "unit": definition.unit,
                "success": False,
                "status": "unsupported",
                "reason": "CAMPO_NO_DEVUELTO_POR_ESTA_ECU",
                "latency_ms": group["latency_ms"],
                "raw_response": group["raw_response"],
            }
        field = group["fields"][definition.position]
        if (
            field["type_id"] == 0x25
            and field["a"] == 0
            and field["b"] == 0
            and not definition.allow_all_zero_fields
        ):
            return {
                "pid": pid_name,
                "unit": definition.unit,
                "success": False,
                "status": "unsupported",
                "reason": "MARCADOR_VACIO_DE_LA_ECU",
                "latency_ms": group["latency_ms"],
                "raw_response": group["raw_response"],
            }
        if field["type_id"] not in definition.accepted_types or field["value"] is None:
            return {"pid": pid_name, "unit": definition.unit, "success": False, "status": "type_mismatch", "reason": f"TIPO_KWP_{field['type_id']:02X}_NO_ESPERADO", "latency_ms": group["latency_ms"], "raw_response": group["raw_response"]}
        value = float(field["b"] if definition.value_from_b else field["value"]) * definition.scale
        if not math.isfinite(value) or (definition.minimum is not None and value < definition.minimum) or (definition.maximum is not None and value > definition.maximum):
            return {"pid": pid_name, "unit": definition.unit, "success": False, "status": "implausible", "reason": "VALOR_FUERA_DE_RANGO", "value": value, "latency_ms": group["latency_ms"], "raw_response": group["raw_response"]}
        return {
            "pid": pid_name,
            "value": round(value, 4),
            "unit": definition.unit,
            "success": True,
            "status": "compatible",
            "latency_ms": group["latency_ms"],
            "raw_response": group["raw_response"],
            "data_source": "measured_vag_kwp2000",
            "captured_monotonic": group.get("captured_monotonic"),
        }

    def read_signal(self, pid_name: str, use_cache: bool = True) -> Dict[str, Any]:
        definition = self.definition_by_name.get(pid_name)
        if definition is None:
            return {"pid": pid_name, "success": False, "status": "mapping_required", "reason": "BLOQUE_NO_DEFINIDO"}
        group = self.read_group(definition.group, use_cache=use_cache)
        return self._decode_signal_from_group(definition, group)

    def read_signals_batch(self, pid_names: Iterable[str]) -> Dict[str, Dict[str, Any]]:
        """Lee cada bloque físico una sola vez y extrae todas sus señales.

        Es esencial en la PPD1.5: más de doscientas métricas documentadas se
        concentran en 69 bloques y no deben convertirse en 214 peticiones CAN.
        """
        definitions_by_group: Dict[int, List[KwpSignalDefinition]] = {}
        results: Dict[str, Dict[str, Any]] = {}
        for pid_name in dict.fromkeys(str(name) for name in pid_names):
            definition = self.definition_by_name.get(pid_name)
            if definition is None:
                results[pid_name] = {
                    "pid": pid_name,
                    "success": False,
                    "status": "mapping_required",
                    "reason": "BLOQUE_NO_DEFINIDO",
                }
                continue
            definitions_by_group.setdefault(definition.group, []).append(definition)

        for group_number in sorted(definitions_by_group):
            group = self.read_group(group_number, use_cache=False)
            for definition in definitions_by_group[group_number]:
                results[definition.pid_name] = self._decode_signal_from_group(definition, group)
        return results

    def probe(
        self,
        standard_identity: Optional[Dict[str, Any]] = None,
        exhaustive: bool = True,
    ) -> Dict[str, Any]:
        self.open()
        try:
            identity = self._read_identity()
            live_signals: List[Dict[str, Any]] = []
            groups: Dict[int, Dict[str, Any]] = {}
            definitions = ALL_KWP_SIGNALS if exhaustive else KWP_SIGNALS
            groups_to_read = (
                tuple(DOCUMENTED_GROUPS)
                if exhaustive
                else tuple(dict.fromkeys(item.group for item in definitions))
            )
            for group in groups_to_read:
                groups[group] = self.read_group(group, use_cache=False)

            by_position = {(item.group, item.position): item for item in definitions}
            for group_number in groups_to_read:
                group_result = groups[group_number]
                title, documented_labels = DOCUMENTED_GROUPS.get(
                    group_number,
                    (f"Bloque {group_number:03d}", ("", "", "", "")),
                )
                returned_count = len(group_result.get("fields", []))
                positions = {
                    position for position, label in enumerate(documented_labels) if label
                }
                positions.update(range(returned_count))
                for position in sorted(positions):
                    definition = by_position.get((group_number, position))
                    label = (
                        definition.label
                        if definition
                        else documented_labels[position]
                        if position < len(documented_labels) and documented_labels[position]
                        else f"Campo descubierto {position + 1}"
                    )
                    pid_name = (
                        definition.pid_name
                        if definition
                        else f"VAG_MWB_{group_number:03d}_{position + 1}"
                    )
                    if definition:
                        reading = self.read_signal(pid_name)
                    elif group_result.get("success") and position < returned_count:
                        field = group_result["fields"][position]
                        is_empty_marker = (
                            field.get("type_id") == 0x25
                            and field.get("a") == 0
                            and field.get("b") == 0
                        )
                        reading = {
                            "success": field.get("value") is not None and not is_empty_marker,
                            "status": "compatible" if field.get("value") is not None and not is_empty_marker else "unsupported" if is_empty_marker else "undecoded",
                            "reason": "MARCADOR_VACIO_DE_LA_ECU" if is_empty_marker else "" if field.get("value") is not None else f"TIPO_KWP_{field['type_id']:02X}_SIN_DECODIFICAR",
                            "value": field.get("value"),
                            "unit": "valor",
                            "latency_ms": group_result.get("latency_ms", 0.0),
                            "raw_response": group_result.get("raw_response", ""),
                        }
                    else:
                        reading = {
                            **group_result,
                            "success": False,
                            "status": group_result.get("status", "unsupported"),
                            "reason": group_result.get("reason", "CAMPO_NO_DEVUELTO_POR_ESTA_ECU"),
                        }
                    field = (
                        group_result["fields"][position]
                        if group_result.get("success") and position < returned_count
                        else {}
                    )
                    live_signals.append({
                        "pid_name": pid_name,
                        "label": label,
                        "category": category_for_group(group_number),
                        "group_title": title,
                        "group_number": group_number,
                        "position": position + 1,
                        "type_id": f"{field.get('type_id'):02X}" if field.get("type_id") is not None else "",
                        "mode": "KWP_21",
                        "pid": f"{group_number:03d}.{position + 1}",
                        "unit": reading.get("unit", definition.unit if definition else "valor"),
                        "supported_reported": bool(group_result.get("success")),
                        "supported_verified": bool(reading.get("success")),
                        "status": reading.get("status", "unknown"),
                        "reason": reading.get("reason", ""),
                        "avg_latency_ms": reading.get("latency_ms", group_result.get("latency_ms", 0.0)),
                        "success_rate": 1.0 if reading.get("success") else 0.0,
                        "source": "vag_kwp2000_inventory",
                        "ecu_address": "01/TP2.0",
                        "sample_value": reading.get("value"),
                        "raw_response": reading.get("raw_response", group_result.get("raw_response", "")),
                    })
            verified = [item for item in live_signals if item["supported_verified"]]
            responding_groups = [group for group, result in groups.items() if result.get("success")]
            category_summary: Dict[str, Dict[str, int]] = {}
            for item in live_signals:
                summary = category_summary.setdefault(
                    item["category"], {"total": 0, "verified": 0, "unavailable": 0}
                )
                summary["total"] += 1
                if item["supported_verified"]:
                    summary["verified"] += 1
                else:
                    summary["unavailable"] += 1
            return {
                "protocol": "VAG KWP2000 sobre TP2.0, bloques de medida 0x21, solo lectura",
                "ecu_address": "01/TP2.0",
                "identified": bool(identity),
                "ecu_part_number": identity.get("long_identification", ""),
                "standard_obd_identity": standard_identity or {},
                "kwp_identity": identity,
                "identity": [],
                "live_signals": live_signals,
                "verified_live_signal_count": len(verified),
                "documented_group_count": len(DOCUMENTED_GROUPS),
                "tested_group_count": len(groups),
                "responding_group_count": len(responding_groups),
                "documented_field_count": documented_field_count(),
                "tested_field_count": len(live_signals),
                "coverage_percent": round(100.0 * len(verified) / len(live_signals), 1) if live_signals else 0.0,
                "mapping_required_count": sum(item["status"] == "undecoded" for item in live_signals),
                "category_summary": category_summary,
                "unsupported_groups": sorted(group for group, result in groups.items() if not result.get("success")),
                "responding_groups": responding_groups,
                "exhaustive": exhaustive,
                "safety": "Solo sesión diagnóstica y lectura 0x21. Sin escritura, codificación, adaptación, rutinas ni borrado.",
                "transcript": self.transport.transcript,
            }
        finally:
            self.close()


__all__ = [
    "KWP_SIGNALS",
    "ALL_KWP_SIGNALS",
    "CATALOG_KWP_SIGNALS",
    "RUNTIME_KWP_SIGNALS",
    "Tp20Transport",
    "VagKwp2000Client",
    "is_legacy_kwp_calibration",
    "normalize_vag_part_number",
]
