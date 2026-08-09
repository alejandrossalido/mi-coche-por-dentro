"""Validaciones de la configuración de escritorio y del backend."""

import os


def test_reproducible_desktop_build_files_exist():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    required = [
        "MiCochePorDentro.spec",
        os.path.join("scripts", "build_windows.ps1"),
        os.path.join("scripts", "smoke_test_windows.ps1"),
        os.path.join("docs", "DESKTOP_BUILD.md"),
        os.path.join("docs", "TROUBLESHOOTING.md"),
    ]
    for relative_path in required:
        assert os.path.isfile(os.path.join(project_root, relative_path))


def test_backend_api_integration_in_process():
    from backend.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    status_resp = client.get("/api/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "online"

    vehicle_resp = client.post(
        "/api/vehicles",
        json={
            "display_name": "Passat de prueba",
            "make": "Volkswagen",
            "model": "Passat B6",
            "year": 2008,
            "engine": "2.0 TDI",
            "engine_code": "CBAB",
            "fuel_type": "Diésel",
            "powertrain_type": "diesel",
            "market": "EU",
        },
    )
    assert vehicle_resp.status_code == 200

    spec_resp = client.get(f"/api/vehicles/{vehicle_resp.json()['id']}/spec")
    assert spec_resp.status_code == 200
    spec_data = spec_resp.json()
    assert spec_data["confidence_tier"] == "OEM_CONFIRMED"
    assert spec_data["metadata"]["engine_code"] == "CBAB"
