Roadmap completo: OBDLink LX + análisis + IA

Primero, una precisión importante: conseguir que funcione “a la perfección” en todos los coches y con todos los sensores no es posible mediante OBD-II genérico. Cada vehículo expone diferentes parámetros y muchas centralitas utilizan protocolos propietarios.

El objetivo realista es conseguir una plataforma que funcione de manera robusta, segura y automática con toda la información OBD-II que cada vehículo permita:

Vehículo
   ↓
OBDLink LX Bluetooth
   ↓
Servicio de captura en el Dell
   ↓
Base de datos y sesiones
   ↓
Análisis matemático
   ↓
Dashboard
   ↓
IA y MCP

La regla principal será:

Primero datos fiables, después gráficas, luego análisis y la IA al final.

Fase 0 — Definir exactamente el alcance
Qué incluirá la primera versión
Conexión con OBDLink LX.
Identificación del vehículo.
Descubrimiento automático de sensores compatibles.
Lectura de DTC genéricos.
Lectura de freeze frame.
Monitorización en tiempo real.
Grabación de sesiones.
Marcadores de síntomas.
Gráficas sincronizadas.
Comparación entre sesiones.
Detección de anomalías.
Interpretación mediante IA.
Informes técnicos.
Servidor MCP de solo lectura.
Qué quedará bloqueado inicialmente
Borrado de averías.
Pruebas de actuadores.
Codificación.
Adaptaciones.
Programación.
Comandos CAN arbitrarios.
Acceso profundo a ABS, airbag o cambio.
Control del vehículo mediante IA.
Resultado esperado

Una herramienta de análisis que explique:

Qué ocurrió.
Cuándo ocurrió.
Qué señales cambiaron.
Qué hipótesis son compatibles.
Qué comprobación conviene hacer después.

No afirmará automáticamente qué pieza hay que sustituir.

Fase 1 — Preparar el Dell Precision
Software base

Instalaríamos en Windows:

Git.
Python.
Visual Studio Code.
Node.js.
OBDwiz.
Controladores y utilidades de OBDLink.
Un gestor de entornos Python.
SQLite.
Navegador actualizado.

El OBDLink LX incluye OBDwiz para Windows y dispone de firmware, guías y herramientas oficiales de configuración.

Estructura inicial del proyecto
vehicle-ai-diagnostics/
├── collector/
├── backend/
├── analysis/
├── database/
├── dashboard/
├── mcp-server/
├── tests/
├── sample-data/
└── documentation/
Repositorio Git

Crearíamos desde el principio:

Rama principal estable.
Rama de desarrollo.
Registro de versiones.
Archivo de configuración de ejemplo.
Exclusión de VIN y datos personales.
Copias de seguridad de sesiones.
Criterio para completar la fase

El Dell debe poder ejecutar:

Python.
Node.js.
OBDwiz.
Una API local.
Una aplicación web vacía.
Pruebas automatizadas básicas.
Fase 2 — Comprar y verificar el OBDLink LX
Compra

Necesitaríamos:

OBDLink LX Bluetooth original.
Alargador OBD-II corto, opcional.
Funda para transportar adaptador y portátil, opcional.

No compraría todavía Raspberry Pi, interfaz J2534 ni otros adaptadores.

Primera conexión
Enchufar el LX al puerto OBD.
Poner el contacto del vehículo.
Pulsar el botón físico de conexión.
Activar Bluetooth en el Dell.
Emparejar el adaptador.
Localizar el puerto COM asignado.
Abrir OBDwiz.
Seleccionar conexión Bluetooth.
Confirmar que reconoce adaptador y vehículo.

El LX utiliza Bluetooth con ordenadores Windows y requiere acceso físico para habilitar el emparejamiento. En Windows 11 puede ser necesario activar el descubrimiento avanzado de dispositivos Bluetooth.

Actualización

Antes de desarrollar:

Comprobar versión de firmware.
Actualizar si existe una versión nueva.
Restaurar configuración de fábrica si presenta comportamientos extraños.
Registrar número de serie y versión.
Criterio para completar la fase

OBDwiz debe mostrar correctamente:

