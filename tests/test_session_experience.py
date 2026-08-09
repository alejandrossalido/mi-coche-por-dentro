from fastapi.testclient import TestClient

import backend.main as backend_main
from database.db import DatabaseManager
from database.parquet_store import TelemetryStore


def test_session_metadata_can_be_named_and_recovered(tmp_path):
    db = DatabaseManager(str(tmp_path / "sessions.db"))
    vehicle = db.create_vehicle("Coche de prueba", make="Hyundai", model="Kona", year=2022)
    session = db.create_session(
        vehicle["id"],
        profile_id="COLD_START",
        title="Arranque de la mañana",
        symptom="Le cuesta arrancar",
        odometer_km=145_000,
        engine_condition="cold",
    )

    updated = db.update_session(session["id"], title="Arranque en frío", odometer_km=145_010)
    assert updated["title"] == "Arranque en frío"
    assert updated["odometer_km"] == 145_010
    assert db.recover_interrupted_sessions() == 1
    recovered = db.get_session(session["id"])
    assert recovered["status"] == "interrupted"
    assert "cierre inesperado" in recovered["notes"]


def test_session_library_reports_only_saved_telemetry(monkeypatch, tmp_path):
    db = DatabaseManager(str(tmp_path / "library.db"))
    store = TelemetryStore(str(tmp_path / "telemetry"))
    vehicle = db.create_vehicle("Kona", make="Hyundai", model="Kona", year=2022)
    session = db.create_session(
        vehicle["id"],
        profile_id="IDLE_STABILITY",
        title="Ralentí de control",
        symptom="Vibra en parado",
    )
    store.save_samples(
        session["id"],
        [
            {
                "session_id": session["id"],
                "timestamp_monotonic": index * 0.1,
                "timestamp_utc": "2026-07-31T10:00:00Z",
                "pid": "RPM",
                "value": 800 + index,
                "unit": "rpm",
                "ecu": "ENGINE",
                "quality": 1.0,
                "latency_ms": 5.0,
                "raw_response": "",
                "data_source": "measured",
            }
            for index in range(10)
        ],
    )
    db.stop_session(session["id"], quality_score=90, data_file=store.get_session_file_path(session["id"]))
    monkeypatch.setattr(backend_main, "db", db)
    monkeypatch.setattr(backend_main, "telemetry_store", store)
    client = TestClient(backend_main.app)

    response = client.get(f"/api/sessions/library?vehicle_id={vehicle['id']}")
    assert response.status_code == 200
    item = response.json()[0]
    assert item["title"] == "Ralentí de control"
    assert item["sample_count"] == 10
    assert item["signal_count"] == 1
    assert item["data_sources"] == ["measured"]
    assert item["result_label"] == "Datos fiables"

    edit_response = client.patch(
        f"/api/sessions/{session['id']}",
        json={"title": "Ralentí después de limpiar admisión", "odometer_km": 145020},
    )
    assert edit_response.status_code == 200
    assert edit_response.json()["title"] == "Ralentí después de limpiar admisión"

    db.record_dtc_scan(
        vehicle["id"],
        "manual",
        mil_status=True,
        dtcs=[{"code": "P0300", "status": "confirmed", "description": "Fallos de combustión."}],
    )
    context_response = client.get(f"/api/sessions/{session['id']}/assistant-context")
    assert context_response.status_code == 200
    context = context_response.json()
    assert context["session"]["symptom"] == "Vibra en parado"
    assert "independiente" in context["scope"]["dtc_scope"]
    assert "Síntoma guardado" in context["scope"]["symptom_scope"]

    query_response = client.post(
        f"/api/sessions/{session['id']}/query",
        json={"question": "¿En qué datos te basas?", "mode": "technical"},
    )
    assert query_response.status_code == 200
    basis = query_response.json()["data_basis"]
    assert basis["session_id"] == session["id"]
    assert basis["sample_count"] == 10
    assert "independiente" in basis["dtc_scope"]
