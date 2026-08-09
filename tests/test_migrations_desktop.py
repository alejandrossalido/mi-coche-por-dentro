import sqlite3

from database.migrations import run_migrations


def test_migrations_create_backup_and_preserve_existing_rows(monkeypatch, tmp_path):
    monkeypatch.setenv("MICOCHE_HOME", str(tmp_path / "profile"))
    database = tmp_path / "legacy.db"
    with sqlite3.connect(database) as conn:
        conn.executescript(
            """
            CREATE TABLE vehicles (
                id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                engine TEXT,
                fuel_type TEXT
            );
            INSERT INTO vehicles (id, display_name, engine, fuel_type)
            VALUES ('custom', 'Vehículo del usuario', 'motor', 'fuel');
            """
        )

    run_migrations(str(database))

    with sqlite3.connect(database) as conn:
        assert conn.execute(
            "SELECT display_name FROM vehicles WHERE id = 'custom'"
        ).fetchone()[0] == "Vehículo del usuario"
        columns = {row[1] for row in conn.execute("PRAGMA table_info(vehicles)")}
        versions = {row[0] for row in conn.execute("SELECT version FROM schema_migrations")}
    assert "powertrain_type" in columns
    assert {"generation", "variant", "engine_code", "market"} <= columns
    assert versions == {1, 2, 3, 4, 5, 6, 7, 8}
    assert list((tmp_path / "profile" / "backups").glob("legacy-*.db"))
