# ADR 0004: Abstracción de Proveedores de Inteligencia Artificial

- **Estado:** Aprobado
- **Fecha:** 2026-07-23

## Contexto
El análisis explicativo asistido por IA puede utilizar distintos proveedores (OpenAI GPT-4, Anthropic Claude, modelos locales Ollama/Llama.cpp) o funcionar totalmente offline sin conexión a Internet.

## Decisión
Implementar el módulo `AIService` (`analysis/ai_service.py`) con una capa de contrato Pydantic (`AiAnalysisResponse`) y fallback determinista local.

## Consecuencias
- La aplicación es 100% funcional sin conexión a Internet.
- La IA nunca puede inventar sensores no disponibles ni alterar conclusiones deterministas del motor de reglas.
