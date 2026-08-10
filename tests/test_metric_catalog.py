from collector.metric_catalog import metric_catalog_for_vehicle
from collector.pid_discovery import STANDARD_PIDS
from collector.vag_kwp2000 import ALL_KWP_SIGNALS
from fastapi.testclient import TestClient

import backend.main as backend_main
from database.db import DatabaseManager


def test_every_vehicle_starts_with_the_complete_standard_pid_catalog():
    rows = metric_catalog_for_vehicle({"make": "Example", "engine_code": "X1"})
    names = {row["pid_name"] for row in rows}

    assert {row[0] for row in STANDARD_PIDS}.issubset(names)
    assert len(names) >= 90
    assert all(row["status"] in {"not_tested", "mapping_required"} for row in rows)
    assert any(row["pid_name"] == "OEM_DPF_DIFFERENTIAL_PRESSURE" for row in rows)
    assert all("importance" in row for row in rows)


def test_bkp_catalog_contains_every_documented_kwp_candidate():
    rows = metric_catalog_for_vehicle({"make": "Volkswagen", "engine_code": "BKP"})
    names = {row["pid_name"] for row in rows}

    assert {definition.pid_name for definition in ALL_KWP_SIGNALS}.issubset(names)
    assert len(names) >= len(ALL_KWP_SIGNALS)


def test_real_evidence_overrides_status_without_erasing_catalog_metadata():
    rows = metric_catalog_for_vehicle(
        {"make": "Volkswagen", "engine_code": "BKP"},
        [{
            "pid_name": "VAG_CAMSHAFT_SPEED",
            "label": "",
            "category": "",
            "supported_verified": 1,
            "status": "compatible",
            "sample_value": 420.0,
            "source": "vag_kwp2000_capture",
        }],
    )
    camshaft = next(row for row in rows if row["pid_name"] == "VAG_CAMSHAFT_SPEED")

    assert camshaft["label"] == "Velocidad del árbol de levas"
    assert camshaft["category"] == "Motor, marcha y mandos"
    assert camshaft["supported_verified"] == 1
    assert camshaft["sample_value"] == 420.0


def test_agent_specific_unknown_metric_is_never_silently_dropped():
    rows = metric_catalog_for_vehicle(
        {"make": "Example", "engine_code": "X1"},
        [{
            "pid_name": "OEM_BATTERY_CURRENT",
            "label": "Corriente de batería",
            "category": "Sistema eléctrico",
            "status": "mapping_required",
            "supported_verified": 0,
            "source": "example_vehicle_catalog",
        }],
    )

    candidate = next(row for row in rows if row["pid_name"] == "OEM_BATTERY_CURRENT")
    assert candidate["status"] == "mapping_required"
    assert candidate["supported_verified"] == 0


def test_metric_catalog_api_exposes_pending_and_confirmed_candidates(monkeypatch, tmp_path):
    test_db = DatabaseManager(str(tmp_path / "catalog.db"))
    monkeypatch.setattr(backend_main, "db", test_db)
    vehicle = test_db.create_vehicle(
        "Passat de prueba",
        make="Volkswagen",
        model="Passat",
        engine_code="BKP",
        powertrain_type="diesel",
    )
    test_db.upsert_vehicle_capability(
        vehicle["id"],
        "VAG_CAMSHAFT_SPEED",
        "KWP_21",
        "051.2",
        supported_reported=True,
        supported_verified=True,
        unit="rpm",
        source="vag_kwp2000_capture",
        status="compatible",
        sample_value=420.0,
    )

    response = TestClient(backend_main.app).get(f"/api/vehicles/{vehicle['id']}/metric-catalog")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["catalogued"] >= len(ALL_KWP_SIGNALS)
    assert payload["summary"]["confirmed"] == 1
    assert payload["summary"]["pending"] > 0


def test_base_metric_catalog_api_works_with_an_empty_garage():
    response = TestClient(backend_main.app).get("/api/metric-catalog")

    assert response.status_code == 200
    payload = response.json()
    names = {row["pid_name"] for row in payload["metrics"]}
    categories = {row["category"] for row in payload["metrics"]}

    assert payload["vehicle_id"] is None
    assert payload["summary"]["catalogued"] == len(payload["metrics"])
    assert len(names) >= 90
    assert "OEM_DPF_DIFFERENTIAL_PRESSURE" in names
    assert {
        "Motor, marcha y mandos",
        "Temperaturas y refrigeración",
        "Admisión, aire, EGR y turbo",
        "Combustible, mezcla e inyección",
        "Escape, DPF/GPF y SCR",
        "Sistema eléctrico y comunicaciones",
    }.issubset(categories)
