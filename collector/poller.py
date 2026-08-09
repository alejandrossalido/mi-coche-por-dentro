"""
Planificador y Bucle de Muestreo de Telemetría (poller).
Prioriza PIDs de alta frecuencia (RPM, Carga, MAP) y baja frecuencia (Temperaturas),
registrando marcas temporales monotónicas y guardando datos en Parquet.
"""
import os
import time
import math
import random
import threading
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from database.parquet_store import TelemetryStore


try:
    import obd
    from obd import commands
except ImportError:
    obd = None
    commands = None

logger = logging.getLogger(__name__)

# PIDs prioritarios (alta frecuencia) vs secundarios (baja frecuencia)
FAST_PIDS = [
    "RPM", "SPEED", "ENGINE_LOAD", "THROTTLE_POS", "MAF", "INTAKE_PRESSURE",
    "ACCELERATOR_POS_D", "ACCELERATOR_POS_E", "RELATIVE_ACCEL_POS",
    "COMMANDED_EGR", "EGR_ERROR", "FUEL_RAIL_PRESSURE_DIRECT",
    "FUEL_RAIL_PRESSURE_ABS",
    "VAG_ACCELERATOR_POSITION", "VAG_EGR_COMMAND", "VAG_EGR_ACTUAL",
    "VAG_EGR_DUTY_CYCLE", "VAG_AIR_MASS_ACTUAL", "VAG_INJECTION_QUANTITY",
    "VAG_FUEL_RATE", "VAG_ENGINE_TORQUE", "VAG_DRIVER_TORQUE_REQUEST",
    "VAG_RAIL_PRESSURE_REQUESTED", "VAG_RAIL_PRESSURE_ACTUAL",
    "VAG_BOOST_PRESSURE_REQUESTED", "VAG_BOOST_PRESSURE_ACTUAL",
]
SLOW_PIDS = [
    "COOLANT_TEMP", "INTAKE_TEMP", "OIL_TEMP", "AMBIANT_AIR_TEMP",
    "CATALYST_TEMP_B1S1", "CATALYST_TEMP_B2S1", "CATALYST_TEMP_B1S2",
    "CATALYST_TEMP_B2S2", "BAROMETRIC_PRESSURE", "CONTROL_MODULE_VOLTAGE",
    "ELM_VOLTAGE", "RUN_TIME", "FUEL_STATUS", "FUEL_PRESSURE",
    "COMMANDED_EQUIV_RATIO", "FUEL_INJECT_TIMING", "FUEL_RATE",
    "VAG_OIL_TEMP", "VAG_AMBIENT_TEMP", "VAG_EXHAUST_TEMP_1",
    "VAG_EXHAUST_TEMP_2", "VAG_BAROMETRIC_PRESSURE", "VAG_INJECTION_TIMING",
    "VAG_FUEL_TEMP", "VAG_INJECTION_DURATION", "VAG_INJECTION_DURATION_2",
    "VAG_TORSION_VALUE",
    "VAG_ALTERNATOR_LOAD", "VAG_CAMSHAFT_SPEED", "VAG_RADIATOR_OUTLET_TEMP",
    "VAG_COOLING_FAN_COMMAND",
    "VAG_INJECTOR_DEVIATION_1", "VAG_INJECTOR_DEVIATION_2",
    "VAG_INJECTOR_DEVIATION_3", "VAG_INJECTOR_DEVIATION_4",
    "VAG_INJECTOR_STATUS_1", "VAG_INJECTOR_STATUS_2",
    "VAG_INJECTOR_STATUS_3", "VAG_INJECTOR_STATUS_4",
    "VAG_INJECTOR_SWITCH_TIME_1", "VAG_INJECTOR_SWITCH_TIME_2",
    "VAG_INJECTOR_SWITCH_TIME_3", "VAG_INJECTOR_SWITCH_TIME_4",
    "VAG_DPF_SOOT_CALCULATED", "VAG_DPF_SOOT_MEASURED",
    "VAG_DPF_SOOT_PERCENT", "VAG_DPF_ASH_MASS",
    "VAG_DPF_DIFFERENTIAL_PRESSURE", "VAG_DPF_DISTANCE_SINCE_REGEN",
    "VAG_DPF_TIME_SINCE_REGEN", "VAG_DPF_REGEN_STATUS", "VAG_ECU_VOLTAGE",
]

FUEL_STATUS_CODES = {
    "": 0.0,
    "Open loop due to insufficient engine temperature": 1.0,
    "Closed loop, using oxygen sensor feedback to determine fuel mix": 2.0,
    "Open loop due to engine load OR fuel cut due to deceleration": 4.0,
    "Open loop due to system failure": 8.0,
    "Closed loop, using at least one oxygen sensor but there is a fault in the feedback system": 16.0,
}