Conexión con el LX.
Conexión con la ECU.
Protocolo detectado.
RPM.
Temperatura.
Tensión.
Algún DTC o indicación de que no hay DTC.
Gráfica básica durante varios minutos.

No continuaría programando hasta que OBDwiz funcionase bien. Así distinguimos problemas de hardware de problemas de nuestro software.

Fase 3 — Crear el prototipo mínimo en Python
Objetivo

Conectar desde Python y leer tres parámetros:

RPM.
Temperatura del refrigerante.
Velocidad.

La librería python-OBD puede buscar puertos Bluetooth y USB, conectarse mediante un puerto COM concreto, consultar comandos y verificar si el vehículo los soporta.

Flujo mínimo
Abrir COM
   ↓
Detectar adaptador
   ↓
Detectar protocolo
   ↓
Confirmar ECU conectada
   ↓
Consultar RPM
   ↓
Mostrar respuesta
   ↓
Cerrar conexión correctamente
Información que registraremos
Puerto COM.
Velocidad de conexión.
Protocolo.
Estado de conexión.
Tiempo de cada consulta.
Respuestas vacías.
Errores.
Desconexiones.
Criterio para completar la fase

El programa debe:

Encontrar el LX.
Conectarse con contacto puesto.
Detectar cuando no hay vehículo.
Leer datos sin bloquearse.
Cerrar correctamente.
Mostrar errores comprensibles.
No fallar si un PID no está disponible.
Fase 4 — Construir el gestor robusto de conexión

Aquí empieza la parte verdaderamente importante.

Máquina de estados

La conexión tendrá estados claros:

ADAPTADOR_NO_ENCONTRADO
ADAPTADOR_DETECTADO
CONECTANDO
CONTACTO_APAGADO
VEHICULO_CONECTADO
CAPTURANDO
CONEXION_PERDIDA
RECONECTANDO
ERROR
Funciones necesarias
Buscar automáticamente puertos.
Permitir seleccionar COM manualmente.
Recordar el adaptador preferido.
Detectar contacto apagado.
Reconectar automáticamente.
Recuperarse tras pérdida de Bluetooth.
Evitar dos procesos usando el mismo COM.
Mostrar calidad y latencia de conexión.
Registrar los errores de bajo nivel.
Permitir reiniciar el adaptador.
Lectura asíncrona

No usaríamos consultas bloqueantes desde la interfaz. python-OBD ofrece una conexión Async con un bucle de actualización y callbacks para recibir nuevos valores sin bloquear la aplicación.

Aun así, envolveríamos la librería detrás de nuestra propia interfaz:

class VehicleAdapter:
    def connect(self): ...
    def disconnect(self): ...
    def get_status(self): ...
    def discover_commands(self): ...
    def start_capture(self, signals): ...
    def stop_capture(self): ...

Esto permitirá reemplazar python-OBD en el futuro sin rehacer toda la aplicación.

Criterio para completar la fase

La conexión debe soportar:

Encender y apagar contacto.
Desenchufar y volver a enchufar el LX.
Alejar momentáneamente el portátil.
Cerrar y abrir la aplicación.
Cambiar de vehículo.
Encontrar PIDs no compatibles.
Recibir respuestas vacías.

Nada de eso debe corromper una sesión ni cerrar la aplicación.

Fase 5 — Descubrimiento automático del vehículo
Primera conexión a cada coche

La aplicación hará un reconocimiento:

Leer VIN, si está disponible.
Detectar protocolo.
Detectar tipo de combustible.
Consultar grupos de PIDs soportados.
Probar los comandos anunciados.
Medir la frecuencia real de cada señal.
Registrar unidades.
Crear un perfil del vehículo.
Pedir manualmente marca, modelo y motor si no pueden determinarse.
Guardar kilometraje introducido por el usuario.
Perfil generado
Vehículo
├── VIN
├── Marca y modelo
├── Año
├── Motor
├── Combustible
├── Protocolo OBD
├── PIDs anunciados
├── PIDs comprobados
├── Frecuencia de lectura
└── Fecha de última conexión
Tres estados para cada PID
Compatible y comprobado.
Anunciado, pero responde de manera irregular.
No compatible.

