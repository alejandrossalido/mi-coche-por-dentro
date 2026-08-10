import httpx
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import backend.main as backend_main
from analysis.ai_service import AIService


client = TestClient(backend_main.app)


def test_security_headers_and_api_cache_policy_are_present():
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["cache-control"] == "no-store"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_cors_accepts_local_dashboard_and_rejects_external_sites():
    local = client.get("/api/status", headers={"Origin": "http://127.0.0.1:3000"})
    external = client.get("/api/status", headers={"Origin": "https://example.com"})

    assert local.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
    assert "access-control-allow-origin" not in external.headers


def test_websocket_rejects_external_browser_origin():
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(
            "/api/live",
            headers={"Origin": "https://example.com"},
        ):
            pass

    assert exc_info.value.code == 1008


def test_simulator_is_disabled_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")

    response = client.post(
        "/api/simulator/trigger-fault",
        json={"fault_type": "IGNITION_OFF"},
    )

    assert response.status_code == 404


def test_anthropic_key_does_not_transmit_without_explicit_consent(monkeypatch):
    def unexpected_remote_call(*args, **kwargs):
        raise AssertionError("No remote request is allowed without explicit consent")

    monkeypatch.setattr(httpx, "post", unexpected_remote_call)
    service = AIService(api_key="sk-ant-test-key")

    response = service.analyze_session(
        vehicle_info={"id": "test", "make": "Example", "model": "Car"},
        dtcs=[],
        stats={"signals": {}},
        rule_findings=[],
    )

    assert response.confidence_level >= 0
