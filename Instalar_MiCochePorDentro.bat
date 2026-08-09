@echo off
setlocal
cd /d "%~dp0"
title Instalar Mi Coche por Dentro

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_windows.ps1"
if errorlevel 1 (
    echo.
    echo La instalacion no ha terminado. Revisa el mensaje anterior.
    pause
    exit /b 1
)

echo.
echo Instalacion terminada.
pause
