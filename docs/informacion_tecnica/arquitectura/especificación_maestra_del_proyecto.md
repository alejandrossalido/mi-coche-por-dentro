# Especificación maestra del proyecto — Mi Coche por Dentro

> **Nombre provisional:** Mi Coche por Dentro
> **Tipo de proyecto:** aplicación local multimarca de monitorización OBD-II y análisis asistido por inteligencia artificial
> **Documento complementario:** `ROADMAP.md`
> **Estado:** especificación funcional y técnica inicial
> **Plataforma principal:** Dell Precision con Windows + OBDLink LX Bluetooth

---

## 1. Propósito de este documento

Este documento define con precisión **qué se quiere construir, por qué se quiere construir, cómo debe comportarse el sistema y qué límites no debe superar**.

Su función es servir como contexto permanente para cualquier persona o inteligencia artificial que participe en el desarrollo. Debe evitar que el proyecto derive hacia una simple aplicación de lectura OBD, que la IA invente diagnósticos o que se implementen operaciones peligrosas sobre el vehículo.

Este archivo describe el **qué**, el **por qué** y las reglas de diseño. El archivo `ROADMAP.md` debe describir el orden de implementación, los hitos y las tareas concretas.

Antes de proponer código o modificar la arquitectura, cualquier agente de desarrollo debe leer ambos documentos.

---

## 2. Resumen ejecutivo

El proyecto consiste en convertir un ordenador portátil Windows y un adaptador OBDLink LX Bluetooth en un **laboratorio portátil de monitorización y análisis de vehículos**.

El sistema deberá ser capaz de:

* Conectarse a distintos vehículos compatibles con OBD-II/EOBD.
* Detectar automáticamente el protocolo y los parámetros disponibles.
* Leer y conservar códigos de avería genéricos.
* Recuperar freeze frames cuando existan.
* Monitorizar datos del motor y emisiones en tiempo real.
* Registrar sesiones de conducción o pruebas en parado.
* Permitir al usuario marcar el instante en el que ocurre un síntoma.
* Sincronizar y representar gráficamente las señales.
* Detectar anomalías mediante cálculos deterministas.
* Comparar sesiones realizadas en diferentes fechas o condiciones.
* Mantener un expediente técnico separado para cada vehículo.
* Utilizar una IA para explicar los datos, ordenar hipótesis y recomendar comprobaciones.
* Generar informes claros para el usuario o para un taller.
* Exponer funciones de consulta mediante MCP en una fase avanzada.

La IA no debe ser el componente que captura los datos ni el que decide por sí solo qué pieza está averiada. La captura y el análisis básico deben funcionar de forma local, reproducible y verificable.

---

## 3. Problema que se quiere resolver

Los lectores OBD convencionales suelen presentar alguno de estos problemas:

* Solo muestran un código de error sin contexto suficiente.
* Enseñan valores en vivo sin ayudar a interpretarlos.
* No conservan un historial técnico estructurado.
* No permiten comparar fácilmente antes y después de una reparación.
* No relacionan el momento de un síntoma con varias señales simultáneas.
* No explican qué datos faltan para confirmar una hipótesis.
* Pueden inducir al usuario a sustituir piezas basándose únicamente en un DTC.

Por otro lado, una inteligencia artificial general puede explicar códigos y conceptos, pero si no recibe datos estructurados y fiables corre el riesgo de:

* Inventar sensores no disponibles.
* Aplicar criterios de un tipo de motor a otro.
* Confundir causa y consecuencia.
* Presentar una hipótesis como un diagnóstico confirmado.
* Recomendar sustituir componentes sin realizar comprobaciones.

El proyecto debe unir ambas partes de forma controlada:

1. El adaptador obtiene datos reales.
2. El software local los valida, guarda y analiza.
3. La IA recibe únicamente información relevante y estructurada.
4. La respuesta distingue hechos, interpretación, hipótesis y siguientes pruebas.

---

## 4. Visión del producto

La visión es crear una herramienta que permita responder de forma razonada a preguntas como:

* ¿Qué ocurrió exactamente cuando el coche dio un tirón?
* ¿Qué señales cambiaron primero?
* ¿El problema solo aparece en frío o también en caliente?
* ¿La reparación realizada produjo una mejora medible?
* ¿Qué averías están activas, cuáles son históricas y cuáles se repiten?
* ¿Qué comprobación conviene realizar antes de comprar una pieza?
* ¿Qué información sería necesario obtener con una herramienta específica del fabricante?

El valor principal no es “adivinar la pieza averiada”, sino **transformar datos dispersos en evidencias, hipótesis ordenadas y un plan de comprobación**.

---

## 5. Principios fundamentales

### 5.1. Los datos mandan

Toda conclusión debe apoyarse en uno o varios de estos elementos:

* Código DTC real.
* Freeze frame real.
* Señal registrada.
* Comparación entre señales.
* Comparación entre sesiones.
* Regla diagnóstica documentada.
* Información proporcionada por el usuario.

Si no existen datos suficientes, el sistema debe decirlo claramente.

### 5.2. Primero análisis determinista, después IA

La IA no debe recibir una serie temporal enorme y “mirarla”. Antes deben calcularse localmente:

* Mínimos, máximos y medias.
* Variabilidad.
* Pendientes y velocidad de cambio.
* Caídas y picos.
* Tiempo fuera de rango.
* Correlaciones.
* Calidad de la captura.
* Ventanas alrededor de eventos.
* Comparaciones con sesiones anteriores.

### 5.3. Solo lectura en la primera versión

La primera versión no debe permitir:

* Borrar DTC.
* Accionar actuadores.
* Enviar comandos CAN arbitrarios.
* Modificar adaptaciones.
* Codificar centralitas.
* Reprogramar unidades.
* Programar llaves.
* Desactivar sistemas.