class TelemetryPoller:
    def __init__(
        self,
        session_id: str,
        adapter_connection=None,
        telemetry_store: Optional[TelemetryStore] = None,
        pids: Optional[List[str]] = None,
        oem_reader: Any = None,
    ):
        self.session_id = session_id
        self.connection = adapter_connection
        self.oem_reader = oem_reader
        self.store = telemetry_store or TelemetryStore()
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._sample_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._samples_buffer: List[Dict[str, Any]] = []
        self._buffer_lock = threading.Lock()
        self.sample_count = 0
        self.valid_sample_count = 0
        self.invalid_sample_count = 0
        self.start_monotonic = 0.0
        self.last_valid_monotonic = 0.0
        self.poll_in_progress = False
        self.poll_started_monotonic = 0.0
        self.last_read_error = ""
        self.abort_reason: Optional[str] = None
        self.pids = list(dict.fromkeys(pids or (FAST_PIDS + SLOW_PIDS)))
        self.attempted_pids: set[str] = set()
        self.valid_pids: set[str] = set()
        self.valid_counts_by_pid: Dict[str, int] = {}

    def register_sample_callback(self, callback: Callable[[Dict[str, Any]], None]):
        self._sample_callbacks.append(callback)

    def start(self, poll_interval_ms: int = 100):
        """Inicia el bucle de muestreo en un hilo secundario."""
        if self.is_running:
            return
        self.is_running = True
        self.start_monotonic = time.monotonic()
        self.last_valid_monotonic = 0.0
        self.poll_in_progress = False
        self.poll_started_monotonic = 0.0
        self._thread = threading.Thread(target=self._poll_loop, args=(poll_interval_ms / 1000.0,), daemon=True)
        self._thread.start()

    def stop(self):
        """Detiene el bucle de muestreo y vuelca el búfer a Parquet."""
        self.is_running = False
        if self._thread and self._thread.is_alive():
            # Una respuesta TP2.0 puede agotar el timeout serie de 3 s. No se
            # debe cerrar el canal por debajo del hilo que todavía lo usa.
            self._thread.join(timeout=5.0 if self.oem_reader else 2.0)
        self.flush_buffer()
        if self.oem_reader and hasattr(self.oem_reader, "close"):
            try:
                self.oem_reader.close()
            except Exception:
                logger.warning("No se pudo cerrar el lector de fabricante.", exc_info=True)

    def flush_buffer(self):
        """Escribe las muestras acumuladas en el archivo Parquet de la sesión."""
        samples_to_write = []
        with self._buffer_lock:
            if self._samples_buffer:
                samples_to_write = list(self._samples_buffer)
                self._samples_buffer.clear()

        if samples_to_write:
            try:
                self.store.save_samples(self.session_id, samples_to_write)
            except Exception as e:
                logger.error(f"Error guardando muestras Parquet, reinsertando en buffer: {e}")
                with self._buffer_lock:
                    self._samples_buffer = samples_to_write + self._samples_buffer
                raise e

    def _generate_simulated_sample(self, pid_name: str, elapsed: float) -> float:
        """Genera valores simulación realistas para pruebas de telemetría sin coche conectado."""
        if pid_name == "RPM":
            return round(800 + 1500 * math.sin(elapsed / 5.0) + random.uniform(-20, 20), 1)
        elif pid_name == "SPEED":
            return round(max(0.0, 50.0 + 30.0 * math.sin(elapsed / 10.0) + random.uniform(-2, 2)), 1)
        elif pid_name == "COOLANT_TEMP":
            return round(min(90.0, 20.0 + elapsed * 0.5), 1)
        elif pid_name == "INTAKE_TEMP":
            return round(25.0 + random.uniform(-0.5, 0.5), 1)
        elif pid_name == "ENGINE_LOAD":
            return round(max(10.0, 30.0 + 20.0 * math.sin(elapsed / 4.0) + random.uniform(-3, 3)), 1)
        elif pid_name == "THROTTLE_POS":
            return round(max(0.0, 15.0 + 25.0 * math.sin(elapsed / 4.0) + random.uniform(-1, 1)), 1)
        elif pid_name == "MAF":
            return round(max(2.0, 10.0 + 15.0 * math.sin(elapsed / 5.0) + random.uniform(-0.5, 0.5)), 2)
        elif pid_name == "INTAKE_PRESSURE":
            return round(max(30.0, 101.0 - 40.0 * math.sin(elapsed / 5.0)), 1)
        elif pid_name == "CONTROL_MODULE_VOLTAGE":
            return round(14.2 + random.uniform(-0.1, 0.1), 2)
        elif pid_name == "RUN_TIME":
            return round(elapsed, 1)
        return 0.0

    def _poll_loop(self, interval_sec: float):
        # La primera vuelta incluye todas las señales. Así incluso una captura
        # corta deja al menos una instantánea completa de lo solicitado.
        slow_counter = 9
        app_mode = os.getenv("APP_MODE", "production").lower()
        fast_pids = [pid for pid in self.pids if pid in FAST_PIDS]
        slow_pids = [pid for pid in self.pids if pid not in FAST_PIDS]

        while self.is_running:
            loop_start = time.monotonic()
            self.poll_in_progress = True
            self.poll_started_monotonic = loop_start
            elapsed_sec = loop_start - self.start_monotonic
            utc_now = datetime.utcnow().isoformat() + "Z"

            # PIDs a consultar en esta vuelta
            pids_to_poll = list(fast_pids)
            slow_counter += 1
            if slow_counter >= 10 or not pids_to_poll:  # PIDs lentos cada 10 ciclos
                pids_to_poll.extend(slow_pids)
                slow_counter = 0

            batch_readings: Dict[str, Dict[str, Any]] = {}
            if self.oem_reader and hasattr(self.oem_reader, "read_signals_batch"):
                oem_pids = [
                    pid for pid in pids_to_poll
                    if pid in getattr(self.oem_reader, "signal_names", set())
                ]
                if oem_pids:
                    try:
                        batch_readings = self.oem_reader.read_signals_batch(oem_pids)
                    except Exception as exc:
                        logger.warning("Falló la lectura agrupada Volkswagen: %s", exc)
                        self.last_read_error = str(exc)

            for pid_name in pids_to_poll:
                val = None
                sample_elapsed = elapsed_sec
                unit = ""
                raw_response = ""
                latency = 0.0
                data_source = "measured"
                quality = 1.0

                if self.oem_reader and pid_name in getattr(self.oem_reader, "signal_names", set()):
                    try:
                        reading = batch_readings.get(pid_name)
                        if reading is None:
                            reading = self.oem_reader.read_signal(pid_name)
                        latency = float(reading.get("latency_ms", 0.0))
                        if reading.get("success"):
                            val = float(reading["value"])
                            captured_monotonic = reading.get("captured_monotonic")
                            if isinstance(captured_monotonic, (int, float)) and math.isfinite(captured_monotonic):
                                sample_elapsed = max(0.0, float(captured_monotonic) - self.start_monotonic)
                            unit = str(reading.get("unit", ""))
                            raw_response = str(reading.get("raw_response", ""))
                            data_source = str(reading.get("data_source", "measured_vag_uds"))
                        else:
                            status = str(reading.get("status", "sin_respuesta"))
                            reason = str(reading.get("reason", status))
                            raw_response = str(reading.get("raw_response", "")) or reason
                            data_source = f"measured_error_{status}"
                            self.last_read_error = reason
                    except Exception as exc:
                        logger.warning("Fallo consultando señal Volkswagen %s: %s", pid_name, exc)
                        raw_response = str(exc)
                        data_source = "measured_error_exception"
                        self.last_read_error = str(exc)
                elif self.connection and hasattr(self.connection, "query") and commands:
                    cmd = getattr(commands, pid_name, None)
                    if cmd:
                        t0 = time.time()
                        try:
                            resp = self.connection.query(cmd)
                            latency = (time.time() - t0) * 1000.0
                            if resp and not resp.is_null():
                                if pid_name == "FUEL_STATUS":
                                    statuses = resp.value if isinstance(resp.value, (tuple, list)) else [resp.value]
                                    primary_status = str(statuses[0] if statuses else "")
                                    raw_response = primary_status
                                    val = FUEL_STATUS_CODES.get(primary_status, 0.0)
                                    unit = "state_code"
                                else:
                                    val = float(resp.value.magnitude) if hasattr(resp.value, "magnitude") else float(resp.value)
                                    unit = str(resp.value.units) if hasattr(resp.value, "units") else ""
                        except Exception as exc:
                            latency = (time.time() - t0) * 1000.0
                            logger.warning("Fallo consultando %s: %s", pid_name, exc)
                            raw_response = str(exc)
                            data_source = "measured_error_exception"
                            self.last_read_error = str(exc)

                if val is None:
                    if app_mode in ["demo", "simulated"]:
                        val = self._generate_simulated_sample(pid_name, elapsed_sec)
                        latency = 5.0
                        data_source = "simulated"
                        quality = 0.5
                    else:
                        val = None
                        if not raw_response:
                            raw_response = "SIN_RESPUESTA_DE_LA_ECU"
                        if data_source == "measured":
                            data_source = "measured_no_response"
                        quality = 0.0

                sample = {
                    "session_id": self.session_id,
                    "timestamp_monotonic": round(sample_elapsed, 3),
                    "timestamp_utc": utc_now,
                    "pid": pid_name,
                    "value": val,
                    "unit": unit,
                    "ecu": "ENGINE",
                    "quality": quality,
                    "latency_ms": round(latency, 2),
                    "raw_response": raw_response,
                    "data_source": data_source
                }

                should_flush = False
                with self._buffer_lock:
                    self._samples_buffer.append(sample)
                    self.sample_count += 1
                    self.attempted_pids.add(pid_name)
                    if val is None:
                        self.invalid_sample_count += 1
                    else:
                        self.valid_sample_count += 1
                        self.valid_pids.add(pid_name)
                        self.valid_counts_by_pid[pid_name] = self.valid_counts_by_pid.get(pid_name, 0) + 1
                        # Una lectura agrupada puede durar bastantes segundos.
                        # La frescura empieza cuando procesamos el resultado.
                        self.last_valid_monotonic = time.monotonic()
                    should_flush = len(self._samples_buffer) >= 50

                if should_flush:
                    try:
                        self.flush_buffer()
                    except Exception:
                        pass



                # Notificar a callbacks (WebSocket, UI dashboard, etc.)
                for cb in self._sample_callbacks:
                    try:
                        cb(sample)
                    except Exception as e:
                        logger.error(f"Error in telemetry callback: {e}")

            self.poll_in_progress = False

            # Stop early when the adapter is connected but the ECU is returning
            # no usable values. This prevents a long, misleading empty session.
            if (
                app_mode not in ["demo", "simulated"]
                and elapsed_sec >= 8.0
                and self.sample_count >= 50
                and self.valid_sample_count == 0
            ):
                self.abort_reason = "NO_VALID_OBD_DATA"
                self.is_running = False
                try:
                    self.flush_buffer()
                except Exception:
                    pass
                break

            # También detener una captura que empezó bien pero perdió después
            # la ECU. La sesión anterior del Passat quedó 7 minutos rellenando
            # nulos porque solo se comprobaba el caso de cero lecturas totales.
            if (
                app_mode not in ["demo", "simulated"]
                and self.last_valid_monotonic
                and time.monotonic() - self.last_valid_monotonic >= 20.0
            ):
                self.abort_reason = "OBD_DATA_LOST"
                self.is_running = False
                try:
                    self.flush_buffer()
                except Exception:
                    pass
                break

            # Mantener frecuencia objetivo
            elapsed_loop = time.monotonic() - loop_start
            sleep_time = max(0.001, interval_sec - elapsed_loop)
            time.sleep(sleep_time)

    def get_metrics(self) -> Dict[str, Any]:
        now = time.monotonic()
        elapsed = max(0.0, now - self.start_monotonic) if self.start_monotonic else 0.0
        last_valid_age = max(0.0, now - self.last_valid_monotonic) if self.last_valid_monotonic else None
        poll_age = max(0.0, now - self.poll_started_monotonic) if self.poll_in_progress else 0.0
        valid_ratio = self.valid_sample_count / self.sample_count if self.sample_count else 0.0
        requested_count = len(self.pids)
        captured_count = len(self.valid_pids)
        missing_pids = [pid for pid in self.pids if pid not in self.valid_pids]
        return {
            "sample_count": self.sample_count,
            "valid_sample_count": self.valid_sample_count,
            "invalid_sample_count": self.invalid_sample_count,
            "valid_ratio": round(valid_ratio, 3),
            "elapsed_sec": round(elapsed, 1),
            "last_valid_age_sec": round(last_valid_age, 1) if last_valid_age is not None else None,
            "poll_in_progress": self.poll_in_progress,
            "poll_age_sec": round(poll_age, 1),
            "abort_reason": self.abort_reason,
            "last_read_error": self.last_read_error,
            "oem_recovery_count": int(getattr(self.oem_reader, "recovery_count", 0) or 0),
            "pids_requested": self.pids,
            "requested_signal_count": requested_count,
            "attempted_signal_count": len(self.attempted_pids),
            "captured_signal_count": captured_count,
            "missing_signal_count": len(missing_pids),
            "capture_coverage_percent": round(100.0 * captured_count / requested_count, 1) if requested_count else 0.0,
            "missing_pids": missing_pids,
            "valid_counts_by_pid": dict(self.valid_counts_by_pid),
        }
