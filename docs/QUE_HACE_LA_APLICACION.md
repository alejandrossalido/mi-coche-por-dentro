# Qué hace Mi Coche por Dentro

**Mi Coche por Dentro** convierte un ordenador Windows y un adaptador OBD-II en una herramienta local para observar, registrar y comprender el funcionamiento del vehículo.

Está pensada tanto para una persona que quiere una explicación clara como para quien desea consultar todos los datos técnicos disponibles.

## Qué aporta

### Datos en directo

Muestra las señales que la ECU realmente responde, organizadas por sistemas:

- motor, RPM, velocidad y carga;
- temperaturas del motor y del aire;
- admisión, caudal, presión, turbo y EGR;
- combustible, inyección y consumo;
- sistema eléctrico y tensión;
- escape, emisiones y DPF/GPF cuando estén disponibles.

La pantalla no debería confundir una señal ausente con un valor real. Los datos no soportados pueden ocultarse y `--` indica que no existe una lectura válida.

### Diagnósticos guiados

La aplicación propone recorridos de captura para revisar:

- estado general;
- batería y alternador;
- termostato y refrigeración;
- estabilidad del ralentí;
- turbo y admisión;
- consumo e inyección;
- emisiones y preparación para ITV.

Antes de empezar comprueba que la conexión y las señales necesarias sean válidas. Durante la prueba se pueden marcar incidencias como tirones, vibraciones, humo, ruido o pérdida de potencia.

### Sesiones e historial

Cada prueba puede guardarse como una sesión independiente. Esto permite:

- volver a consultar un trayecto;
- revisar gráficas sincronizadas;
- comparar el comportamiento en distintas condiciones;
- construir una referencia habitual para cada coche;
- comprobar el antes y el después de una reparación.

### Informes comprensibles

Al finalizar, genera un informe que resume:

- calidad y cobertura de la captura;
- hechos observados en los datos;
- valores o comportamientos que requieren atención;
- limitaciones de la prueba;
- comprobaciones siguientes recomendadas.

El informe diferencia hechos, cálculos e hipótesis. No debería afirmar que una pieza está averiada cuando los datos no permiten demostrarlo.

### Códigos y monitores

Cuando el vehículo los soporta, puede consultar:

- códigos DTC guardados o pendientes;
- Freeze Frame;
- readiness de emisiones;
- resultados internos del Modo 06.

El estado de los monitores ayuda a entender lo que informa la ECU, pero no garantiza por sí solo superar una ITV.

### Garaje para varios coches

Cada usuario crea sus propios vehículos. Cada coche mantiene separados:

- ficha técnica;
- capacidades detectadas;
- sesiones y telemetría;
- códigos de avería;
- reparaciones y comparaciones;
- referencias históricas.

La versión pública no incluye los coches del desarrollador ni datos personales precargados.

### Dos niveles de compatibilidad

**OBD-II genérico:** funciona con los parámetros estándar que anuncie y responda cada vehículo.

**Perfil avanzado:** añade datos propietarios documentados para una combinación concreta de modelo, motor y ECU. Estos perfiles pueden ofrecer información mucho más útil, pero deben investigarse y validarse individualmente.

Por eso dos coches con el mismo nombre comercial pueden mostrar distinta cantidad de datos.

### Modo guiado y profesional

- **Modo guiado:** reduce la complejidad, explica los pasos y destaca la información esencial.
- **Modo profesional:** muestra controles, estados y datos técnicos adicionales.

El idioma puede cambiarse entre español, inglés, italiano y alemán.

## Consumo de combustible

Si la ECU entrega caudal de combustible, la aplicación puede utilizarlo directamente. En otros coches el consumo se calcula a partir de señales verificadas.

El consumo medio del trayecto debe obtenerse integrando combustible y distancia, no haciendo una media simple de los valores instantáneos. Cuando sea calculado, el informe debe indicarlo.

## Funcionamiento local y privacidad

La adquisición, el almacenamiento y el análisis básico funcionan localmente. Los datos se guardan en:

```text
%LOCALAPPDATA%\MiCochePorDentro
```

No es obligatorio utilizar un servicio de IA ni introducir una clave externa. Tampoco se necesita matrícula o VIN completo para utilizar la aplicación.

## Adaptadores y vehículos

La aplicación trabaja con adaptadores serie OBD-II compatibles. Una conexión USB de calidad suele ser la opción más estable. Los clones ELM327 económicos pueden perder respuestas o no soportar protocolos ampliados.

La cobertura depende de cuatro factores:

1. lo que ofrece la ECU;
2. el protocolo utilizado;
3. las capacidades del adaptador;
4. la existencia de documentación fiable para señales propietarias.

## Lo que no hace

- No codifica ni reprograma centralitas.
- No ejecuta adaptaciones o actuadores.
- No borra automáticamente códigos DTC.
- No controla el vehículo.
- No sustituye las comprobaciones mecánicas ni a un profesional.
- No inventa sensores que el coche no ofrece.

## Seguridad

El conductor nunca debe manipular la aplicación mientras circula. Las pruebas en marcha requieren un acompañante que opere el ordenador o deben registrarse sin interacción.

El proyecto está diseñado alrededor del principio de **solo lectura**. Una futura función que escribiese en una ECU necesitaría un diseño y una revisión de seguridad independientes.

## Estado de la plataforma

La distribución de escritorio actual está orientada a Windows 10/11 de 64 bits. Linux y macOS no cuentan todavía con paquete ni compatibilidad OBD oficialmente probados.

El proyecto puede seguir recibiendo nuevos perfiles de vehículos, mejoras de análisis, traducciones y actualizaciones de compatibilidad sin perder los coches y sesiones guardados por el usuario.
