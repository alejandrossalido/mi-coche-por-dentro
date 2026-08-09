"""
Gestor de base de datos y operaciones CRUD para 'Mi Coche por Dentro'.
"""
import uuid
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from database.schema import init_db, DEFAULT_DB_PATH

class DatabaseManager:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        init_db(self.db_path)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    def close(self):
        """Cierra la conexión principal si está abierta."""
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except Exception:
                pass

    # --- VEHÍCULOS ---
    def create_vehicle(self, display_name: str, make: str = "", model: str = "",
                       year: Optional[int] = None, engine: str = "", fuel_type: str = "",
                       powertrain_type: str = "gasoline", vin_encrypted: str = "",
                       vin_hash: str = "", generation: str = "", variant: str = "",
                       engine_code: str = "", market: str = "EU") -> Dict[str, Any]:
        vehicle_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO vehicles (
                    id, vin_encrypted, vin_hash, display_name, make, model, year,
                    engine, fuel_type, powertrain_type, generation, variant,
                    engine_code, market, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    vehicle_id, vin_encrypted, vin_hash or vehicle_id,
                    display_name, make, model, year, engine, fuel_type,
                    powertrain_type, generation, variant, engine_code,
                    market, now, now
                )
            )
        return self.get_vehicle(vehicle_id)


    def get_vehicle(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_vehicles(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM vehicles ORDER BY created_at DESC")
            return [dict(r) for r in cursor.fetchall()]

    def update_vehicle_identification(
        self,
        vehicle_id: str,
        *,
        engine: Optional[str] = None,
        engine_code: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Actualiza solo la identificación mecánica confirmada por la ECU."""
        updates: List[str] = []
        values: List[Any] = []
        for column, value in (("engine", engine), ("engine_code", engine_code)):
            if value is not None:
                updates.append(f"{column} = ?")
                values.append(value)
        if not updates:
            return self.get_vehicle(vehicle_id)
        updates.append("updated_at = ?")
        values.extend((datetime.utcnow().isoformat(), vehicle_id))
        with self.get_connection() as conn:
            conn.execute(
                f"UPDATE vehicles SET {', '.join(updates)} WHERE id = ?",
                values,
            )
        return self.get_vehicle(vehicle_id)

    # --- SESIONES ---
    def create_session(self, vehicle_id: str, profile_id: Optional[str] = None,
                       engine_condition: str = "warm", notes: str = "",
                       title: str = "", symptom: str = "",
                       odometer_km: Optional[float] = None) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO sessions (
                    id, vehicle_id, profile_id, title, symptom, started_at,
                    odometer_km, engine_condition, notes, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id, vehicle_id, profile_id, title, symptom, now,
                    odometer_km, engine_condition, notes, "recording"
                )
            )
        return self.get_session(session_id)

    def stop_session(
        self,
        session_id: str,
        quality_score: float = 1.0,
        data_file: str = "",
        requested_signal_count: int = 0,
        captured_signal_count: int = 0,
        capture_coverage_percent: float = 0.0,
    ) -> Optional[Dict[str, Any]]:
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET ended_at = ?, status = 'completed', capture_quality_score = ?, data_file = ?,
                    requested_signal_count = ?, captured_signal_count = ?, capture_coverage_percent = ?
                WHERE id = ?
                """,
                (
                    now, quality_score, data_file, requested_signal_count,
                    captured_signal_count, capture_coverage_percent, session_id,
                )
            )
        return self.get_session(session_id)

    def fail_session(
        self,
        session_id: str,
        reason: str,
        data_file: str = "",
        requested_signal_count: int = 0,
        captured_signal_count: int = 0,
        capture_coverage_percent: float = 0.0,
    ) -> Optional[Dict[str, Any]]:
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET ended_at = ?, status = 'error', capture_quality_score = 0,
                    data_file = ?, notes = CASE
                        WHEN notes IS NULL OR notes = '' THEN ?
                        ELSE notes || ' | ' || ?
                    END,
                    requested_signal_count = ?, captured_signal_count = ?, capture_coverage_percent = ?
                WHERE id = ?
                """,
                (
                    now, data_file, reason, reason, requested_signal_count,
                    captured_signal_count, capture_coverage_percent, session_id,
                ),
            )
        return self.get_session(session_id)

    def interrupt_session(self, session_id: str, reason: str = "") -> Optional[Dict[str, Any]]:
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET ended_at = ?, status = 'interrupted',
                    notes = CASE
                        WHEN ? = '' THEN notes
                        WHEN notes IS NULL OR notes = '' THEN ?
                        ELSE notes || ' | ' || ?
                    END
                WHERE id = ? AND status = 'recording'
                """,
                (now, reason, reason, reason, session_id),
            )
        return self.get_session(session_id)

    def recover_interrupted_sessions(self) -> int:
        """Marca como interrumpidas capturas antiguas que quedaron abiertas."""
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET ended_at = COALESCE(ended_at, ?), status = 'interrupted',
                    notes = CASE
                        WHEN notes IS NULL OR notes = ''
                            THEN 'Recuperada tras un cierre inesperado'
                        ELSE notes || ' | Recuperada tras un cierre inesperado'
                    END
                WHERE status = 'recording'
                """,
                (now,),
            )
            return cursor.rowcount

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_sessions(self, vehicle_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            if vehicle_id:
                cursor = conn.execute("SELECT * FROM sessions WHERE vehicle_id = ? ORDER BY started_at DESC", (vehicle_id,))
            else:
                cursor = conn.execute("SELECT * FROM sessions ORDER BY started_at DESC")
            return [dict(r) for r in cursor.fetchall()]

    def update_session(
        self,
        session_id: str,
        *,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        symptom: Optional[str] = None,
        odometer_km: Optional[float] = None,
        engine_condition: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        updates: List[str] = []
        values: List[Any] = []
        for column, value in (
            ("title", title),
            ("notes", notes),
            ("symptom", symptom),
            ("odometer_km", odometer_km),
            ("engine_condition", engine_condition),
        ):
            if value is not None:
                updates.append(f"{column} = ?")
                values.append(value)
        if not updates:
            return self.get_session(session_id)
        values.append(session_id)
        with self.get_connection() as conn:
            conn.execute(
                f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?",
                values,
            )
        return self.get_session(session_id)

    # --- MARCADORES DE EVENTOS ---
    def add_event_marker(self, session_id: str, offset_ms: int, event_type: str, note: str = "") -> Dict[str, Any]:
        marker_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO event_markers (id, session_id, timestamp_offset_ms, timestamp_utc, event_type, note)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (marker_id, session_id, offset_ms, now, event_type, note)
            )
        return self.get_event_marker(marker_id)

    def get_event_marker(self, marker_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM event_markers WHERE id = ?", (marker_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_event_markers(self, session_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM event_markers WHERE session_id = ? ORDER BY timestamp_offset_ms ASC", (session_id,))
            return [dict(r) for r in cursor.fetchall()]

    # --- REPARACIONES Y MANTENIMIENTO ---
    def create_repair_action(self, vehicle_id: str, description: str, notes: str = "") -> Dict[str, Any]:
        repair_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO repair_actions (id, vehicle_id, performed_at, description, notes) VALUES (?, ?, ?, ?, ?)",
                (repair_id, vehicle_id, now, description, notes)
            )
        return self.get_repair_action(repair_id)

    def get_repair_action(self, repair_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM repair_actions WHERE id = ?", (repair_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_repair_actions(self, vehicle_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM repair_actions WHERE vehicle_id = ? ORDER BY performed_at DESC", (vehicle_id,))
            return [dict(r) for r in cursor.fetchall()]

    # --- DTC SCANS & RECORDS ---
    def record_dtc_scan(self, vehicle_id: str, scan_type: str, mil_status: bool, dtcs: List[Dict[str, str]], session_id: Optional[str] = None) -> Dict[str, Any]:
        scan_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        records: List[Dict[str, Any]] = []
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO dtc_scans (id, vehicle_id, session_id, scan_type, mil_status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (scan_id, vehicle_id, session_id, scan_type, 1 if mil_status else 0, now)
            )
            for dtc in dtcs:
                dtc_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO dtc_records (id, scan_id, code, status, description, raw_payload) VALUES (?, ?, ?, ?, ?, ?)",
                    (dtc_id, scan_id, dtc.get("code", "P0000"), dtc.get("status", "confirmed"), dtc.get("description", ""), dtc.get("raw_payload", ""))
                )
                records.append(
                    {
                        "id": dtc_id,
                        "scan_id": scan_id,
                        "code": dtc.get("code", "P0000"),
                        "status": dtc.get("status", "confirmed"),
                        "description": dtc.get("description", ""),
                        "raw_payload": dtc.get("raw_payload", ""),
                    }
                )
        return {
            "id": scan_id,
            "vehicle_id": vehicle_id,
            "session_id": session_id,
            "scan_type": scan_type,
            "mil_status": bool(mil_status),
            "created_at": now,
            "records": records,
        }
    def list_dtc_scans(self, vehicle_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM dtc_scans WHERE vehicle_id = ? ORDER BY created_at DESC", (vehicle_id,))
            return [dict(r) for r in cursor.fetchall()]

    def list_dtc_records(self, scan_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM dtc_records WHERE scan_id = ?", (scan_id,))
            return [dict(r) for r in cursor.fetchall()]

    def add_freeze_frame(
        self,
        dtc_record_id: str,
        parameter: str,
        value: float,
        unit: str = "",
    ) -> Dict[str, Any]:
        frame_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO freeze_frames (id, dtc_record_id, parameter, value, unit)
                VALUES (?, ?, ?, ?, ?)
                """,
                (frame_id, dtc_record_id, parameter, float(value), unit),
            )
        return {
            "id": frame_id,
            "dtc_record_id": dtc_record_id,
            "parameter": parameter,
            "value": float(value),
            "unit": unit,
        }

    def list_freeze_frames(self, dtc_record_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM freeze_frames
                WHERE dtc_record_id = ?
                ORDER BY parameter ASC
                """,
                (dtc_record_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    # --- VEHICLE CAPABILITIES ---
    def upsert_vehicle_capability(self, vehicle_id: str, pid_name: str, mode: str, pid: str,
                                   supported_reported: bool = True, supported_verified: bool = True,
                                   unit: str = "", avg_latency_ms: float = 0.0, success_rate: float = 1.0,
                                   source: str = "obd_generic", status: str = "", reason: str = "",
                                   ecu_address: str = "", label: str = "", category: str = "",
                                   group_title: str = "", group_number: Optional[int] = None,
                                   position: Optional[int] = None, type_id: str = "",
                                   sample_value: Optional[float] = None, raw_response: str = "") -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO vehicle_capabilities
                (vehicle_id, pid_name, mode, pid, supported_reported, supported_verified, unit,
                 avg_latency_ms, success_rate, source, status, reason, ecu_address, label,
                 category, group_title, group_number, position, type_id, sample_value, raw_response,
                 last_verified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(vehicle_id, pid_name) DO UPDATE SET
                    mode = excluded.mode,
                    pid = excluded.pid,
                    supported_reported = excluded.supported_reported,
                    supported_verified = excluded.supported_verified,
                    unit = excluded.unit,
                    avg_latency_ms = excluded.avg_latency_ms,
                    success_rate = excluded.success_rate,
                    source = excluded.source,
                    status = excluded.status,
                    reason = excluded.reason,
                    ecu_address = excluded.ecu_address,
                    label = excluded.label,
                    category = excluded.category,
                    group_title = excluded.group_title,
                    group_number = excluded.group_number,
                    position = excluded.position,
                    type_id = excluded.type_id,
                    sample_value = excluded.sample_value,
                    raw_response = excluded.raw_response,
                    last_verified_at = excluded.last_verified_at
                """,
                (vehicle_id, pid_name, mode, pid, 1 if supported_reported else 0, 1 if supported_verified else 0,
                 unit, avg_latency_ms, success_rate, source, status, reason, ecu_address, label,
                 category, group_title, group_number, position, type_id, sample_value, raw_response, now)
            )
        return {"vehicle_id": vehicle_id, "pid_name": pid_name, "verified": supported_verified}

    def list_vehicle_capabilities(self, vehicle_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM vehicle_capabilities WHERE vehicle_id = ?", (vehicle_id,))
            return [dict(r) for r in cursor.fetchall()]