No basta con confiar en la lista anunciada por la ECU. Algunos vehículos declaran parámetros que posteriormente responden vacíos o con valores inconsistentes.

Criterio para completar la fase

Al conectar un coche nuevo, el sistema debe crear automáticamente un panel únicamente con los sensores que ese coche realmente entrega.

Fase 6 — Diseñar el sistema de captura
Perfiles de captura

No leeremos todos los sensores a la vez. Prepararemos perfiles:

Arranque en frío
RPM.
Tensión.
Temperaturas.
MAF.
MAP.
Fuel trims.
Presión de combustible.
Ralentí
RPM.
Carga.
MAF.
MAP.
Fuel trims.
Tensión.
Aceleración
RPM.
Velocidad.
Acelerador.
Carga.
MAF.
MAP.
Presión de combustible.
Calentamiento
Refrigerante.
Admisión.
Aceite, si está disponible.
Velocidad.
Carga.
Tiempo desde arranque.
Perfil personalizado

El usuario podrá elegir manualmente sensores.

Planificador de consultas

No todos los PIDs necesitan la misma frecuencia:

RPM                    alta frecuencia
Acelerador             alta frecuencia
MAP/MAF                alta frecuencia
Temperaturas           baja frecuencia
VIN                     solo al conectar
DTC                     inicio y final
Monitores emisiones    solo bajo petición

El sistema priorizará las señales rápidas y consultará las lentas con menos frecuencia.

Datos guardados por muestra
session_id
timestamp_monotonic
timestamp_utc
pid
value
unit
ecu
quality
latency_ms
raw_response opcional
Control de calidad

Cada sesión guardará:

Frecuencia solicitada.
Frecuencia real.
Porcentaje de respuestas válidas.
Muestras perdidas.
Latencia.
Reconexiones.
Duración.
Sensores seleccionados.
Criterio para completar la fase

Una sesión de prueba debe poder:

Durar sin cerrarse inesperadamente.
Mantener marcas de tiempo coherentes.
Guardar datos aunque falle la interfaz visual.
Recuperarse de una desconexión.
Indicar qué datos faltan.
Cerrarse correctamente aunque el vehículo se apague.
Fase 7 — Diseñar la base de datos
SQLite para información estructurada

Guardaríamos:

Vehículos.
Adaptadores.
Escaneos.
DTC.
Sesiones.
Síntomas.
Eventos.
Reparaciones.
Informes.
Configuraciones.
Resultados de análisis.
Parquet para telemetría

Las muestras de sesiones largas se guardarían en archivos Parquet:

data/
├── vehicles/
│   └── VIN_HASH/
│       ├── sessions/
│       │   ├── session_001.parquet
│       │   └── session_002.parquet
│       └── reports/
Privacidad
El VIN se almacenará localmente.
En los informes se podrá ocultar.
La IA recibirá un identificador anonimizado.
La ubicación no se registrará inicialmente.
Nada se enviará a Internet sin autorización.
Copias de seguridad
Exportación de cada vehículo.
Importación posterior.
Copia automática de la base de datos.
Recuperación tras cierre incorrecto.
Versionado del esquema.
Criterio para completar la fase

Debe ser posible:

Cerrar la aplicación.
Reiniciar el Dell.
Recuperar todas las sesiones.
Exportar un vehículo.
Importarlo en otra instalación.
Detectar archivos dañados.
Mantener separados varios coches.
Fase 8 — Crear la API local

Utilizaríamos FastAPI para separar la adquisición de datos de la interfaz visual. FastAPI proporciona una API documentada automáticamente mediante OpenAPI, lo que facilita probar cada función antes de construir el dashboard.

Endpoints iniciales
GET  /adapter/status
POST /adapter/connect
POST /adapter/disconnect

GET  /vehicle/current
GET  /vehicle/supported-pids

GET  /dtc
GET  /freeze-frame

POST /sessions
POST /sessions/{id}/stop
POST /sessions/{id}/markers
GET  /sessions/{id}
GET  /sessions/{id}/signals
Comunicación en vivo

Utilizaríamos WebSocket o un flujo similar para enviar datos al dashboard sin realizar consultas repetitivas.

Criterio para completar la fase

La documentación automática de la API debe permitir:

Conectar.
Leer sensores.
Iniciar una sesión.
Añadir un marcador.
Detener la sesión.
Consultar los datos guardados.

Todo sin abrir todavía el dashboard.

Fase 9 — Construir el dashboard
Pantallas principales
Garaje
Lista de vehículos.
Última conexión.
DTC abiertos.
Número de sesiones.
Reparaciones recientes.
Conexión
Adaptador.
Puerto COM.
Protocolo.
Tensión.
Estado.
Latencia.
Calidad de datos.
Datos en vivo
Indicadores.
Gráficas.
Sensores seleccionables.
Frecuencia real.
Alertas de valores inválidos.
Sesión
Iniciar y detener.
Seleccionar perfil de captura.
Añadir marcadores.
Escribir notas.
Mostrar tiempo transcurrido.
Mostrar calidad de captura.
Análisis
Gráficas sincronizadas.
Zoom.
Selección de intervalos.
Eventos marcados.
Mínimos y máximos.
Comparación entre señales.
Comparador
Sesión A frente a sesión B.
Antes frente a después.
Frío frente a caliente.
Evento normal frente a evento anómalo.
DTC
Código.
Estado.
Descripción.
Fecha de primera aparición.
Freeze frame.
Sesiones relacionadas.
Reparaciones posteriores.
Criterio para completar la fase

Una persona sin conocimientos de programación debe poder:

Conectar el coche.
Elegir una prueba.
Empezar la captura.
Marcar un síntoma.
Terminar.
Ver el evento en una gráfica.
Guardar una nota.
Exportar la sesión.
Fase 10 — Crear el motor de análisis determinista

La IA todavía no entra.

Análisis básicos
Mínimo.
Máximo.
Media.
Mediana.
Percentiles.
Desviación estándar.
Derivada o velocidad de cambio.
Tiempo fuera de intervalo.
Valores repetidos.
Saltos imposibles.
Señales congeladas.
Muestras ausentes.
Análisis de eventos

Para cada marcador extraeremos:

10 segundos anteriores
momento del evento
10 segundos posteriores

Calcularemos:

Qué señal cambió primero.
Magnitud del cambio.
Duración.
Recuperación.
Señales correlacionadas.
Diferencias respecto a periodos normales.
Análisis por tipo de prueba
Temperatura
Tiempo de calentamiento.
Pendiente.
Temperatura estable.
Caídas durante circulación.
Comparación entre sesiones.
Ralentí
Variabilidad de RPM.
Oscilaciones periódicas.
Relación con MAF, MAP o fuel trims.
Admisión
Coherencia entre acelerador, carga, MAF y MAP.
Caídas simultáneas.
Respuesta retardada.
Combustión en gasolina
Fuel trims en ralentí y carga.
Diferencias entre bancadas.
Relación con MAF y sondas.
Sistema eléctrico
Tensión mínima.
Estabilidad de carga.
Caídas coincidentes con eventos.
Criterio para completar la fase

Todo hallazgo debe contener:

Qué se detectó
En qué intervalo
Qué señales lo sustentan
Cuánto cambió
Cuántas veces se repitió
Calidad de los datos

Nunca mostrará “sensor averiado” solo porque un valor sea extraño.

Fase 11 — Crear un sistema de reglas

La siguiente capa será una biblioteca de reglas transparentes.

Ejemplo conceptual:

SI:
  el refrigerante tarda demasiado en subir
  Y después queda persistentemente bajo
  Y el vehículo está circulando

ENTONCES:
  patrón compatible con funcionamiento frío

COMPROBAR:
  condiciones ambientales
  termostato
  sensor
  carga y tipo de recorrido
Clasificación

Cada resultado será una de estas categorías:

Dato medido.
Anomalía matemática.
Patrón compatible.
Hipótesis.
Prueba recomendada.
Conclusión confirmada externamente.
Confianza

La confianza dependerá de:

Calidad de captura.
Número de repeticiones.
PIDs disponibles.
Coherencia entre señales.
Conocimiento del vehículo.
Existencia de DTC.
Comparación con sesiones normales.
Criterio para completar la fase

El motor de reglas debe ser útil incluso con Internet apagado y sin IA.