### 5.4. Multimarca sin fingir universalidad

El sistema debe funcionar con los parámetros OBD-II/EOBD que exponga cada vehículo. No debe asumir que todos los coches ofrecen los mismos PIDs.

### 5.5. Explicar la incertidumbre

La aplicación debe diferenciar siempre:

* **Dato medido.**
* **Anomalía detectada.**
* **Interpretación.**
* **Hipótesis.**
* **Prueba recomendada.**
* **Diagnóstico confirmado externamente.**

### 5.6. La aplicación debe ser útil sin Internet

Sin conexión a Internet deben seguir funcionando:

* Conexión con el vehículo.
* Descubrimiento de PIDs.
* Lectura de datos.
* Grabación de sesiones.
* Dashboard.
* Análisis matemático.
* Reglas locales.
* Comparación de sesiones.
* Informes básicos.

La IA remota será una capa opcional.

---

## 6. Alcance de la primera versión estable

La primera versión estable debe incluir:

1. Conexión Bluetooth con OBDLink LX en Windows.
2. Selección automática o manual del puerto COM.
3. Detección del estado de conexión.
4. Identificación básica del vehículo.
5. Descubrimiento automático de PIDs compatibles.
6. Lectura de DTC genéricos.
7. Lectura de freeze frame cuando esté disponible.
8. Visualización de telemetría en tiempo real.
9. Perfiles de captura predefinidos.
10. Perfiles de captura personalizados.
11. Grabación robusta de sesiones.
12. Marcadores de síntomas.
13. Gráficas sincronizadas.
14. Línea temporal de eventos.
15. Comparación entre sesiones.
16. Historial por vehículo.
17. Registro de reparaciones y notas.
18. Motor de análisis determinista.
19. Motor de reglas diagnósticas.
20. Integración opcional con IA.
21. Generación de informes.
22. Exportación e importación de datos.
23. Auditoría de operaciones.
24. Servidor MCP de solo lectura en una fase posterior.

---

## 7. Fuera de alcance en la primera versión

No se intentará implementar inicialmente:

* Cobertura universal de ABS, airbag, cambio, climatización o confort.
* Diagnóstico profundo propietario de todas las marcas.
* Pruebas de actuadores.
* Adaptaciones y codificación.
* Reprogramación mediante J2534.
* Diagnosis oficial OEM.
* Interpretación automática de ruidos.
* Geolocalización y mapas.
* Estimación precisa de potencia de motor.
* Sustitución de un osciloscopio, multímetro o manómetro.
* Diagnóstico automático concluyente de averías mecánicas.
* Aplicación móvil nativa.
* Servicio en la nube obligatorio.
* Control remoto del vehículo.

Estas capacidades podrían estudiarse como extensiones independientes.

---

## 8. Usuario objetivo

El usuario principal es una persona aficionada a la mecánica, la electrónica o la programación que quiere entender mejor el comportamiento de distintos coches.

No se presupone que el usuario sea mecánico profesional, pero sí que puede:

* Conectar un adaptador OBD.
* Poner el contacto o arrancar el vehículo.
* Realizar una prueba de conducción de forma segura.
* Describir un síntoma.
* Interpretar instrucciones sencillas de comprobación.

La interfaz debe evitar exigir conocimientos de programación.

---

## 9. Casos de uso principales

### 9.1. Leer una luz de avería

El usuario conecta el adaptador, abre la aplicación y obtiene:

* Código.
* Estado.
* Descripción.
* Freeze frame.
* Posibles sistemas implicados.
* Comprobaciones recomendadas.
* Nivel de confianza.

### 9.2. Investigar un tirón intermitente

El usuario inicia una sesión, conduce con un acompañante y marca el momento del tirón. La aplicación analiza los segundos anteriores y posteriores.

### 9.3. Analizar consumo elevado

Se comparan sesiones equivalentes y se estudian temperaturas, carga, mezcla, MAF, MAP y otros PIDs disponibles.

### 9.4. Comprobar una reparación

El usuario registra una sesión antes y otra después de cambiar, limpiar o reparar un componente.

### 9.5. Analizar arranque en frío

Se registra desde antes del arranque hasta la estabilización del ralentí y el calentamiento.

### 9.6. Preparar información para un taller

La aplicación genera un informe con síntomas, códigos, gráficos, eventos y preguntas concretas para el profesional.

---

## 10. Hardware previsto

### 10.1. Equipo principal

* Dell Precision con Windows.
* Bluetooth funcional.
* Capacidad suficiente de almacenamiento local.

### 10.2. Interfaz de vehículo

* OBDLink LX Bluetooth original.

### 10.3. Accesorios opcionales

* Alargador OBD-II corto.
* Funda de transporte.
* Cargador para el portátil.
* Soporte seguro para el ordenador.
* Mantenedor de batería para pruebas largas con contacto puesto.

### 10.4. Regla de seguridad durante la conducción

El conductor nunca debe manipular el portátil. Las pruebas dinámicas deben realizarse con:

* Un acompañante que controle la aplicación, o
* La sesión configurada y arrancada antes de comenzar a circular.

---

## 11. Stack tecnológico propuesto

### 11.1. Backend y adquisición

* Python 3.12 o superior.
* FastAPI para API local.
* Pydantic para modelos y validación.
* `python-OBD` como primera capa de comunicación.
* Abstracción propia para evitar dependencia directa del proveedor.
* Polars o Pandas para análisis.
* NumPy y SciPy cuando sean necesarios.

### 11.2. Persistencia

* SQLite para metadatos y entidades.
* Parquet para telemetría de alta densidad.
* Archivos JSON para configuraciones exportables.

### 11.3. Frontend

* Next.js.
* TypeScript estricto.
* Cliente generado o tipado a partir de OpenAPI.
* Apache ECharts, uPlot o librería equivalente para series temporales.

