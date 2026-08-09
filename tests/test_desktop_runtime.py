import json
import os
import socket
import sys
import threading
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app_paths
from desktop_launcher import BackendServer, is_port_available, select_port


def test_resource_path_uses_source_root(monkeypatch):
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    assert app_paths.resource_path("dashboard/out") == (
        Path(app_paths.__file__).resolve().parent / "dashboard" / "out"
    )


def test_resource_path_uses_pyinstaller_root(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert app_paths.resource_path("rules/diagnostic_rules.yaml") == (
        tmp_path / "rules" / "diagnostic_rules.yaml"
    ).resolve()


def test_user_directories_are_persistent_and_separate(monkeypatch, tmp_path):
    monkeypatch.setenv("MICOCHE_HOME", str(tmp_path / "profile"))
    directories = app_paths.ensure_user_directories()
    assert directories["data"].is_dir()
    assert directories["telemetry"].is_dir()
    assert directories["logs"].is_dir()
    assert app_paths.database_path().parent == directories["data"]
    assert app_paths.resource_root() != directories["root"]


def test_environment_files_are_loaded_without_overriding_process(monkeypatch, tmp_path):
    project_root = tmp_path / "project"
    profile_root = tmp_path / "profile"
    (profile_root / "config").mkdir(parents=True)
    project_root.mkdir()
    (project_root / ".env").write_text(
        "MICOCHE_TEST_PROJECT=project\nMICOCHE_TEST_PRIORITY=project\n",
        encoding="utf-8",
    )
    (profile_root / "config" / ".env").write_text(
        "MICOCHE_TEST_PROFILE=profile\nMICOCHE_TEST_PRIORITY=profile\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(app_paths, "resource_root", lambda: project_root)
    monkeypatch.setattr(app_paths, "user_root", lambda: profile_root)
    monkeypatch.setenv("MICOCHE_TEST_PRIORITY", "process")

    loaded = app_paths.load_environment()

    assert loaded == [project_root / ".env", profile_root / "config" / ".env"]
    assert os.environ["MICOCHE_TEST_PROJECT"] == "project"
    assert os.environ["MICOCHE_TEST_PROFILE"] == "profile"
    assert os.environ["MICOCHE_TEST_PRIORITY"] == "process"


def test_select_port_falls_back_when_preferred_is_occupied():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as occupied:
        occupied.bind(("127.0.0.1", 0))
        occupied.listen()
        occupied_port = occupied.getsockname()[1]
        selected = select_port(occupied_port)
        assert selected != occupied_port
        assert is_port_available(selected)


def test_wait_until_healthy_detects_backend_that_died():
    server = BackendServer(select_port(8000))
    server.thread = threading.Thread(target=lambda: None)
    server.thread.start()
    server.thread.join()
    with pytest.raises(RuntimeError, match="terminó durante el arranque"):
        server.wait_until_healthy(timeout_seconds=0.2)


def test_wait_until_healthy_times_out():
    stop = threading.Event()
    server = BackendServer(select_port(8000))
    server.thread = threading.Thread(target=stop.wait, daemon=True)
    server.thread.start()
    try:
        with pytest.raises(TimeoutError, match="no superó /health"):
            server.wait_until_healthy(timeout_seconds=0.25)
    finally:
        stop.set()
        server.thread.join(timeout=1)


def test_source_launcher_backend_dashboard_api_and_shutdown():
    server = BackendServer(select_port(8000))
    server.start()
    try:
        server.wait_until_healthy(timeout_seconds=20)
        with TestClient(_app()) as client:
            assert client.get("/health").status_code == 200
            assert client.get("/api/status").json()["status"] == "online"
            assert client.get("/api/vehicles").status_code == 200
            dashboard = client.get("/")
            assert dashboard.status_code == 200
            assert "<html" in dashboard.text.lower()
    finally:
        server.stop()
    assert server.thread is not None
    assert not server.thread.is_alive()


def test_health_reports_missing_dashboard():
    app = _app()
    original = app.state.dashboard_available
    app.state.dashboard_available = False
    try:
        response = TestClient(app).get("/health")
        assert response.status_code == 503
        assert "Dashboard" in response.json()["detail"]
    finally:
        app.state.dashboard_available = original


def test_runtime_status_is_valid_json(tmp_path, monkeypatch):
    monkeypatch.setenv("MICOCHE_HOME", str(tmp_path))
    import desktop_launcher

    desktop_launcher._write_runtime_status(43210)
    payload = json.loads(desktop_launcher._runtime_file().read_text(encoding="utf-8"))
    assert payload["pid"] > 0
    assert payload["port"] == 43210
    assert payload["url"] == "http://127.0.0.1:43210"
    desktop_launcher._remove_runtime_status()
    assert not desktop_launcher._runtime_file().exists()


def _app():
    from backend.main import app

    return app
