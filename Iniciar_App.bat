@echo off
title Mi Coche por Dentro — Telemetria OBD-II & IA
cd /d "%~dp0"
echo Iniciando servidor backend y cargando interfaz de usuario...
.\.venv\Scripts\python.exe desktop_launcher.py
