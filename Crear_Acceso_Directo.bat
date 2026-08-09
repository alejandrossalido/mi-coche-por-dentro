@echo off
setlocal
cd /d "%~dp0"
title Crear acceso directo de Mi Coche por Dentro

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\create_desktop_shortcut.ps1" -ProjectRoot "%~dp0"
if errorlevel 1 (
    echo.
    echo No se pudo crear el acceso directo. Revisa el mensaje anterior.
    pause
    exit /b 1
)

echo.
echo Ya puedes abrir Mi Coche por Dentro desde el escritorio.
pause
