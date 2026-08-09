"""
Tests unitarios para las extensiones avanzadas: Mode06Analyzer, RepairActions y VehicleBackupExporter.
"""
import pytest
import os
from collector.mode06 import Mode06Analyzer
from database.db import DatabaseManager
from database.exporter import VehicleBackupExporter

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_ext_vehicle.db")
TEST_ZIP_PATH = os.path.join(os.path.dirname(__file__), "test_export.zip")

@pytest.fixture(autouse=True)
def cleanup():
    import gc
    gc.collect()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    if os.path.exists(TEST_ZIP_PATH):
        try:
            os.remove(TEST_ZIP_PATH)
        except Exception:
            pass
    yield
    gc.collect()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    if os.path.exists(TEST_ZIP_PATH):
        try:
            os.remove(TEST_ZIP_PATH)
        except Exception:
            pass


def test_mode06_analyzer():
    monitors = Mode06Analyzer.get_mode06_monitors("v1")
    assert monitors == []

def test_repair_actions_and_exporter():
    db = DatabaseManager(db_path=TEST_DB_PATH)
    v = db.create_vehicle(display_name="VW Golf", make="VW", model="Golf", year=2019)
    
    r = db.create_repair_action(vehicle_id=v["id"], description="Sustitución de Bujías", notes="NGK Iridium")
    assert r["id"] is not None
    
    repairs = db.list_repair_actions(v["id"])
    assert len(repairs) == 1

    exporter = VehicleBackupExporter(db_manager=db)
    zip_res = exporter.export_vehicle_zip(v["id"], TEST_ZIP_PATH)
    assert os.path.exists(zip_res)
    db.close()