### 11.4. Inteligencia artificial

* Capa de proveedor intercambiable.
* Posibilidad de utilizar OpenAI, Anthropic o un modelo local.
* Respuestas estructuradas mediante esquemas JSON.
* La aplicación nunca debe depender de un único proveedor.

### 11.5. MCP

* SDK MCP para Python.
* Transporte local `stdio` inicialmente.
* Solo herramientas de lectura y análisis.

### 11.6. Desarrollo y calidad

* Git.
* `pytest`.
* Ruff.
* Black o formateador equivalente.
* Mypy o Pyright.
* ESLint.
* Prettier.
* Playwright para pruebas de interfaz.

No se deben fijar versiones exactas en este documento. Las versiones deberán bloquearse en los archivos de dependencias del proyecto.

---

## 12. Arquitectura general

```text
┌─────────────────────────────────────────────────────────────┐
│                         VEHÍCULO                            │
└──────────────────────────────┬──────────────────────────────┘
                               │ OBD-II / EOBD
┌──────────────────────────────▼──────────────────────────────┐
│                    OBDLink LX Bluetooth                    │
└──────────────────────────────┬──────────────────────────────┘
                               │ Puerto COM virtual
┌──────────────────────────────▼──────────────────────────────┐
│                 Servicio de adquisición Python             │
│ Conexión · Descubrimiento · DTC · PIDs · Captura · Calidad │
└─────────────┬────────────────┬────────────────┬─────────────┘
              │                │                │
      ┌───────▼───────┐ ┌──────▼──────┐ ┌──────▼───────────┐
      │ SQLite        │ │ Parquet     │ │ Motor de análisis│
      │ Metadatos     │ │ Telemetría  │ │ y reglas         │
      └───────┬───────┘ └──────┬──────┘ └──────┬───────────┘
              └────────────────┴────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                        FastAPI                              │
│ REST · WebSocket · OpenAPI · Autorización local            │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                     Dashboard Next.js                      │
│ Garaje · En vivo · Sesiones · Análisis · Informes          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │     IA y servidor MCP     │
                 │ Explicación y planificación│
                 └───────────────────────────┘
```

---

## 13. Regla de separación de responsabilidades

### OBDLink LX

Solo transporta las comunicaciones entre el vehículo y el ordenador.

### Servicio de adquisición

* Controla el puerto COM.
* Consulta PIDs.
* Captura datos.
* Mide calidad.
* Gestiona reconexiones.

### Motor de análisis

* Procesa señales.
* Detecta anomalías.
* Compara sesiones.
* Ejecuta reglas.

### Backend

* Coordina servicios.
* Expone la API.
* Gestiona persistencia.

### Dashboard

* Muestra información.
* Recoge acciones del usuario.
* No debe acceder directamente al puerto COM.

### IA

* Explica.
* Resume.
* Ordena hipótesis.
* Propone siguientes pruebas.
* No captura datos directamente.
* No controla el vehículo.

---

## 14. Módulos del sistema

### 14.1. Gestor del adaptador

Responsabilidades:

* Buscar puertos COM.
* Identificar el OBDLink.
* Conectar y desconectar.
* Detectar contacto apagado.
* Detectar vehículo ausente.
* Recuperarse de desconexiones.
* Evitar accesos simultáneos al puerto.
* Exponer estado y latencia.

Estados recomendados:

```text
ADAPTER_NOT_FOUND
ADAPTER_FOUND
CONNECTING
ADAPTER_CONNECTED
VEHICLE_NOT_RESPONDING
VEHICLE_CONNECTED
CAPTURING
CONNECTION_LOST
RECONNECTING
ERROR
```

### 14.2. Descubrimiento del vehículo

Debe:

* Leer VIN cuando esté disponible.
* Detectar protocolo.
* Consultar PIDs anunciados.
* Comprobar qué PIDs responden realmente.
* Medir frecuencia y estabilidad.
* Solicitar manualmente datos no disponibles.
* Crear un perfil por vehículo.

### 14.3. Lector de DTC

Debe soportar:

* Escaneo inicial.
* Escaneo final de sesión.
* DTC almacenados.
* DTC pendientes.
* DTC permanentes cuando se admitan.
* Estado de la MIL.
* Asociación con freeze frame.
* Historial de apariciones.

### 14.4. Motor de captura

Debe:

* Cargar perfiles de captura.
* Priorizar PIDs rápidos.
* Consultar PIDs lentos con menor frecuencia.
* Añadir marcas temporales monotónicas.
* Guardar calidad y latencia.
* Escribir datos progresivamente.
* No perder toda la sesión si la interfaz falla.
* Recuperarse de desconexiones.

### 14.5. Gestor de sesiones

Cada sesión debe registrar:

* Vehículo.
* Fecha y hora.
* Kilometraje.
* Tipo de prueba.
* Motor frío o caliente.
* Condiciones indicadas por el usuario.
* Sensores solicitados.
* Sensores realmente disponibles.
* DTC antes y después.
* Marcadores.
* Calidad de captura.
* Notas.
* Reparaciones relacionadas.

### 14.6. Motor de análisis

Debe trabajar sobre datos locales y producir hallazgos reproducibles.

### 14.7. Motor de reglas

Debe aplicar reglas transparentes y versionadas.

### 14.8. Servicio de IA

Debe recibir contexto estructurado, no acceso directo a la base de datos completa.

### 14.9. Generador de informes

Debe generar informes en HTML y, posteriormente, PDF.

### 14.10. Servidor MCP

Debe exponer herramientas de consulta sin acceso directo al adaptador.

---

## 15. Parámetros que podrían monitorizarse

La disponibilidad depende de cada coche. Algunos ejemplos son:

### Motor y conducción

* RPM.
* Velocidad.
* Carga calculada.
* Posición del acelerador.
* Posición de mariposa.
* Tiempo desde arranque.

