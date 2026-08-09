from analysis.ai_service import AIService
from analysis.dtc_translations import describe_dtc_in_spanish


def test_interactive_assistant_uses_recent_user_context():
    service = AIService()

    response = service.query_interactive(
        user_question="¿Qué prueba debería hacer?",
        vehicle_info={"display_name": "Vehículo de prueba", "powertrain_type": "gasoline"},
        dtcs=[],
        stats={"signals": {}},
        rule_findings=[],
        conversation_history=[
            {"role": "user", "content": "El coche da tirones cuando acelero."},
            {"role": "assistant", "content": "Necesito más información."},
        ],
    )

    assert response["recommended_test"]["profile_id"] == "INTAKE_TURBO"


def test_dtc_descriptions_are_returned_in_spanish():
    assert describe_dtc_in_spanish("P0171", "System Too Lean (Bank 1)") == (
        "Mezcla demasiado pobre en el banco 1."
    )
    assert "castellano" in describe_dtc_in_spanish("P9999", "Unknown fault")


def test_interactive_assistant_uses_saved_session_symptom_and_reports_basis():
    service = AIService()
    response = service.query_interactive(
        user_question="¿Y qué debería revisar primero?",
        vehicle_info={
            "id": "vehicle-1",
            "display_name": "Vehículo de prueba",
            "powertrain_type": "gasoline",
        },
        dtcs=[],
        stats={
            "total_samples": 120,
            "signals": {
                "RPM": {"has_data": True, "min": 780, "max": 2600, "mean": 1250, "std": 20},
                "INTAKE_PRESSURE": {"has_data": True, "min": 45, "max": 160, "mean": 98, "std": 15},
            },
        },
        rule_findings=[],
        symptom_note="Síntoma declarado: pierde potencia al acelerar",
        session_context={
            "id": "session-1",
            "title": "Pérdida de potencia",
            "sample_count": 120,
            "data_sources": {"measured": 120},
            "dtc_scope": "No hay un escaneo DTC guardado para este vehículo.",
        },
    )

    assert response["recommended_test"]["profile_id"] == "INTAKE_TURBO"
    assert response["data_basis"]["session_id"] == "session-1"
    assert response["data_basis"]["sample_count"] == 120
    assert response["data_basis"]["valid_signal_count"] == 2
    assert response["data_basis"]["data_sources"] == {"measured": 120}
    assert "Síntoma guardado" in response["context_used"][-1]


def test_interactive_assistant_filters_incoherent_diesel_signals_and_does_not_invent_values():
    service = AIService()
    response = service.query_interactive(
        user_question="¿Cuál fue el LTFT?",
        vehicle_info={
            "id": "diesel-1",
            "display_name": "Diésel de prueba",
            "powertrain_type": "diesel",
        },
        dtcs=[],
        stats={
            "total_samples": 40,
            "signals": {
                "LONG_FUEL_TRIM_1": {
                    "has_data": True,
                    "min": -2,
                    "max": 4,
                    "mean": 1,
                    "std": 1,
                },
                "RPM": {"has_data": True, "min": 800, "max": 2200, "mean": 1200, "std": 30},
            },
        },
        rule_findings=[],
        session_context={"id": "session-diesel", "sample_count": 40, "data_sources": {"measured": 40}},
    )

    assert response["data_basis"]["valid_signal_count"] == 1
    assert all(item["pid"] != "LONG_FUEL_TRIM_1" for item in response["evidence"])
    assert "no voy a estimar ni inventar" in response["answer"]


def test_interactive_assistant_answers_exact_obd_value_question():
    service = AIService()
    response = service.query_interactive(
        user_question="¿Qué voltaje registró la batería?",
        vehicle_info={"id": "v1", "display_name": "Coche", "powertrain_type": "gasoline"},
        dtcs=[],
        stats={
            "total_samples": 25,
            "signals": {
                "CONTROL_MODULE_VOLTAGE": {
                    "has_data": True,
                    "min": 13.8,
                    "max": 14.4,
                    "mean": 14.1,
                    "std": 0.1,
                    "unit": "V",
                }
            },
        },
        rule_findings=[],
        session_context={"id": "s1", "sample_count": 25, "data_sources": {"measured": 25}},
    )

    assert "media 14.1" in response["answer"]
    assert "mínimo 13.8" in response["answer"]
    assert response["evidence"][0]["unit"] == "V"
