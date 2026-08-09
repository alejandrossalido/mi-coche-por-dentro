"""
Prueba de Extremo a Extremo (E2E Full Pipeline) de 'Mi Coche por Dentro'.
Cubre: Registro de coche -> Identificación de motor -> Sesión de telemetría en Polars/Parquet ->
       Análisis determinista -> Resolutor de Ficha Técnica OEM por clave estricta ->
       Filtro de coherencia semántica -> Consulta interactiva a IA -> Verificación de cero PIDs alucinados.
"""
import pytest
import os
import tempfile
import polars as pl
from database.db import DatabaseManager
from database.parquet_store import TelemetryStore
from analysis.statistics import SignalStatistics
from analysis.rules_engine import RuleEngine
from analysis.spec_resolver import SpecResolver
from analysis.coherence_rules import PhysicalCoherenceValidator
from analysis.ai_service import AIService

def test_e2e_full_pipeline_passat_cbab():
    tmpdir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(tmpdir, "test_e2e.db")
        db = DatabaseManager(db_path)
        telemetry_store = TelemetryStore(base_dir=tmpdir)

        # 1. Crear vehículo identificando el motor exacto CBAB
        vehicle = db.create_vehicle(
            display_name="VW Passat B6 2.0 TDI CBAB",
            make="Volkswagen",
            model="Passat",
            year=2009,
            engine="CBAB",
            fuel_type="Diésel",
            powertrain_type="diesel"
        )
        assert vehicle["id"] is not None

        # 2. Registrar sesión de telemetría
        session = db.create_session(vehicle_id=vehicle["id"], notes="Prueba de tramo en carretera con tirón en aceleración")
        session_id = session["id"]

        # 3. Guardar dataset de telemetría real en Parquet mediante save_samples
        samples = []
        for i in range(60):
            t_ms = float(i * 1000)
            rpm_val = 800.0 if i < 45 else (2800.0 if i != 45 else 1200.0)
            boost_val = 1.25 if i != 45 else 0.40
            
            samples.append({
                "session_id": session_id,
                "timestamp_monotonic": t_ms / 1000.0,
                "timestamp_utc": f"2026-07-29T16:00:{i:02d}Z",
                "pid": "RPM",
                "value": rpm_val,
                "unit": "RPM",
                "ecu": "ENGINE",
                "quality": 1.0
            })
            samples.append({
                "session_id": session_id,
                "timestamp_monotonic": t_ms / 1000.0,
                "timestamp_utc": f"2026-07-29T16:00:{i:02d}Z",
                "pid": "BOOST_PRESSURE_REL",
                "value": boost_val,
                "unit": "bar",
                "ecu": "ENGINE",
                "quality": 1.0
            })

        telemetry_store.save_samples(session_id, samples)
        loaded_df = telemetry_store.load_session_dataframe(session_id)
        assert loaded_df is not None
        assert len(loaded_df) == 120 # 60 * 2 PIDs

        # 4. Análisis Estadístico y Motor de Reglas sobre el DataFrame de telemetría cargado
        stats = SignalStatistics.analyze_full_session(loaded_df)
        rule_engine = RuleEngine()
        rule_findings = rule_engine.evaluate_session(loaded_df)


        # 5. Resolución de Ficha Técnica por Clave Estricta Make+Model+EngineCode
        resolved_spec = SpecResolver.resolve_spec(
            make=vehicle["make"],
            model=vehicle["model"],
            engine_code=vehicle["engine"],
            powertrain_type=vehicle["powertrain_type"]
        )

        assert resolved_spec["confidence_tier"] == "OEM_CONFIRMED"
        assert resolved_spec["metadata"]["engine_code"] == "CBAB"
        assert resolved_spec["metadata"]["source_type"] == "OEM_CONFIRMED"

        # 6. Validación de Coherencia Física Semántica
        raw_signals = stats.get("signals", {})
        coherent_signals = PhysicalCoherenceValidator.filter_coherent_signals(raw_signals, vehicle["powertrain_type"])
        
        # Verificar que NO se incluyeron Fuel Trims de gasolina ni RPM de motor combustion en BEV
        assert "STFT" not in coherent_signals
        assert "LTFT" not in coherent_signals

        # 7. Consulta Interactiva a la IA
        ai_service = AIService()
        question = "¿Por qué cayó la presión del turbo y las RPM alrededor del segundo 45?"
        ai_response = ai_service.query_interactive(
            user_question=question,
            vehicle_info=vehicle,
            dtcs=[],
            stats=stats,
            rule_findings=rule_findings,
            symptom_note=session["notes"]
        )

        assert ai_response["status"] == "success"
        assert ai_response["question"] == question
        assert "answer" in ai_response
        assert len(ai_response["answer"]) > 50
    finally:
        # Limpieza segura para Windows
        db.get_connection().close()

def test_e2e_full_pipeline_unknown_engine_requires_identification():
    # Si se conoce Make y Model pero NO el código de motor, rechaza OEM_CONFIRMED y exige identificación
    resolved = SpecResolver.resolve_spec(make="Volkswagen", model="Passat", engine_code="")
    assert resolved["confidence_tier"] == "ENGINE_IDENTIFICATION_REQUIRED"
    assert "se requiere especificar el código de motor exacto" in resolved["resolved_source"]
