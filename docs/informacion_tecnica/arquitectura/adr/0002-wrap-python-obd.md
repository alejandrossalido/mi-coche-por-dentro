# ADR 0002: Abstracción Propia sobre la Librería python-OBD

- **Estado:** Aprobado
- **Fecha:** 2026-07-23

## Contexto
La librería `python-OBD` proporciona la capa base de comunicación serie/Bluetooth ELM327/OBDLink. Sin embargo, depender directamente de sus clases en todo el proyecto dificultaría la adaptación a adaptadores propietarios o transportes J2534 en el futuro.

## Decisión
Envolver `python-OBD` dentro del módulo de abstracción `AdapterManager` (`collector/adapter_manager.py`).

## Consecuencias
- Desacoplamiento total entre el backend/dashboard y la librería de comunicación de bajo nivel.
- Capacidad de conmutar transparente entre hardware real y el simulador de pruebas sin modificar la API REST.
