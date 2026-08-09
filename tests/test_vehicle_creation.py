from fastapi.testclient import TestClient

import backend.main as backend_main
from database.db import DatabaseManager


def test_create_vehicle_api_preserves_identity_and_powertrain(monkeypatch, tmp_path):
    test_db = DatabaseManager(str(tmp_path / "vehicles.db"))
    monkeypatch.setattr(backend_main, "db", test_db)
    client = TestClient(backend_main.app)

    response = client.post(
        "/api/vehicles",
        json={
            "display_name": "Kona de pruebas",
            "make": "  Hyundai ",
            "model": " Kona ",
            "year": 2021,
            "generation": "OS",
            "variant": "Tecno",
            "engine": "1.6 GDi Hybrid 141 CV",
            "engine_code": "g4le",
            "powertrain_type": "hybrid",
            "market": "eu",
        },
    )

    assert response.status_code == 200
    vehicle = response.json()
    assert vehicle["display_name"] == "Kona de pruebas"
    assert vehicle["make"] == "Hyundai"
    assert vehicle["model"] == "Kona"
    assert vehicle["fuel_type"] == "Híbrido"
    assert vehicle["powertrain_type"] == "hybrid"
    assert vehicle["generation"] == "OS"
    assert vehicle["variant"] == "Tecno"
    assert vehicle["engine_code"] == "G4LE"
    assert vehicle["market"] == "EU"

    spec_response = client.get(f"/api/vehicles/{vehicle['id']}/spec")
    assert spec_response.status_code == 200
    assert spec_response.json()["confidence_tier"] == "GENERIC_ENGINEERING_RANGE"


def test_create_vehicle_generates_name_and_requires_basic_identity(monkeypatch, tmp_path):
    test_db = DatabaseManager(str(tmp_path / "vehicles.db"))
    monkeypatch.setattr(backend_main, "db", test_db)
    client = TestClient(backend_main.app)

    response = client.post(
        "/api/vehicles",
        json={
            "make": "Hyundai",
            "model": "Kona",
            "year": 2022,
            "powertrain_type": "bev",
        },
    )

    assert response.status_code == 200
    assert response.json()["display_name"] == "Hyundai Kona 2022"
    assert response.json()["fuel_type"] == "Eléctrico"

    invalid_response = client.post(
        "/api/vehicles",
        json={"make": "", "model": "Kona", "year": 2022},
    )
    assert invalid_response.status_code == 422


def test_mode06_does_not_return_demo_values(monkeypatch, tmp_path):
    test_db = DatabaseManager(str(tmp_path / "vehicles.db"))
    monkeypatch.setattr(backend_main, "db", test_db)
    client = TestClient(backend_main.app)

    response = client.get("/api/vehicles/v1/mode06")

    assert response.status_code == 200
    assert response.json()["available"] is False
    assert response.json()["monitors"] == []
    assert "demostración" in response.json()["message"]