### Temperaturas

* Refrigerante.
* Aire de admisión.
* Aceite.
* Ambiente.
* Catalizador.

### Admisión

* MAF.
* MAP.
* Presión barométrica.
* EGR ordenada.
* Error de EGR.

### Combustible y mezcla

* Estado del sistema de combustible.
* Presión de combustible.
* Presión de rail.
* Fuel trim a corto plazo.
* Fuel trim a largo plazo.
* Relación lambda.
* Caudal de combustible.

### Emisiones

* Sondas de oxígeno.
* Monitores de emisiones.
* Estado de catalizador.
* Estado de EGR.
* Datos Mode 06 cuando sean fiables.

### Sistema eléctrico

* Tensión del adaptador.
* Tensión informada por ECU.

El sistema no debe mostrar indicadores de parámetros que el coche no ofrezca.

---

## 16. Perfiles de captura

### 16.1. Arranque en frío

Objetivo: estudiar arranque, tensión, temperaturas y estabilización.

Señales preferentes:

* Tensión.
* RPM.
* Refrigerante.
* Admisión.
* MAF.
* MAP.
* Fuel trims.
* Presión de combustible.

### 16.2. Ralentí

Objetivo: estudiar estabilidad y oscilaciones.

### 16.3. Calentamiento

Objetivo: medir curva de temperatura y estabilidad.

### 16.4. Aceleración controlada

Objetivo: observar respuesta de motor, aire y combustible.

### 16.5. Conducción constante

Objetivo: estudiar temperaturas, mezcla y estabilidad bajo carga uniforme.

### 16.6. Síntoma intermitente

Objetivo: registrar durante más tiempo y marcar eventos.

### 16.7. Perfil personalizado

El usuario elige señales, prioridad y frecuencia objetivo.

---

## 17. Marcadores de eventos

El usuario debe poder marcar:

* Tirón.
* Pérdida de potencia.
* Humo.
* Vibración.
* Ralentí irregular.
* Ruido.
* Testigo encendido.
* Cambio brusco.
* Evento personalizado.

Cada marcador debe guardar:

* Marca temporal monotónica.
* Marca UTC.
* Tipo.
* Texto opcional.
* Usuario.
* Sesión.

El análisis debe extraer automáticamente una ventana configurable, por ejemplo:

* 10 segundos antes.
* Momento del evento.
* 10 segundos después.

---

## 18. Modelo de datos

### 18.1. Entidades principales

#### `Vehicle`

* `id`
* `vin_encrypted`
* `vin_hash`
* `display_name`
* `make`
* `model`
* `year`
* `engine`
* `fuel_type`
* `notes`
* `created_at`
* `updated_at`

#### `Adapter`

* `id`
* `name`
* `serial_number`
* `firmware_version`
* `preferred_com_port`
* `last_seen_at`

#### `VehicleCapability`

* `vehicle_id`
* `pid_name`
* `mode`
* `pid`
* `supported_reported`
* `supported_verified`
* `unit`
* `avg_latency_ms`
* `success_rate`
* `last_verified_at`

#### `DtcScan`

* `id`
* `vehicle_id`
* `session_id`
* `scan_type`
* `mil_status`
* `created_at`

#### `DtcRecord`

* `id`
* `scan_id`
* `code`
* `status`
* `description`
* `raw_payload`

#### `FreezeFrame`

* `id`
* `dtc_record_id`
* `parameter`
* `value`
* `unit`

#### `CaptureProfile`

* `id`
* `name`
* `description`
* `signal_configuration_json`

#### `Session`

* `id`
* `vehicle_id`
* `profile_id`
* `started_at`
* `ended_at`
* `odometer_km`
* `engine_condition`
* `notes`
* `data_file`
* `capture_quality_score`
* `status`

#### `EventMarker`

* `id`
* `session_id`
* `timestamp_offset_ms`
* `event_type`
* `note`

#### `AnalysisRun`

* `id`
* `session_id`
* `analysis_version`
* `created_at`
* `status`

#### `Finding`

* `id`
* `analysis_run_id`
* `finding_type`
* `severity`
* `confidence`
* `start_ms`
* `end_ms`
* `evidence_json`
* `message`

#### `RepairAction`

* `id`
* `vehicle_id`
* `performed_at`
* `description`
* `parts`
* `cost`
* `notes`

#### `Report`

* `id`
* `vehicle_id`
* `session_id`
* `report_type`
* `file_path`
* `created_at`

#### `AuditLog`

* `id`
* `timestamp`
* `actor`
* `action`
* `parameters_json`
* `result`

### 18.2. Telemetría en Parquet

Columnas mínimas:

```text
session_id
monotonic_ns
utc_timestamp
signal_id
signal_name
value
unit
quality_flag
latency_ms
source_ecu
raw_value_optional
```

Para mejorar rendimiento, podrá utilizarse un formato ancho por bloque temporal, siempre que exista una capa de acceso uniforme.

---

## 19. Calidad de los datos

Cada muestra debe clasificarse con una bandera:

```text
VALID
TIMEOUT
NO_DATA
OUT_OF_RANGE
DECODE_ERROR
STALE
INTERPOLATED
CONNECTION_LOST
```

Cada sesión debe calcular:

* Porcentaje de muestras válidas.
* Frecuencia real por señal.
* Latencia media y percentiles.
* Número de reconexiones.
* Duración sin datos.
* PIDs eliminados por inestabilidad.

No se debe interpolar automáticamente para diagnosis. Si se interpola para visualización, los datos deben quedar marcados.

---

## 20. Sincronización temporal

Se utilizarán dos tiempos:

* Reloj monotónico para ordenar y calcular intervalos.
* UTC para mostrar fechas y relacionar sesiones.

