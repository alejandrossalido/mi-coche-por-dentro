# Seguridad

## Versiones mantenidas

Mientras no existan versiones estables publicadas en GitHub Releases, se mantiene únicamente la rama `main`.

## Comunicar una vulnerabilidad

No publiques claves, VIN, telemetría, matrículas ni detalles explotables en una incidencia pública.

Utiliza el formulario privado de GitHub:

<https://github.com/alejandrossalido/mi-coche-por-dentro/security/advisories/new>

Incluye la versión o commit, Windows utilizado, pasos mínimos para reproducir y el impacto esperado. No adjuntes capturas reales del vehículo sin anonimizarlas.

## Límites de seguridad del proyecto

- El servidor escucha exclusivamente en la interfaz local del ordenador.
- La API y el canal en directo rechazan orígenes web externos.
- La aplicación está diseñada para diagnóstico de solo lectura: no codifica, reprograma ni ejecuta actuadores.
- El análisis local es el predeterminado. Configurar una clave de IA no autoriza por sí solo a enviar datos; cada consulta remota exige una elección explícita del usuario.
- Nunca manipules la aplicación mientras conduces. Las pruebas en circulación requieren un acompañante.

La aplicación es una ayuda informativa y no sustituye a un diagnóstico profesional.