Fase 12 — Añadir la inteligencia artificial

Solo en este momento.

Información enviada a la IA

No enviaremos continuamente toda la telemetría. Enviaremos:

Perfil anonimizado.
Tipo de motor.
Síntoma.
DTC.
Freeze frame.
Resumen estadístico.
Ventanas anómalas.
Hallazgos del motor de reglas.
Reparaciones previas.
Datos ausentes.
Qué podrá hacer
Explicar DTC.
Resumir una sesión.
Relacionar hallazgos.
Priorizar hipótesis.
Recomendar comprobaciones.
Formular preguntas al usuario.
Generar un informe.
Explicar limitaciones.
Formato obligatorio de respuesta
1. Datos observados
2. Interpretación
3. Posibles causas
4. Pruebas recomendadas
5. Datos que faltan
6. Nivel de confianza
7. Advertencias
Barreras contra alucinaciones

La IA no podrá:

Inventar sensores no disponibles.
Suponer valores solicitados si solo tenemos valores reales.
Declarar una pieza averiada sin evidencia.
Ocultar datos contradictorios.
recomendar borrar DTC antes de guardar el diagnóstico.
Ejecutar órdenes sobre el coche.
Presentar hipótesis como hechos.
Criterio para completar la fase

Cada afirmación técnica debe poder relacionarse con:

Un DTC.
Una medición.
Una regla.
Una fuente documental.
O quedar marcada explícitamente como hipótesis.
Fase 13 — Crear el servidor MCP

El MCP será una interfaz, no el núcleo del proyecto.

El SDK oficial de MCP para Python permite exponer herramientas y recursos mediante transportes como stdio y Streamable HTTP. Para una instalación local comenzaríamos con stdio.

Herramientas MCP
get_adapter_status()
get_current_vehicle()
get_supported_pids()
read_fault_codes()
get_freeze_frame()
list_sessions()
get_session_summary()
get_event_window()
find_anomalies()
compare_sessions()
generate_test_plan()
generate_report()
Recursos MCP
vehicle://current/profile
vehicle://current/faults
session://{id}/summary
session://{id}/events
report://{id}
Lo que no se expondrá
clear_dtc()
send_raw_obd_command()
send_can_frame()
change_configuration()
run_actuator()
write_adaptation()
Auditoría

Cada llamada guardará:

Hora.
Herramienta.
Parámetros.
Resultado.
Cliente.
Errores.
Criterio para completar la fase

Un cliente MCP debe poder preguntar:

“Analiza la última sesión y prepara el siguiente plan de prueba.”

Y obtener una respuesta sin acceder directamente al puerto COM.

Fase 14 — Crear protocolos de prueba repetibles

Prepararemos instrucciones para que los datos sean comparables.

Protocolo de arranque frío
Vehículo parado suficientes horas.
Registrar temperatura ambiental.
Contacto antes del arranque.
No acelerar.
Registrar hasta estabilización.
Protocolo de calentamiento
Ruta similar.
Misma selección de PIDs.
Registrar condiciones ambientales.
Evitar comparar tráfico urbano con autovía.
Protocolo de aceleración
Lugar seguro.
Misma marcha o condición.
Intervalo de RPM comparable.
Acompañante manejando el portátil.
Sin manipular el equipo mientras se conduce.
Protocolo de ralentí
Motor a temperatura.
Consumidores eléctricos anotados.
Climatizador indicado.
Duración estándar.
Sin intervenciones durante la captura.
Criterio para completar la fase

Dos personas deben poder repetir la misma prueba y obtener datos razonablemente comparables.

Fase 15 — Validación con varios vehículos

No validaremos el proyecto con un solo coche.

Conjunto mínimo recomendable
Gasolina atmosférico.
Gasolina turbo.
Diésel.
Vehículo de distinta antigüedad.
Vehículo moderno con CAN.
Un coche sin DTC.
Uno con un fallo conocido.
Uno con un PID anunciado pero irregular.
Casos que debemos provocar o simular

Sin crear averías peligrosas:

Contacto apagado.
Motor apagado con contacto.
Desconexión Bluetooth.
Adaptador desenchufado.
PID no soportado.
Respuesta vacía.
Sesión interrumpida.
Archivo dañado.
VIN no disponible.
Cambio de vehículo.
DTC desconocido.
IA sin suficiente información.
Métricas de validación
Porcentaje de sesiones guardadas correctamente.
Pérdidas de conexión.
Frecuencia real.
Muestras válidas.
Tiempo de recuperación.
Consistencia de unidades.
Errores del descubrimiento de PIDs.
Falsas alertas.
Respuestas incorrectas de IA.
Fase 16 — Generación de informes
Informe de escaneo
Vehículo.
Fecha.
Protocolo.
PIDs disponibles.
DTC.
Freeze frame.
Monitores.
Informe de sesión
Condiciones.
Sensores.
Calidad de captura.
Eventos.
Gráficas.
Anomalías.
Informe de diagnosis
Síntoma.
Evidencias.
Interpretación.
Hipótesis ordenadas.
Pruebas recomendadas.
Riesgos.
Datos ausentes.
Confianza.
Informe antes/después
Reparación realizada.
Sesiones comparadas.
Métricas anteriores.
Métricas posteriores.
Mejoras.
Problemas persistentes.
Fase 17 — Empaquetar la aplicación
Inicio simplificado

El usuario no debería abrir varias terminales.

Crearemos un lanzador que:

Compruebe Bluetooth.
Arranque el backend.
Compruebe la base de datos.
Arranque el dashboard.
Abra el navegador.
Muestre errores de forma comprensible.
Instalación

Prepararemos:

Instalador de Windows.
Configuración inicial.
Carpeta de datos.
Sistema de actualización.
Exportación de copias.
Modo diagnóstico.
Registro de errores.
Funcionamiento sin Internet

Sin conexión, debe seguir funcionando:

Captura.
Historial.
Gráficas.
Comparación.
Motor matemático.
Reglas.
Informes básicos.

Solo quedarían desactivados:

Análisis mediante modelo remoto.
Consulta de documentación online.
Sincronización opcional.
Fase 18 — Criterios para considerar el proyecto terminado

No lo consideraría listo hasta cumplir lo siguiente.

Conexión
Detecta el OBDLink automáticamente.
Se recupera de desconexiones.
No bloquea la interfaz.
No pierde toda la sesión por un error.
Datos
Normaliza unidades.
Conserva marcas temporales.
Identifica muestras inválidas.
Muestra la frecuencia real.
No inventa valores ausentes.
Multimarca
Crea perfiles distintos por vehículo.
Descubre PIDs por coche.
No asume que todos ofrecen lo mismo.
Maneja varios protocolos OBD-II.
Análisis
Encuentra eventos marcados.
Compara sesiones.
Explica qué señales sustentan cada hallazgo.
Separa anomalías de diagnósticos.
IA
Cita internamente las evidencias.
Expresa incertidumbre.
No identifica piezas sin pruebas.
Reconoce cuando faltan datos.
No puede escribir en el vehículo.
Seguridad
La primera versión es de solo lectura.
No permite comandos CAN arbitrarios.
No borra DTC sin autorización y copia previa.
Registra todas las operaciones.
Protege el VIN y los datos del usuario.
Experiencia de uso

El flujo final debe ser:

Conectar OBDLink
      ↓
Abrir aplicación
      ↓
Seleccionar vehículo o detectarlo
      ↓
Elegir prueba
      ↓
Iniciar sesión
      ↓
Marcar síntoma
      ↓
Finalizar
      ↓
Ver análisis
      ↓
Preguntar a la IA
      ↓
Generar informe
Orden exacto que seguiría
Preparar Dell y repositorio.
Comprar OBDLink LX.
Validarlo con OBDwiz.
Leer tres PIDs desde Python.
Crear conexión robusta.
Descubrir PIDs automáticamente.
Grabar sesiones fiables.
Diseñar base de datos.
Crear API local.
Construir dashboard.
Añadir marcadores.
Implementar análisis matemático.
Crear reglas diagnósticas.
Añadir comparación entre sesiones.
Integrar IA.
Crear servidor MCP.
Validar con varios vehículos.
Generar informes.
Empaquetar para Windows.
Añadir plugins propietarios en una segunda etapa.