Nunca se utilizará únicamente la hora del sistema para medir duraciones, porque puede cambiar.

Todas las señales deben alinearse sobre una línea temporal común antes de comparar.

---

## 21. Análisis determinista

### 21.1. Estadísticas básicas

* Mínimo.
* Máximo.
* Media.
* Mediana.
* Percentiles.
* Desviación estándar.
* Rango intercuartílico.

### 21.2. Calidad de señal

* Señal congelada.
* Saltos imposibles.
* Valores ausentes.
* Saturación.
* Cambio de unidad.
* Frecuencia insuficiente.

### 21.3. Dinámica

* Primera derivada.
* Pendiente.
* Tiempo de respuesta.
* Pico.
* Caída.
* Sobreimpulso.
* Tiempo de recuperación.

### 21.4. Correlación

* Correlación lineal.
* Correlación con desfase.
* Coincidencia de eventos.
* Orden temporal de cambios.

### 21.5. Comparación entre sesiones

* Re-muestreo a una base común.
* Normalización por condición.
* Comparación de intervalos equivalentes.
* Comparación antes y después.
* Comparación frío y caliente.

### 21.6. Detección de anomalías

La primera versión debe usar métodos explicables:

* Umbrales configurables.
* IQR.
* Z-score cuando proceda.
* Cambio de régimen.
* Diferencia respecto a línea base del mismo vehículo.
* Persistencia temporal.

No se debe comenzar con modelos de machine learning opacos.

---

## 22. Sistema de reglas diagnósticas

Las reglas deben almacenarse fuera del código, por ejemplo en YAML.

Ejemplo conceptual:

```yaml
id: coolant_low_stable_temperature
version: 1
applies_to:
  fuel_types: [gasoline, diesel]
requirements:
  - coolant_temp
  - vehicle_speed
conditions:
  - coolant_temp remains_below 78 for 900s
  - vehicle_speed above 50 for 600s
result:
  classification: compatible_pattern
  message: El motor permanece a una temperatura baja durante circulación estable.
  hypotheses:
    - termostato abierto
    - sensor de temperatura incoherente
    - condiciones ambientales o carga insuficiente
  recommended_checks:
    - comparar temperatura inicial con temperatura ambiente
    - verificar con medición externa
```

Cada regla debe incluir:

* Identificador.
* Versión.
* Tipos de motor aplicables.
* Señales obligatorias.
* Condiciones.
* Excepciones.
* Mensaje.
* Hipótesis.
* Pruebas recomendadas.
* Nivel máximo de confianza permitido.

---

## 23. Escala de confianza

La confianza no debe ser una opinión de la IA. Debe calcularse a partir de factores conocidos.

Factores:

* Calidad de datos.
* Número de señales de apoyo.
* Número de repeticiones.
* Existencia de DTC relacionado.
* Presencia de datos contradictorios.
* Comparación con una sesión normal.
* Especificidad de la regla.

Niveles visibles:

* **Baja:** indicio aislado o datos insuficientes.
* **Media:** patrón coherente y repetido, pero con varias causas posibles.
* **Alta:** múltiples evidencias coherentes y pruebas externas compatibles.
* **Confirmada:** solo cuando el usuario registra una comprobación o reparación que lo demuestra.

La IA no puede elevar por sí sola una hipótesis a “confirmada”.

---

## 24. Contrato de comportamiento de la IA

La IA debe responder siempre con esta estructura:

1. **Resumen.**
2. **Datos observados.**
3. **Interpretación.**
4. **Hipótesis ordenadas.**
5. **Comprobaciones recomendadas.**
6. **Datos que faltan.**
7. **Nivel de confianza.**
8. **Advertencias de seguridad.**

### Reglas obligatorias

* No inventar sensores.
* No inventar valores.
* No suponer que un PID solicitado existe.
* No confundir MAP con presión de turbo solicitada.
* No aplicar fuel trims de gasolina a un diésel si no son relevantes.
* No recomendar sustituir piezas únicamente por un DTC.
* No ocultar datos contradictorios.
* No afirmar que un freeze frame contiene fecha o todos los sensores.
* No afirmar que OBD-II genérico cubre todas las centralitas.
* No ejecutar operaciones de escritura.
* Identificar claramente las limitaciones del conjunto de datos.

### Contexto enviado a la IA

Debe enviarse un objeto estructurado similar a:

```json
{
  "vehicle": {
    "id": "vehicle-01",
    "fuel_type": "gasoline",
    "engine": "unknown",
    "protocol": "ISO_15765_4"
  },
  "symptom": "tirón bajo aceleración",
  "dtcs": [],
  "freeze_frame": {},
  "session_quality": {
    "valid_samples_percent": 97.8
  },
  "events": [
    {
      "offset_ms": 196420,
      "type": "jerk",
      "findings": []
    }
  ],
  "missing_data": ["boost_requested"]
}
```

No se enviará el VIN completo salvo autorización explícita.

---

## 25. Funciones del dashboard

### 25.1. Pantalla de inicio

* Estado del adaptador.
* Vehículo actual.
* Botón de conexión.
* Últimos vehículos.
* Últimas sesiones.

### 25.2. Garaje

* Lista de vehículos.
* Alias.
* Última conexión.
* DTC activos conocidos.
* Número de sesiones.
* Reparaciones registradas.

### 25.3. Conexión

* Puerto COM.
* Adaptador.
* Firmware.
* Protocolo.
* Tensión.
* Latencia.
* Estado.

### 25.4. Datos en vivo

* Tarjetas configurables.
* Gráficas.
* Calidad de datos.
* Frecuencia real.
* Pausar visualización sin parar captura.

### 25.5. Nueva sesión

* Selección de vehículo.
* Tipo de prueba.
* Motor frío/caliente.
* Kilometraje.
* Notas.
* Sensores.
* Inicio y parada.

