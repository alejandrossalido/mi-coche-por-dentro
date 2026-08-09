"""Launcher de escritorio fiable para Mi Coche por Dentro."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import logging
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app_paths import (
    APP_DISPLAY_NAME,
    APP_VERSION,
    ensure_user_directories,
    load_environment,
    resource_root,
    resource_path,
    runtime_path,
    user_root,
)

HOST = "127.0.0.1"
DEFAULT_PORT = 8000
STARTUP_TIMEOUT_SECONDS = 30.0
logger = logging.getLogger("desktop_launcher")


def _prepare_directories() -> dict[str, Path]:
    try:
        return ensure_user_directories()
    except OSError:
        fallback = Path(tempfile.gettempdir()) / "MiCochePorDentro"
        os.environ["MICOCHE_HOME"] = str(fallback)
        return ensure_user_directories()


def configure_logging() -> Path:
    directories = _prepare_directories()
    log_file = directories["logs"] / "app.log"
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if sys.stderr is not None:
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)
    return log_file


def is_port_available(port: int, host: str = HOST) -> bool:
    if not 1 <= int(port) <= 65535:
        return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        candidate.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            candidate.bind((host, int(port)))
        except OSError:
            return False
    return True


def select_port(preferred_port: int = DEFAULT_PORT, host: str = HOST) -> int:
    if is_port_available(preferred_port, host):
        return preferred_port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        candidate.bind((host, 0))
        return int(candidate.getsockname()[1])


class BackendServer:
    def __init__(self, port: int):
        self.port = port
        self.server = None
        self.thread: Optional[threading.Thread] = None
        self.error: Optional[BaseException] = None

    @property
    def url(self) -> str:
        return f"http://{HOST}:{self.port}"

    def start(self) -> None:
        self.thread = threading.Thread(
            target=self._run,
            name="fastapi-backend",
            daemon=True,
        )
        self.thread.start()

    def _run(self) -> None:
        try:
            import uvicorn
            from backend.main import app

            config = uvicorn.Config(
                app=app,
                host=HOST,
                port=self.port,
                log_config=None,
                log_level="info",
                access_log=False,
                use_colors=False,
            )
            self.server = uvicorn.Server(config)
            logger.info("Inicio de FastAPI en %s", self.url)
            self.server.run()
        except BaseException as exc:
            self.error = exc
            logger.exception("El backend FastAPI terminó con una excepción.")

    def wait_until_healthy(self, timeout_seconds: float = STARTUP_TIMEOUT_SECONDS) -> None:
        deadline = time.monotonic() + timeout_seconds
        health_url = f"{self.url}/health"
        last_error = "sin respuesta"
        while time.monotonic() < deadline:
            if self.error is not None:
                raise RuntimeError(f"El backend terminó durante el arranque: {self.error!r}")
            if self.thread is not None and not self.thread.is_alive():
                raise RuntimeError("El backend terminó durante el arranque sin quedar disponible.")
            try:
                with urllib.request.urlopen(health_url, timeout=1.0) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                    if response.status == 200 and payload.get("status") == "healthy":
                        logger.info("Health check correcto: %s", health_url)
                        return
                    last_error = f"respuesta no válida: HTTP {response.status}"
            except urllib.error.HTTPError as exc:
                last_error = f"HTTP {exc.code}: {exc.reason}"
            except (OSError, ValueError, urllib.error.URLError) as exc:
                last_error = str(exc)
            time.sleep(0.2)
        raise TimeoutError(
            f"FastAPI no superó /health en {timeout_seconds:.1f} s ({last_error})."
        )

    def stop(self, timeout_seconds: float = 10.0) -> None:
        if self.server is not None:
            self.server.should_exit = True
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=timeout_seconds)
        if self.thread is not None and self.thread.is_alive():
            logger.error("El hilo de FastAPI no terminó dentro del timeout de cierre.")
        else:
            logger.info("FastAPI cerrado limpiamente.")


class SingleInstance:
    ERROR_ALREADY_EXISTS = 183

    def __init__(self) -> None:
        self.handle = None

    def acquire(self) -> bool:
        if os.name != "nt":
            return True
        # El perfil de datos forma parte de la identidad de la instancia. Esto
        # permite ejecutar una prueba aislada sin interferir con la aplicación
        # real, manteniendo el bloqueo de dos ventanas sobre el mismo perfil.
        profile_key = hashlib.sha256(
            str(user_root()).casefold().encode("utf-8")
        ).hexdigest()[:16]
        self.handle = ctypes.windll.kernel32.CreateMutexW(
            None, False, f"Local\\MiCochePorDentro.Desktop.{profile_key}"
        )
        return ctypes.windll.kernel32.GetLastError() != self.ERROR_ALREADY_EXISTS

    def close(self) -> None:
        if self.handle and os.name == "nt":
            ctypes.windll.kernel32.CloseHandle(self.handle)
            self.handle = None


def _show_error_dialog(message: str, log_file: Path) -> None:
    logger.error("%s", message)
    try:
        import tkinter as tk

        root = tk.Tk()
        root.title(f"{APP_DISPLAY_NAME} — Error de arranque")
        root.geometry("680x330")
        root.resizable(True, True)
        tk.Label(
            root,
            text="No se pudo iniciar la aplicación.",
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        ).pack(fill="x", padx=18, pady=(18, 8))
        text = tk.Text(root, wrap="word", height=9, font=("Segoe UI", 10))
        text.insert(
            "1.0",
            f"{message}\n\nRegistro de diagnóstico:\n{log_file}",
        )
        text.configure(state="disabled")
        text.pack(fill="both", expand=True, padx=18, pady=8)
        buttons = tk.Frame(root)
        buttons.pack(fill="x", padx=18, pady=(4, 16))

        def open_logs() -> None:
            os.startfile(str(log_file.parent))

        def copy_error() -> None:
            root.clipboard_clear()
            root.clipboard_append(f"{message}\nLog: {log_file}")
            root.update()

        tk.Button(buttons, text="Abrir carpeta de logs", command=open_logs).pack(
            side="left", padx=(0, 8)
        )
        tk.Button(buttons, text="Copiar error", command=copy_error).pack(
            side="left", padx=(0, 8)
        )
        tk.Button(buttons, text="Cerrar", command=root.destroy).pack(side="right")
        root.mainloop()
    except Exception:
        logger.exception("No se pudo mostrar el diálogo gráfico de error.")
        if os.name == "nt":
            ctypes.windll.user32.MessageBoxW(
                0,
                f"{message}\n\nLog: {log_file}",
                f"{APP_DISPLAY_NAME} — Error",
                0x10,
            )


def _show_already_running() -> None:
    message = "Mi Coche por Dentro ya está abierto."
    if os.name == "nt":
        ctypes.windll.user32.MessageBoxW(0, message, APP_DISPLAY_NAME, 0x40)
    else:
        logger.warning(message)


def _browser_fallback(url: str) -> None:
    logger.warning("PyWebView no está disponible; se usa el navegador como fallback.")
    browser_candidates = [
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
    ]
    for browser_path in browser_candidates:
        if browser_path.is_file():
            process = subprocess.Popen([str(browser_path), f"--app={url}"])
            process.wait()
            return

    webbrowser.open(url)
    try:
        import tkinter.messagebox as messagebox

        messagebox.showinfo(
            APP_DISPLAY_NAME,
            "La aplicación está abierta en el navegador. "
            "Pulsa Aceptar cuando quieras cerrar el servidor local.",
        )
    except Exception:
        while True:
            time.sleep(1)


def open_desktop_window(url: str) -> None:
    try:
        import webview

        webview.create_window(
            title=f"{APP_DISPLAY_NAME} — Telemetría OBD-II e IA",
            url=url,
            width=1280,
            height=800,
            min_size=(960, 640),
            resizable=True,
        )
        webview.start(debug=False)
    except Exception:
        logger.exception("No se pudo iniciar PyWebView.")
        _browser_fallback(url)


def _runtime_file() -> Path:
    return runtime_path() / "desktop.json"


def _write_runtime_status(port: int) -> None:
    payload = {
        "pid": os.getpid(),
        "port": port,
        "url": f"http://{HOST}:{port}",
        "started_at": time.time(),
    }
    _runtime_file().write_text(json.dumps(payload), encoding="utf-8")


def _remove_runtime_status() -> None:
    status_file = _runtime_file()
    try:
        if status_file.is_file():
            payload = json.loads(status_file.read_text(encoding="utf-8"))
            if payload.get("pid") == os.getpid():
                status_file.unlink()
    except (OSError, ValueError):
        logger.warning("No se pudo limpiar el archivo de estado %s", status_file)


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=not getattr(sys, "frozen", False))
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--run-seconds", type=float, default=0.0)
    return parser.parse_args(argv)


def run_application(args: argparse.Namespace, log_file: Path) -> int:
    configured_port = int(os.environ.get("MICOCHE_PORT", DEFAULT_PORT))
    port = select_port(configured_port)
    if port != configured_port:
        logger.warning("El puerto %s estaba ocupado; se usará %s.", configured_port, port)
    logger.info("Puerto seleccionado: %s", port)

    backend = BackendServer(port)
    try:
        backend.start()
        backend.wait_until_healthy()
        _write_runtime_status(port)
        if args.headless:
            lifetime = max(0.0, float(args.run_seconds))
            deadline = time.monotonic() + lifetime if lifetime else None
            while deadline is None or time.monotonic() < deadline:
                if backend.error is not None:
                    raise RuntimeError(f"El backend terminó: {backend.error!r}")
                time.sleep(0.1)
        else:
            open_desktop_window(backend.url)
        return 0
    except Exception as exc:
        logger.exception("Fallo de arranque o ejecución.")
        if not args.headless:
            _show_error_dialog(str(exc), log_file)
        return 1
    finally:
        _remove_runtime_status()
        backend.stop()


def main(argv: Optional[list[str]] = None) -> int:
    load_environment()
    log_file = configure_logging()
    args = _parse_args(argv)
    logger.info("Inicio de %s versión %s", APP_DISPLAY_NAME, APP_VERSION)
    logger.info("Ejecutable: %s", Path(sys.executable).resolve())
    logger.info("Directorio de trabajo: %s", Path.cwd())
    logger.info("Raíz de recursos: %s", resource_root())
    logger.info("Directorio de datos: %s", user_root())
    dashboard = resource_path("dashboard/out/index.html")
    logger.info("Dashboard: %s (%s)", dashboard, "disponible" if dashboard.is_file() else "ausente")

    instance = SingleInstance()
    if not instance.acquire():
        logger.warning("Se rechazó una segunda instancia.")
        if not args.headless:
            _show_already_running()
        return 2

    try:
        return run_application(args, log_file)
    finally:
        instance.close()
        logger.info("Cierre de %s", APP_DISPLAY_NAME)
        logging.shutdown()


if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()
    raise SystemExit(main())
