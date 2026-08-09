"""Rutas de recursos empaquetados y datos persistentes de la aplicación."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict

APP_NAME = "MiCochePorDentro"
APP_DISPLAY_NAME = "Mi Coche por Dentro"
APP_VERSION = "1.10.0"


def load_environment() -> list[Path]:
    """Carga configuración local sin sobrescribir variables del proceso."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return []

    loaded: list[Path] = []
    candidates = [resource_root() / ".env"]
    # El segundo archivo permite configurar un ejecutable empaquetado sin
    # modificar su directorio de instalación.
    candidates.append(user_root() / "config" / ".env")
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file():
            load_dotenv(resolved, override=False)
            loaded.append(resolved)
    return loaded


def resource_root() -> Path:
    """Devuelve la raíz inmutable del código o de los recursos de PyInstaller."""
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root).resolve()
    return Path(__file__).resolve().parent


def resource_path(relative_path: str | os.PathLike[str]) -> Path:
    """Resuelve un recurso sin depender del directorio de trabajo actual."""
    return (resource_root() / Path(relative_path)).resolve()


def user_root() -> Path:
    """Devuelve la raíz persistente y modificable de la aplicación."""
    override = os.environ.get("MICOCHE_HOME")
    if override:
        return Path(override).expanduser().resolve()

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return (Path(local_app_data) / APP_NAME).resolve()

    return (Path.home() / "AppData" / "Local" / APP_NAME).resolve()


def ensure_user_directories() -> Dict[str, Path]:
    """Crea y devuelve todos los directorios persistentes necesarios."""
    root = user_root()
    directories = {
        "root": root,
        "data": root / "data",
        "telemetry": root / "data" / "telemetry",
        "logs": root / "logs",
        "backups": root / "backups",
        "config": root / "config",
        "runtime": root / "runtime",
    }
    for path in directories.values():
        path.mkdir(parents=True, exist_ok=True)
    return directories


def database_path() -> Path:
    return ensure_user_directories()["data"] / "vehicle_ai.db"


def telemetry_path() -> Path:
    return ensure_user_directories()["telemetry"]


def logs_path() -> Path:
    return ensure_user_directories()["logs"]


def backups_path() -> Path:
    return ensure_user_directories()["backups"]


def runtime_path() -> Path:
    return ensure_user_directories()["runtime"]
