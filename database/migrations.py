"""Migraciones SQLite incrementales y no destructivas."""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from app_paths import backups_path

logger = logging.getLogger(__name__)

MIGRATIONS: List[Dict[str, Any]] = [
    {
        "version": 1,
        "description": "Añadir columna powertrain_type a la tabla vehicles",
        "script": """
            ALTER TABLE vehicles ADD COLUMN powertrain_type TEXT DEFAULT 'gasoline';
        """,
    },
    {
        "version": 2,
        "description": "Versión reservada de una migración anterior",
        "script": """
            SELECT 1;
        """,
    },
    {
        "version": 3,
        "description": "Eliminar escaneos DTC sintéticos creados por versiones antiguas sin ECU",
        "required_tables": ["dtc_scans", "dtc_records"],
        "script": """
            CREATE TEMP TABLE legacy_synthetic_scans AS
            SELECT scan_id
            FROM dtc_records
            GROUP BY scan_id
            HAVING COUNT(*) = 2
               AND SUM(CASE WHEN code = 'P0171' AND raw_payload = '0171' THEN 1 ELSE 0 END) = 1
               AND SUM(CASE WHEN code = 'P0300' AND raw_payload = '0300' THEN 1 ELSE 0 END) = 1;

            DELETE FROM dtc_records
            WHERE scan_id IN (SELECT scan_id FROM legacy_synthetic_scans);

            DELETE FROM dtc_scans
            WHERE id IN (SELECT scan_id FROM legacy_synthetic_scans);

            DROP TABLE legacy_synthetic_scans;
        """,
    },
    {
        "version": 4,
        "description": "Separar identidad comercial y tecnica de los vehiculos",
        "required_tables": ["vehicles"],
        "columns": {
            "generation": "TEXT DEFAULT ''",
            "variant": "TEXT DEFAULT ''",
            "engine_code": "TEXT DEFAULT ''",
            "market": "TEXT DEFAULT 'EU'",
        },
        "script": """
            SELECT 1;
        """,
    },
    {
        "version": 5,
        "description": "Añadir nombre y síntoma estructurado a las sesiones",
        "required_tables": ["sessions"],
        "columns_by_table": {
            "sessions": {
                "title": "TEXT DEFAULT ''",
                "symptom": "TEXT DEFAULT ''",
            },
        },
        "script": """
            UPDATE sessions
            SET title = COALESCE(NULLIF(notes, ''), 'Sesión de diagnóstico')
            WHERE title IS NULL OR title = '';
        """,
    },
    {
        "version": 6,
        "description": "Registrar procedencia y diagnóstico de capacidades OBD y Volkswagen",
        "required_tables": ["vehicle_capabilities"],
        "columns_by_table": {
            "vehicle_capabilities": {
                "source": "TEXT DEFAULT 'obd_generic'",
                "status": "TEXT DEFAULT ''",
                "reason": "TEXT DEFAULT ''",
                "ecu_address": "TEXT DEFAULT ''",
            },
        },
        "script": """
            UPDATE vehicle_capabilities
            SET source = COALESCE(NULLIF(source, ''), 'obd_generic'),
                status = CASE
                    WHEN status IS NOT NULL AND status != '' THEN status
                    WHEN supported_verified = 1 THEN 'compatible'
                    WHEN supported_reported = 1 THEN 'unresponsive'
                    ELSE 'unsupported'
                END;
        """,
    },
    {
        "version": 7,
        "description": "Guardar inventario completo y evidencia bruta de bloques Volkswagen",
        "required_tables": ["vehicle_capabilities"],
        "columns_by_table": {
            "vehicle_capabilities": {
                "label": "TEXT DEFAULT ''",
                "category": "TEXT DEFAULT ''",
                "group_title": "TEXT DEFAULT ''",
                "group_number": "INTEGER",
                "position": "INTEGER",
                "type_id": "TEXT DEFAULT ''",
                "sample_value": "REAL",
                "raw_response": "TEXT DEFAULT ''",
            },
        },
        "script": """
            UPDATE vehicle_capabilities
            SET label = COALESCE(label, ''),
                category = COALESCE(category, ''),
                group_title = COALESCE(group_title, ''),
                type_id = COALESCE(type_id, ''),
                raw_response = COALESCE(raw_response, '');
        """,
    },
    {
        "version": 8,
        "description": "Conservar la cobertura real de señales de cada sesión",
        "required_tables": ["sessions"],
        "columns_by_table": {
            "sessions": {
                "requested_signal_count": "INTEGER DEFAULT 0",
                "captured_signal_count": "INTEGER DEFAULT 0",
                "capture_coverage_percent": "REAL DEFAULT 0",
            },
        },
        "script": """
            UPDATE sessions
            SET requested_signal_count = COALESCE(requested_signal_count, 0),
                captured_signal_count = COALESCE(captured_signal_count, 0),
                capture_coverage_percent = COALESCE(capture_coverage_percent, 0);
        """,
    },
]


def _backup_database(conn: sqlite3.Connection, db_path: str) -> Path:
    backup_name = f"{Path(db_path).stem}-{datetime.now():%Y%m%d-%H%M%S-%f}.db"
    backup_file = backups_path() / backup_name
    with sqlite3.connect(str(backup_file)) as backup_conn:
        conn.backup(backup_conn)
    logger.info("Copia de seguridad previa a migraciones: %s", backup_file)
    return backup_file


def run_migrations(db_path: str) -> None:
    """Ejecuta solo migraciones pendientes y no oculta fallos reales."""
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
                """
            )
            applied_versions = {
                row["version"]
                for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
            }
            pending = [
                migration
                for migration in MIGRATIONS
                if migration["version"] not in applied_versions
            ]
            if pending:
                _backup_database(conn, db_path)

            for migration in pending:
                version = migration["version"]
                logger.info("Aplicando migración v%s: %s", version, migration["description"])
                required_tables = migration.get("required_tables", [])
                existing_tables = {
                    row["name"]
                    for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    ).fetchall()
                }
                try:
                    if all(table in existing_tables for table in required_tables):
                        column_definitions = migration.get("columns", {})
                        if column_definitions:
                            existing_columns = {
                                row["name"]
                                for row in conn.execute("PRAGMA table_info(vehicles)").fetchall()
                            }
                            for column_name, column_type in column_definitions.items():
                                if column_name not in existing_columns:
                                    conn.execute(
                                        f"ALTER TABLE vehicles ADD COLUMN {column_name} {column_type}"
                                    )
                        for table_name, table_columns in migration.get("columns_by_table", {}).items():
                            existing_columns = {
                                row["name"]
                                for row in conn.execute(
                                    f"PRAGMA table_info({table_name})"
                                ).fetchall()
                            }
                            for column_name, column_type in table_columns.items():
                                if column_name not in existing_columns:
                                    conn.execute(
                                        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                                    )
                        conn.executescript(migration["script"])
                    else:
                        logger.info(
                            "La migración v%s no aplica: faltan tablas opcionales %s.",
                            version,
                            required_tables,
                        )
                except sqlite3.OperationalError as exc:
                    duplicate_v1_column = (
                        version == 1 and "duplicate column name" in str(exc).lower()
                    )
                    if not duplicate_v1_column:
                        logger.exception("Falló la migración v%s", version)
                        raise
                    logger.info(
                        "La columna de migración v1 ya existía; se registra como aplicada."
                    )

                conn.execute(
                    "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
                    (version, migration["description"]),
                )
    finally:
        conn.close()
