# ADR 0003: Operación Estricta en Modo Solo Lectura en la Primera Versión

- **Estado:** Aprobado
- **Fecha:** 2026-07-23

## Contexto
El envío de comandos de escritura, borrado automático de DTCs, pruebas de actuadores o reprogramaciones CAN sin supervisión puede provocar situaciones peligrosas en el vehículo o borrado involuntario de evidencias de avería.

## Decisión
Bloquear todas las operaciones de escritura en el vehículo en la primera versión del sistema. La aplicación funcionará **únicamente en modo solo lectura** (lectura de PIDs Mode 01, DTCs Mode 03/07, Freeze Frames Mode 02 y Monitores Mode 06).

## Consecuencias
- Garantía absoluta de seguridad e integridad para el vehículo del usuario.
- Preservación permanente del historial de códigos de error antes de cualquier reparación.