### 25.6. Marcadores

* Botones grandes.
* Atajos de teclado.
* Nota rápida.

### 25.7. Análisis

* Gráficas sincronizadas.
* Zoom.
* Selección de intervalo.
* Eventos.
* Hallazgos.
* Calidad.

### 25.8. Comparación

* Selección de dos sesiones.
* Señales comunes.
* Diferencias estadísticas.
* Superposición.
* Antes/después.

### 25.9. IA

* Preguntas sugeridas.
* Contexto visible.
* Evidencias enlazadas.
* Respuesta estructurada.

### 25.10. Informes

* Vista previa.
* Exportación.
* Opción de anonimizar VIN.

---

## 26. API local propuesta

### Adaptador

```text
GET    /api/adapter/status
GET    /api/adapter/ports
POST   /api/adapter/connect
POST   /api/adapter/disconnect
POST   /api/adapter/reconnect
```

### Vehículo

```text
GET    /api/vehicles
POST   /api/vehicles
GET    /api/vehicles/{vehicle_id}
PATCH  /api/vehicles/{vehicle_id}
POST   /api/vehicles/discover
GET    /api/vehicles/{vehicle_id}/capabilities
```

### DTC

```text
POST   /api/vehicles/{vehicle_id}/dtc-scans
GET    /api/dtc-scans/{scan_id}
GET    /api/vehicles/{vehicle_id}/dtcs
GET    /api/dtc-records/{dtc_id}/freeze-frame
```

### Sesiones

```text
POST   /api/sessions
GET    /api/sessions
GET    /api/sessions/{session_id}
POST   /api/sessions/{session_id}/start
POST   /api/sessions/{session_id}/stop
POST   /api/sessions/{session_id}/markers
GET    /api/sessions/{session_id}/signals
GET    /api/sessions/{session_id}/quality
```

### Análisis

```text
POST   /api/sessions/{session_id}/analysis
GET    /api/analysis/{analysis_id}
GET    /api/sessions/{session_id}/findings
POST   /api/comparisons
GET    /api/comparisons/{comparison_id}
```

### IA

```text
POST   /api/ai/explain-dtcs
POST   /api/ai/analyze-session
POST   /api/ai/generate-test-plan
POST   /api/ai/generate-report
```

### Informes

```text
POST   /api/reports
GET    /api/reports/{report_id}
GET    /api/reports/{report_id}/download
```

### WebSocket

```text
WS     /api/live
```

Los endpoints deben utilizar modelos tipados y respuestas estables.

---

## 27. Herramientas MCP previstas

```text
get_adapter_status()
get_current_vehicle()
get_vehicle_capabilities(vehicle_id)
list_fault_codes(vehicle_id)
get_freeze_frame(dtc_id)
list_sessions(vehicle_id)
get_session_summary(session_id)
get_event_window(session_id, marker_id)
find_anomalies(session_id)
compare_sessions(session_a, session_b)
generate_test_plan(session_id)
generate_report(session_id)
```

No se implementarán inicialmente:

```text
clear_dtc()
send_raw_command()
send_can_frame()
run_actuator()
write_adaptation()
change_coding()
```

---

## 28. Seguridad y privacidad

### 28.1. Seguridad del vehículo

* Solo lectura por defecto.
* Puerto COM controlado por un único servicio.
* Lista blanca de comandos.
* Sin comandos arbitrarios.
* Sin escritura desde IA.

### 28.2. Seguridad del usuario

* Avisos claros antes de pruebas dinámicas.
* El conductor no manipula la aplicación.
* No mostrar recomendaciones que impliquen riesgo sin advertencia.

### 28.3. Privacidad

* VIN cifrado localmente.
* Identificador hash para relaciones internas.
* No enviar VIN completo a la IA por defecto.
* No registrar ubicación inicialmente.
* Consentimiento antes de enviar datos a servicios externos.

### 28.4. Secretos

* Claves de API en variables de entorno.
* Nunca en Git.
* Archivo `.env.example` sin valores reales.

### 28.5. Auditoría

Registrar:

* Conexiones.
* Escaneos.
* Inicio y fin de sesión.
* Solicitudes a IA.
* Herramientas MCP.
* Exportaciones.
* Errores.

---

## 29. Manejo de errores

La aplicación debe explicar errores en lenguaje comprensible.

Ejemplos:

* “No se ha encontrado el OBDLink.”
* “El adaptador está conectado, pero el vehículo no responde. Comprueba el contacto.”
* “El puerto COM está siendo utilizado por otro programa.”
* “Este vehículo no ofrece el parámetro seleccionado.”
* “La sesión continúa, pero se han perdido datos durante 3,2 segundos.”
* “No hay información suficiente para realizar este análisis.”

Los errores técnicos completos deben guardarse en logs.

---

## 30. Observabilidad y logs

Se deben separar:

* Log de aplicación.
* Log de comunicación OBD.
* Log de sesión.
* Log de análisis.
* Log de IA.
* Log de auditoría.

Cada log debe tener:

* Fecha UTC.
* Nivel.
* Módulo.
* Identificador de operación.
* Mensaje.
* Excepción cuando exista.

No deben incluirse claves de API ni VIN sin anonimizar.

---

## 31. Estrategia de pruebas

### 31.1. Pruebas unitarias

* Decodificación.
* Máquina de estados.
* Conversión de unidades.
* Estadísticas.
* Reglas.
* Modelos de datos.

### 31.2. Simulador de adaptador

Debe existir un adaptador simulado que reproduzca:

* Respuestas válidas.
* PID no soportado.
* Timeout.
* Desconexión.
* Valores fuera de rango.
* DTC.
* Freeze frame.

El desarrollo del dashboard y análisis no debe depender siempre de tener un coche conectado.

### 31.3. Pruebas de integración

