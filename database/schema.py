"""
Esquema de base de datos SQLite para 'Mi Coche por Dentro'.
Define las tablas para metadatos de vehículos, adaptadores, escaneos DTC, sesiones y análisis.
"""
import sqlite3
import os
from app_paths import database_path

DEFAULT_DB_PATH = str(database_path())

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS vehicles (
    id TEXT PRIMARY KEY,
    vin_encrypted TEXT,
    vin_hash TEXT UNIQUE,
    display_name TEXT NOT NULL,
    make TEXT,
    model TEXT,
    year INTEGER,
    engine TEXT,
    fuel_type TEXT,
    powertrain_type TEXT DEFAULT 'gasoline',
    generation TEXT DEFAULT '',
    variant TEXT DEFAULT '',
    engine_code TEXT DEFAULT '',
    market TEXT DEFAULT 'EU',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS adapters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    serial_number TEXT,
    firmware_version TEXT,
    preferred_com_port TEXT,
    last_seen_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vehicle_capabilities (
    vehicle_id TEXT NOT NULL,
    pid_name TEXT NOT NULL,
    mode TEXT NOT NULL,
    pid TEXT NOT NULL,
    supported_reported INTEGER DEFAULT 0,
    supported_verified INTEGER DEFAULT 0,
    unit TEXT,
    avg_latency_ms REAL,
    success_rate REAL,
    source TEXT DEFAULT 'obd_generic',
    status TEXT DEFAULT '',
    reason TEXT DEFAULT '',
    ecu_address TEXT DEFAULT '',
    label TEXT DEFAULT '',
    category TEXT DEFAULT '',
    group_title TEXT DEFAULT '',
    group_number INTEGER,
    position INTEGER,
    type_id TEXT DEFAULT '',
    sample_value REAL,
    raw_response TEXT DEFAULT '',
    last_verified_at TIMESTAMP,
    PRIMARY KEY (vehicle_id, pid_name),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dtc_scans (
    id TEXT PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    session_id TEXT,
    scan_type TEXT NOT NULL, -- 'initial', 'final', 'manual'
    mil_status INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dtc_records (
    id TEXT PRIMARY KEY,
    scan_id TEXT NOT NULL,
    code TEXT NOT NULL,
    status TEXT, -- 'confirmed', 'pending', 'permanent'
    description TEXT,
    raw_payload TEXT,
    FOREIGN KEY (scan_id) REFERENCES dtc_scans(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS freeze_frames (
    id TEXT PRIMARY KEY,
    dtc_record_id TEXT NOT NULL,
    parameter TEXT NOT NULL,
    value REAL,
    unit TEXT,
    FOREIGN KEY (dtc_record_id) REFERENCES dtc_records(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS capture_profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    signal_configuration_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    profile_id TEXT,
    title TEXT DEFAULT '',
    symptom TEXT DEFAULT '',
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    odometer_km REAL,
    engine_condition TEXT, -- 'cold', 'warm', 'hot'
    notes TEXT,
      data_file TEXT, -- ruta al archivo parquet
      capture_quality_score REAL,
      requested_signal_count INTEGER DEFAULT 0,
      captured_signal_count INTEGER DEFAULT 0,
      capture_coverage_percent REAL DEFAULT 0,
      status TEXT NOT NULL, -- 'recording', 'completed', 'interrupted', 'error'
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES capture_profiles(id)
);

CREATE TABLE IF NOT EXISTS event_markers (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp_offset_ms INTEGER NOT NULL,
    timestamp_utc TIMESTAMP NOT NULL,
    event_type TEXT NOT NULL, -- 'jerk', 'power_loss', 'smoke', 'vibration', etc.
    note TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    analysis_version TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    analysis_run_id TEXT NOT NULL,
    finding_type TEXT NOT NULL,
    severity TEXT NOT NULL, -- 'info', 'warning', 'critical'
    confidence REAL NOT NULL,
    start_ms INTEGER,
    end_ms INTEGER,
    evidence_json TEXT,
    message TEXT NOT NULL,
    FOREIGN KEY (analysis_run_id) REFERENCES analysis_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS repair_actions (
    id TEXT PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    performed_at TIMESTAMP NOT NULL,
    description TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);
"""

def init_db(db_path: str = DEFAULT_DB_PATH):
    """Inicializa la base de datos SQLite creando tablas y ejecutando migraciones no destructivas."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        with conn:
            conn.executescript(CREATE_TABLES_SQL)
            capture_profiles = [
                ("COMPLETE_DIAGNOSTIC", "Diagnóstico completo guiado"),
                ("COLD_START", "Arranque en frío"),
                ("IDLE_STABILITY", "Estabilidad de ralentí"),
                ("CONTROLLED_ACCELERATION", "Aceleración controlada"),
                ("WARMUP_CURVE", "Curva de calentamiento"),
                ("CUSTOM", "Prueba personalizada"),
                ("BATTERY_CHARGING", "Batería y sistema de carga"),
                ("COOLING_SYSTEM", "Sistema de refrigeración"),
                ("INTAKE_TURBO", "Admisión y sobrealimentación"),
                ("FUEL_MIXTURE", "Combustible y mezcla"),
                ("EMISSIONS_ITV", "Emisiones e ITV"),
            ]
            conn.executemany(
                """
                INSERT OR IGNORE INTO capture_profiles (
                    id, name, description, signal_configuration_json
                )
                VALUES (?, ?, '', '{}')
                """,
                capture_profiles,
            )
            # Los vehículos son datos del usuario. Una instalación nueva debe
            # arrancar con el garaje vacío y permitir que cada persona añada los suyos.
    finally:
        conn.close()

    # Ejecutar migraciones no destructivas
    from database.migrations import run_migrations
    run_migrations(db_path)