* Adaptador simulado + backend.
* Backend + base de datos.
* Backend + Parquet.
* API + frontend.
* IA + esquemas estructurados.

### 31.4. Pruebas hardware-in-the-loop

Con OBDLink y vehículo real:

* Contacto apagado.
* Contacto puesto.
* Motor arrancado.
* Adaptador desenchufado.
* Bluetooth desconectado.
* Cambio de vehículo.

### 31.5. Pruebas E2E

Flujo completo:

1. Abrir aplicación.
2. Conectar adaptador.
3. Detectar vehículo.
4. Crear sesión.
5. Añadir marcador.
6. Detener.
7. Analizar.
8. Generar informe.

---

## 32. Matriz mínima de validación multimarca

Validar al menos con:

* Gasolina atmosférico.
* Gasolina turbo.
* Diésel.
* Vehículo CAN moderno.
* Vehículo más antiguo con protocolo diferente.
* Vehículo sin DTC.
* Vehículo con DTC conocido.
* Vehículo con PIDs anunciados pero inestables.

No se debe afirmar compatibilidad con una marca o modelo hasta probarla o disponer de evidencia suficiente.

---

## 33. Criterios de aceptación

### Conexión

* Detecta el adaptador o explica por qué no puede.
* Reconecta sin reiniciar toda la aplicación.
* No corrompe la sesión ante una desconexión.

### Descubrimiento

* No muestra PIDs no verificados como disponibles.
* Guarda capacidades por vehículo.

### Captura

* Usa reloj monotónico.
* Guarda progresivamente.
* Identifica muestras inválidas.
* Informa de frecuencia real.

### Dashboard

* Permite completar el flujo sin terminal.
* Mantiene sincronizadas las gráficas.
* Muestra calidad de datos.

### Análisis

* Cada hallazgo incluye intervalo y evidencias.
* Distingue anomalía de diagnóstico.
* No inventa datos ausentes.

### IA

* Respeta la estructura obligatoria.
* Indica incertidumbre.
* No recomienda piezas como certeza sin confirmación.
* No controla el vehículo.

### Privacidad

* VIN oculto en exportaciones cuando se solicite.
* Datos externos enviados solo con consentimiento.

---

## 34. Definición de “terminado”

Una función no está terminada hasta que:

* Tiene requisitos claros.
* Está implementada.
* Tiene pruebas.
* Maneja errores.
* Está documentada.
* Aparece correctamente en la interfaz.
* No rompe compatibilidad con sesiones anteriores.
* Respeta seguridad y privacidad.

---

## 35. Estructura de carpetas recomendada

```text
vehicle-ai-diagnostics/
├── apps/
│   ├── api/
│   └── dashboard/
├── packages/
│   ├── obd-core/
│   ├── domain-models/
│   ├── analysis-engine/
│   ├── rules-engine/
│   ├── report-generator/
│   └── ai-contracts/
├── services/
│   ├── collector/
│   └── mcp-server/
├── data/
│   ├── database/
│   ├── telemetry/
│   ├── reports/
│   └── backups/
├── rules/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
├── simulator/
├── scripts/
├── docs/
│   ├── PROJECT_SPEC.md
│   ├── ROADMAP.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATA_MODEL.md
│   └── SECURITY.md
├── .env.example
├── README.md
└── docker-compose.dev.yml
```

No es obligatorio utilizar un monorepo si añade complejidad innecesaria. La estructura podrá simplificarse mientras se mantenga la separación de responsabilidades.

---

## 36. Convenciones de desarrollo

### Python

* Tipado estático.
* Funciones pequeñas.
* Excepciones propias del dominio.
* Nada de `print` para logs.
* Modelos Pydantic en límites de API.
* Dependencias inyectables.

### TypeScript

* Modo estricto.
* Evitar `any`.
* Tipos generados desde OpenAPI cuando sea viable.
* Componentes presentacionales separados de lógica de datos.

### Git

* Commits pequeños y descriptivos.
* Una funcionalidad por rama.
* Pull requests con pruebas y captura de pantalla cuando afecte a UI.

### Base de datos

* Migraciones versionadas.
* No editar manualmente esquemas de producción.
* Copia de seguridad antes de migraciones destructivas.

---

## 37. Configuración

Variables recomendadas:

```text
APP_ENV=production
DATABASE_PATH=./data/database/app.db
TELEMETRY_PATH=./data/telemetry
REPORT_PATH=./data/reports
LOG_LEVEL=INFO
OBD_COM_PORT=
OBD_BAUDRATE=
AI_PROVIDER=disabled
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
SEND_VIN_TO_AI=false
```

La aplicación debe poder funcionar con `AI_PROVIDER=disabled`.

---

## 38. Informes

### Informe de escaneo

* Datos del vehículo.
* Protocolo.
* DTC.
* Freeze frame.
* Estado de monitores.

### Informe de sesión

* Tipo de prueba.
* Condiciones.
* Señales.
* Calidad.
* Eventos.
* Gráficas.

### Informe de diagnosis asistida

* Síntoma.
* Datos observados.
* Hallazgos.
* Hipótesis.
* Pruebas recomendadas.
* Datos ausentes.
* Confianza.

### Informe antes/después

* Intervención.
* Sesiones comparadas.
* Métricas.
* Mejoras.
* Problemas persistentes.

---

## 39. Ampliaciones futuras

Una vez estable la capa OBD genérica, podrán añadirse plugins independientes:

* Importador de FORScan.
* Importador de VCDS.
* Importador de ISTA.
* Importador de Launch, Autel o Bosch.
* Integración TeslaMate.
* Interfaces J2534.
* PIDs propietarios documentados.
* GPS externo.
* Captura de audio para relacionar ruidos.
* Modelos locales de IA.
* Sincronización cifrada opcional.

Las extensiones no deben romper el núcleo genérico.

---

## 40. Decisiones que deben permanecer abiertas

* Librería definitiva de gráficos.
* Pandas frente a Polars.
* Forma final de empaquetado Windows.
* Proveedor inicial de IA.
* Formato exacto de telemetría en Parquet.
* Estrategia de cifrado local del VIN.
* Si el frontend y backend se distribuyen juntos o por separado.
* Si se implementa inicialmente un monorepo.

Estas decisiones deben resolverse mediante prototipos pequeños y ADRs, no por preferencia personal sin pruebas.

---

## 41. Architecture Decision Records

Toda decisión importante debe documentarse en `docs/informacion_tecnica/arquitectura/adr/`.

Ejemplos:

```text
docs/informacion_tecnica/arquitectura/adr/0001-use-sqlite-and-parquet.md
docs/informacion_tecnica/arquitectura/adr/0002-wrap-python-obd.md
docs/informacion_tecnica/arquitectura/adr/0003-read-only-first-version.md
docs/informacion_tecnica/arquitectura/adr/0004-ai-provider-abstraction.md
```

Cada ADR debe incluir:

* Contexto.
* Opciones consideradas.
* Decisión.
* Consecuencias.
* Fecha.

---

## 42. Instrucciones permanentes para la IA desarrolladora

La IA que programe este proyecto debe seguir estas reglas:

1. Leer `PROJECT_SPEC.md` y `ROADMAP.md` antes de proponer cambios.
2. No modificar el alcance silenciosamente.
3. No implementar operaciones de escritura sobre el coche.
4. No conectar el frontend directamente al puerto COM.
5. Mantener una abstracción entre la aplicación y `python-OBD`.
6. Escribir pruebas para toda lógica de análisis.
7. Crear simuladores y fixtures antes de depender de un coche real.
8. No inventar PIDs ni significados propietarios.
9. No mezclar datos reales con datos interpolados sin marcarlos.
10. No enviar datos privados a servicios externos sin autorización.
11. Mantener el sistema funcional sin IA.
12. No usar la IA como sustituto del análisis determinista.
13. Explicar las decisiones arquitectónicas importantes.
14. Proponer migraciones pequeñas y reversibles.
15. No introducir dependencias nuevas sin justificar su necesidad.
16. Evitar complejidad prematura.
17. Priorizar fiabilidad de captura frente a cantidad de funciones.
18. Mantener documentación y tipos actualizados.
19. Mostrar siempre limitaciones técnicas al usuario.
20. Nunca presentar una hipótesis mecánica como una certeza sin evidencia.

---

## 43. Formato esperado de cada tarea de desarrollo

Antes de programar una funcionalidad, la IA debe presentar:

```text
Objetivo
Archivos afectados
Cambios propuestos
Riesgos
Pruebas necesarias
Criterios de aceptación
```

Después de programarla debe indicar:

```text
Qué se ha implementado
Qué pruebas se han ejecutado
Qué limitaciones quedan
Qué documentación se ha actualizado
Siguiente paso recomendado
```

---

## 44. Primer bloque de trabajo recomendado

El primer objetivo técnico debe ser mínimo y comprobable:

> Conectar el OBDLink LX, detectar el puerto COM, leer RPM, velocidad y temperatura, guardar las muestras con tiempo monotónico y mostrar el estado de conexión.

Tareas:

1. Crear repositorio.
2. Configurar Python y pruebas.
3. Crear interfaz `VehicleAdapter`.
4. Crear implementación `PythonObdAdapter`.
5. Crear adaptador simulado.
6. Crear máquina de estados.
7. Leer tres PIDs.
8. Guardar una sesión de prueba.
9. Añadir logs.
10. Documentar cómo ejecutarlo.

No se debe comenzar con el dashboard completo, la IA o MCP hasta que esta base sea estable.

---

## 45. Primer flujo funcional objetivo

```text
1. Conectar OBDLink LX al coche.
2. Abrir la aplicación.
3. La aplicación detecta el adaptador.
4. El usuario pulsa “Conectar”.
5. Se detecta el vehículo y el protocolo.
6. Se descubren los PIDs disponibles.
7. El usuario selecciona “Prueba de síntoma”.
8. Comienza la captura.
9. El usuario o acompañante marca “Tirón”.
10. Se detiene la sesión.
11. Se muestran diez segundos antes y después.
12. El motor local identifica qué señales cambiaron.
13. La IA explica los resultados con incertidumbre.
14. Se genera un informe.
```

Este flujo representa el primer producto realmente útil.

---

## 46. Resultado final esperado

Al completar el proyecto, el usuario dispondrá de una aplicación local capaz de:

* Trabajar con distintos vehículos OBD-II.
* Crear un perfil de capacidades por coche.
* Leer y conservar códigos genéricos.
* Registrar telemetría de forma fiable.
* Marcar síntomas durante una prueba.
* Visualizar señales sincronizadas.
* Detectar anomalías explicables.
* Comparar sesiones y reparaciones.
* Mantener un historial técnico.
* Consultar los datos mediante lenguaje natural.
* Generar informes útiles.
* Reconocer cuándo los datos genéricos no son suficientes.

La definición más precisa del producto es:

> **Una plataforma multimarca de recopilación, visualización y análisis de datos OBD-II que utiliza inteligencia artificial para explicar evidencias y proponer el siguiente paso de diagnosis, sin sustituir la comprobación física ni las herramientas específicas del fabricante.**

---

## 47. Regla final del proyecto

Cuando exista conflicto entre añadir una función llamativa y mantener datos fiables, seguridad y claridad, se debe elegir siempre:

1. Fiabilidad.
2. Seguridad.
3. Trazabilidad.
4. Claridad.
5. Funcionalidad adicional.

La IA solo será útil si los datos que recibe son correctos y si el sistema reconoce honestamente sus límites.
