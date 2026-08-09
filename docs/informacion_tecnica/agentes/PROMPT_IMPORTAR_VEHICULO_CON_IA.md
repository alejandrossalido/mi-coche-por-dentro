# Prompt maestro para integrar un vehículo con IA

## Uso

1. Abre la carpeta de **Mi Coche por Dentro** en un agente de programación potente con acceso al repositorio, Internet, terminal y lectura de PDF.
2. Copia el bloque completo.
3. Cambia únicamente `MI VEHÍCULO`. Los demás datos son opcionales.
4. Adjunta capturas, sesiones o documentación si ya las tienes.

Una identificación inicial suficiente suele ser:

```text
MI VEHÍCULO: marca, modelo/generación, año, combustible, motor/cilindrada, potencia y mercado
```

No compartas matrícula ni VIN completo. Si el agente necesita distinguir dos variantes, debe pedir únicamente el dato mínimo necesario.

---

## Prompt para copiar

```text
Actúa como responsable técnico de compatibilidad OBD y completa, con la máxima autonomía y rigor, la integración del siguiente vehículo en el proyecto local "Mi Coche por Dentro".

MI VEHÍCULO:
[MARCA, MODELO Y GENERACIÓN SI SE CONOCE, AÑO, COMBUSTIBLE, MOTOR/CILINDRADA, POTENCIA Y MERCADO]

DATOS OPCIONALES QUE YA CONOZCO:
- Código de motor: [DESCONOCIDO O DATO]
- Cambio y tracción: [DESCONOCIDO O DATO]
- ECU, referencia o software: [DESCONOCIDO O DATO]
- Norma y sistemas de emisiones: [DESCONOCIDO O DATO]
- Adaptador y tipo de conexión: [DESCONOCIDO O DATO]
- Modificaciones, reprogramaciones o componentes sustituidos: [NINGUNO/DESCONOCIDO O DETALLE]
- Señales que aparecen y señales que quedan en "--": [DESCONOCIDO O LISTA]
- Síntomas o métricas prioritarias: [NINGUNO O DETALLE]
- Capturas, sesiones, logs, manuales o PDF adjuntos: [NINGUNO O LISTA]

OBJETIVO FINAL
Deja el proyecto tan completo, seguro y probado como permitan el repositorio, la documentación legítimamente accesible y la evidencia disponible. Busca la máxima cobertura REAL y ÚTIL de esta variante: identidad, motor, temperaturas, admisión, MAF/MAP, turbo, EGR, combustible, inyección, consumo, sistema eléctrico, escape, emisiones, DPF/GPF/SCR, DTC, Freeze Frame, readiness, Modo 06 y cualquier otra señal que la mecánica y la ECU justifiquen.

La lista anterior es solo el mínimo. Investiga de forma exhaustiva TODAS las métricas que la variante, sus ECUs y el hardware puedan ofrecer, aunque el usuario no las haya mencionado y aunque su utilidad parezca secundaria. No selecciones únicamente las métricas “interesantes”: cualquier señal documentada o razonablemente candidata debe entrar en el catálogo técnico con identificador, origen y estado. Intenta implementar y verificar cada una. Si no puedes obtenerla, no la elimines silenciosamente: clasifícala como pendiente, sin decodificar, condicional, no disponible, no aplicable o inaccesible con este hardware. El inventario puede mostrarla vacía con ese estado; el cuadro de instrumentos nunca debe presentarla como una medición real sin evidencia.

El hardware de referencia del proyecto es el Vgate vLinker FS USB. Determina primero todas las redes y protocolos que esta unidad puede alcanzar en el vehículo concreto. Después busca todas las métricas accesibles por OBD-II estándar y por diagnosis de fabricante con ese hardware: Mode 01 completo, Freeze Frame/Mode 02, DTC presentes/pendientes/permanentes, readiness, Mode 06, identidad estrictamente necesaria y todos los bloques, PID, DID, local identifiers y campos propietarios de cada ECU segura y legible. El catálogo base ya enumera todos los comandos Mode 01 decodificables por la versión incluida de python-OBD; amplíalo si la norma aplicable, el fabricante o la ECU documentan más. No hagas fuerza bruta ni envíes servicios de escritura.

MODO DE EJECUCIÓN AUTÓNOMA
- No termines después de proponer un plan, listar fuentes o crear una matriz. Continúa en esta misma tarea con la investigación, los cambios, las pruebas, el build y el informe final siempre que puedas hacerlo sin el coche.
- No me preguntes por información que puedas obtener del repositorio, documentación pública, archivos adjuntos o una identificación segura ya implementable.
- Haz directamente los cambios locales respaldados por evidencia. Conserva los cambios existentes del usuario y no modifiques datos privados.
- Si falta un dato de identidad, avanza con la capa genérica y prepara un resolver seguro; pregunta solo si elegir una variante concreta cambiaría identificadores, fórmulas o transporte.
- Solo detente cuando sea imprescindible una respuesta del coche, una fuente autorizada que yo deba aportar o una decisión que cambie materialmente el alcance. En ese caso deja el código y las pruebas preparados y pide una única prueba o dato concreto.
- No declares integración completa mientras quede pendiente la validación que únicamente puede realizar el vehículo real.

REGLAS INNEGOCIABLES DE SEGURIDAD Y PRIVACIDAD
1. Todo será SOLO LECTURA.
2. No implementes ni ejecutes escritura de memoria, codificación, adaptación, borrado de DTC, actuadores, rutinas, regeneraciones, desbloqueo de seguridad, flasheo ni control del vehículo.
3. No pruebes servicios, subfunciones o direcciones desconocidas por fuerza bruta. Cada petición propietaria debe estar en una lista permitida y tener justificación de lectura.
4. No eludas pasarelas de seguridad, pagos, credenciales, cifrado ni controles de acceso.
5. No inventes PID, DID, bloques, direcciones, encabezados, fórmulas, bytes, endianess, signo, factor, offset, unidades, rangos o compatibilidad.
6. Un dato publicado para un coche parecido es una pista, no evidencia aplicable a esta ECU.
7. No uses simulación, un cero artificial, el último valor conocido o un timeout como sustituto de una medición real.
8. No leas, guardes ni publiques matrícula, VIN completo, ubicación, claves, inmovilizador, base personal o rutas privadas. Anonimiza capturas y respuestas.
9. Usa un MICOCHE_HOME temporal para pruebas. No añadas coches personales ni dependas de su UUID.
10. Detén cualquier inventario real ante tensión inadecuada, errores repetidos, latencia extrema o pérdida sostenida de respuestas, y restaura siempre el adaptador a un estado conocido.

FASE 1 — AUDITA EL PROYECTO ANTES DE CAMBIARLO
Lee README.md, docs/IMPORTAR_VEHICULO.md, docs/informacion_tecnica/README.md, la especificación, las ADR y los perfiles de compatibilidad existentes. Inspecciona como mínimo:
- modelo de datos y creación de vehículos;
- resolución de ficha e identidad;
- adaptadores, transporte ELM/STN y máquina de conexión;
- OBD genérico, transportes de fabricante y descubrimiento;
- catálogos, decodificadores y estados de capacidad;
- planificador de captura, persistencia y respuestas brutas;
- interfaz dinámica, traducciones, análisis e informes;
- pruebas, empaquetado Windows y smoke test.

Ejecuta primero la suite y el build actuales. Registra los fallos previos por separado. Reutiliza la arquitectura existente y las lecciones de integraciones reales, pero no copies identificadores o fórmulas de otra variante sin demostrar aplicabilidad.

FASE 2 — RESUELVE LA IDENTIDAD TÉCNICA
Empieza con MI VEHÍCULO; no me obligues a completar una ficha enorme. Investiga y construye internamente:
- denominación exacta, generación/plataforma, intervalo de fabricación y mercado;
- combustible o sistema de propulsión, cilindrada, potencia y tecnología de inyección;
- códigos de motor posibles y el correspondiente a esta variante;
- cambio y tracción solo cuando afecten a ECU, red o señales;
- turbo y sistemas EGR, DPF/GPF, SCR/AdBlue realmente instalados;
- familia, hardware, referencia y software/calibración de la ECU;
- protocolo, gateway, dirección, sesión y red física accesible;
- modificaciones o sustituciones que invaliden la configuración de fábrica;
- adaptador y capacidades físicas necesarias.

Separa siempre:
- DECLARADO POR EL USUARIO;
- DEDUCIDO DE DOCUMENTACIÓN;
- IDENTIFICADO POR LA ECU.

Marca cada dato como CONFIRMADO, PROBABLE, AMBIGUO o DESCONOCIDO, con fuente. La identidad leída de la ECU prevalece sobre una suposición por año o nombre comercial. Si siguen siendo posibles dos ECUs incompatibles, no elijas una silenciosamente: implementa la identificación y pide solo el código, foto anonimizada o lectura que las diferencie.

No solicites VIN completo por defecto. Si unos pocos caracteres son imprescindibles para distinguir variante o planta, explica por qué, usa solo esos caracteres y no los incorpores al repositorio.

FASE 3 — INVESTIGACIÓN TÉCNICA Y PDF
Busca activamente documentación específica de la variante, motor y ECU. Prioridad:
1. documentación oficial: manuales de taller, boletines, diagramas, formación y documentación de diagnosis del fabricante;
2. normas SAE/ISO y documentación oficial del proveedor de ECU, adaptador o herramienta;
3. ODX/PDX, DBC, catálogos de bloques o archivos de diagnosis disponibles legalmente;
4. homologaciones, catálogos OEM y referencias que confirmen motor, emisiones o ECU;
5. implementaciones abiertas reproducibles con peticiones, respuestas crudas y fórmulas;
6. foros, capturas o vídeos únicamente como pistas que deben contrastarse.

Busca combinando modelo, plataforma, código de motor, referencia ECU y términos como workshop manual, service manual, self-study programme, diagnostic protocol, measuring blocks, live data, PID, DID, local identifier, ODX, PDX, KWP2000, UDS, ISO-TP, CAN, DoIP, injection, turbo, EGR, DPF/GPF, SCR y filetype:pdf. Busca también en el idioma habitual del fabricante.

Para cada documento relevante:
- verifica autor/editor, título, versión, fecha, mercado, motor, ECU y firmware aplicables;
- usa únicamente una fuente legítima;
- léelo completo o busca sistemáticamente las secciones relevantes;
- aplica OCR si es un escaneo y revisa visualmente tablas, diagramas, signos y fórmulas;
- registra URL, título, revisión, páginas y la afirmación exacta que respalda;
- contrasta identificadores, longitudes, unidades y escalas con otra fuente o una respuesta real;
- no subas al repositorio PDF de pago, con copyright incompatible o datos personales: conserva enlaces, citas breves, páginas y notas propias;
- si está en un portal autorizado inaccesible, indica el título/referencia exactos y qué páginas o exportación debo aportar legalmente.

Entrega una bibliografía concisa y califica cada fuente como PRIMARIA, SECUNDARIA o PISTA.

FASE 4 — COMPRUEBA PROTOCOLO, RED Y ADAPTADOR
Antes de prometer señales propietarias determina:
- OBD-II/EOBD genérico disponible;
- K-Line/ISO 9141/ISO 14230, CAN, ISO-TP, KWP2000, TP2.0, UDS, DoIP, CAN FD u otro transporte aplicable;
- dirección física/funcional, CAN de 11/29 bits, velocidad y temporización;
- sesión de lectura necesaria, mantenimiento de sesión y cierre limpio;
- gateway, redes secundarias o pasarela segura;
- capacidades reales del adaptador: red física, cambio de bus, K-Line, CAN FD, DoIP o J2534.

Si el adaptador no puede acceder físicamente a la red, clasifica esas señales como INACCESIBLES CON ESTE HARDWARE. No intentes recuperarlas mediante comandos improvisados. Mantén OBD genérico operativo si falla la capa propietaria.

FASE 5 — CREA EL CATÁLOGO Y EL CONTRATO DE EVIDENCIA
Crea primero el inventario exhaustivo y después decide qué puede medirse. Recorre sistemáticamente todos los PIDs estándar aplicables, todos los bloques/DID/local identifiers documentados para cada ECU accesible y todos los campos de sus respuestas. No cierres el catálogo al alcanzar una cobertura “suficiente” y no descartes una métrica solo porque no se use aún en una regla diagnóstica.

Crea como artefacto de trabajo una matriz por señal con:
- nombre canónico estable y etiqueta comprensible;
- sistema, utilidad diagnóstica y prioridad;
- ECU de origen y variantes aplicables;
- protocolo, dirección, servicio y PID/DID/bloque/posición;
- petición y estructura de respuesta esperada;
- longitud, bytes de estado/no disponible, endianess, signo, factor, offset y fórmula;
- unidad canónica y rango físico;
- frecuencia razonable y condición necesaria;
- fuente, documento, páginas y nivel de confianza;
- procedencia: MEDIDA POR ECU, CALCULADA o INFERIDA;
- prueba de validación.

Usa estados separados y persistentes:
- DOCUMENTADA/POTENCIAL: aparece en una fuente aplicable, aún no consultada;
- RESPONDIDA_SIN_DECODIFICAR: existen bytes reales pero no una fórmula demostrada;
- VERIFICADA_ESTÁTICA: respuesta, tipo, fórmula y valor son coherentes detenido;
- VERIFICADA_DINÁMICA: además cambia correctamente durante una sesión adecuada;
- CONDICIONAL: requiere motor, temperatura, carga, regeneración u otro estado concreto;
- NO_DISPONIBLE: rechazo, marcador vacío, campo ausente o sensor no equipado;
- NO_APLICABLE: no tiene sentido en esta mecánica;
- INACCESIBLE_HARDWARE: la red no es alcanzable con el adaptador;
- ERROR_TEMPORAL: timeout o fallo recuperable;
- OBSOLETA: hubo lectura, pero ya no es reciente;
- OCULTA: no debe mostrarse al usuario.

Documentado no significa respondido; respondido no significa decodificado; plausible no significa verificado. Conserva campos auxiliares desconocidos como bytes sin asignarles un nombre inventado.

FASE 6 — IMPLEMENTA EL FLUJO COMPLETO
No implementes únicamente un perfil o una lista de relojes. Integra por capas:
1. resolución de identidad independiente del UUID local;
2. OBD-II genérico realmente soportado;
3. transporte de fabricante con lista blanca de lecturas y limpieza garantizada;
4. catálogo y decodificadores puros con trazabilidad;
5. inventario real de capacidades por ECU/referencia/software;
6. planificador multicanal eficiente;
7. persistencia de mediciones, respuestas desconocidas e intentos fallidos;
8. interfaz basada en capacidad real;
9. captura, análisis, informes y contexto de IA;
10. pruebas, documentación, build y paquete Windows.

En el planificador:
- agrupa señales de un mismo bloque y decodifica todos sus campos desde una sola respuesta;
- asigna mayor frecuencia a RPM, carga, pedal, aire y presión; media a inyección/turbo/EGR; baja a temperaturas, estados y emisiones;
- consulta identidad una vez y DTC al principio/final, no continuamente;
- alterna grupos, limita reintentos y evita que una señal problemática bloquee las demás;
- registra frecuencia real, latencia, último dato válido, respuestas correctas y motivo de fallo;
- prioriza calidad y estabilidad sobre cantidad de PIDs.

Trata correctamente las particularidades de transporte: respuestas de longitud diferente, bloques extendidos, campos extra desconocidos, tramas idénticas duplicadas, respuestas negativas y marcadores vacíos. Solo añade tolerancias cuando exista evidencia y nunca cuentes una trama duplicada como dos mediciones.

Al cambiar entre transporte propietario y OBD genérico, o al abortar/cerrar, restaura el adaptador de forma fiable. Una señal lenta o temporalmente ausente no debe provocar por sí sola un falso aviso de ECU desconectada: separa estado global de conexión, frescura por señal y silencio real del bus.

PERSISTENCIA Y AUSENCIAS
Guarda, cuando la arquitectura lo permita y sin datos personales:
- vehículo/ficha técnica, ECU y versión;
- sesión, UTC y tiempo monotónico;
- identificador, valor, unidad y procedencia;
- respuesta bruta anonimizada o referencia a la evidencia;
- decodificador/catálogo utilizado;
- calidad, latencia y condición de funcionamiento;
- intento sin valor y causa exacta.

Distingue al menos: no solicitada, timeout, respuesta negativa, marcador vacío, campo ausente, tipo desconocido, descartada por incoherencia, condición no activa y no aplicable. La interfaz puede ocultar lo no soportado, pero la evidencia técnica útil no debe perderse.

INTERFAZ, INFORME E IA
- Genera las tarjetas desde capacidades reales; no diseñes primero una pantalla fija y fuerces después los datos.
- Mantén dos niveles distintos: el cuadro de instrumentos muestra mediciones verificadas o una identificación claramente explicada; el inventario técnico muestra TODAS las métricas catalogadas, incluidas pendientes, condicionales, no disponibles, no aplicables e inaccesibles.
- Registra cada familia nueva mediante un proveedor del catálogo general (`collector/metric_catalog.py`) para que ninguna candidata dependa de que el agente recuerde crear una tarjeta manual.
- Cada métrica catalogada debe generar automáticamente su reloj/tarjeta, incluso sin valor. Conserva los filtros `Solo con datos`, `Todas las métricas`, `Sin datos visibles` y `Vista de diagnóstico`; no vuelvas a una lista fija que omita candidatos.
- Diferencia disponible, sin lectura reciente, condicional, pendiente de decodificar, no ofrecida, no aplicable y error de comunicación.
- Mantén todas las traducciones de español, inglés, italiano y alemán.
- El informe debe ser comprensible para no mecánicos y separar hechos, cálculos, hipótesis, calidad y limitaciones.
- El análisis recibe identidad exacta, condiciones, señales capturadas, ausencias con motivo, estadísticas, incidencias y evidencia; nunca interpreta ausencia como cero.
- La aplicación y el informe determinista deben seguir funcionando sin API de IA.

REGLAS FÍSICAS Y CÁLCULOS DELICADOS
- No muestres presión de rail en motores sin common rail, fuel trims de gasolina como requisito de un diésel ni SCR/AdBlue en variantes que no lo equipan.
- Consumo: prioriza caudal medido. Si se deriva, documenta entradas, arquitectura y cobertura. El consumo medio integra combustible y distancia; no promedia L/100 km instantáneos y excluye velocidad/muestras inválidas.
- Turbo: confirma absoluta frente a relativa y sincroniza solicitado/real.
- EGR: masa de aire objetivo/real no equivale automáticamente a porcentaje de apertura.
- DPF/GPF/SCR: readiness no representa hollín, ceniza o regeneración. Un bloque documentado que devuelve vacío queda NO_DISPONIBLE, no cero.
- Híbridos/EV: identifica las ECUs y estados de propulsión; no reutilices PIDs térmicos ni sondees buses de seguridad.
- Un valor constante puede ser real, condicional, no disponible o estar mal decodificado; no lo aceptes solo por su rango.

FASE 7 — VALIDA ANTES DE ENTREGAR
Añade pruebas para:
- números con y sin signo, endianess, factores, offsets y unidades;
- marcadores no disponibles, respuestas negativas, truncadas, extendidas y con campos adicionales;
- timeouts, duplicados, reconexión, aborto y restauración del adaptador;
- ECU/firmware equivocados y resolución de variantes;
- estados de capacidad, ocultación y frescura;
- planificador, agrupación y carga del bus;
- persistencia de respuestas e intentos fallidos;
- consumo y demás cálculos derivados;
- informes con datos parciales y funcionamiento sin IA;
- base vacía, otros vehículos, simulador, traducciones y paquete de escritorio.

Valida cada señal no solo por rango, sino por comportamiento: RPM al acelerar, velocidad cero detenido, temperatura continua, pedal al pisarlo, turbo con carga, tensión con motor parado/arrancado y coherencia entre señales relacionadas. Contrasta con una herramienta fiable cuando exista.

Ejecuta al final la suite Python completa, comprobación de traducciones, build del dashboard, empaquetado Windows y smoke test cuando el entorno lo permita. No ocultes fallos o avisos previos.

FASE 8 — PRIMERA CONEXIÓN REAL
Si el coche está disponible, la primera operación debe ser identificación e inventario, no una prueba en carretera:
1. detectar adaptador, firmware y capacidades;
2. comprobar tensión y contacto;
3. detectar OBD y PIDs estándar;
4. leer identidad estrictamente necesaria de ECU, hardware, software y calibración;
5. comparar con la ficha seleccionada y detenerse si no coincide;
6. activar el catálogo correcto;
7. consultar únicamente identificadores de lectura documentados;
8. conservar respuestas válidas, desconocidas, vacías y rechazadas;
9. clasificar cada señal y mostrar cobertura real;
10. restaurar el adaptador antes de iniciar la captura normal.

Si necesito hacer yo la prueba, entrégame un único protocolo breve que indique:
- objetivo y señales;
- contacto/motor, frío/caliente y detenido/en marcha;
- duración, acciones y límites prudentes de RPM/carga;
- lista exacta de peticiones de solo lectura;
- criterio de aborto por tensión, latencia o pérdidas;
- identificador de sesión, capturas y archivos anonimizados que debo devolverte.

Empieza siempre detenido. Si es imprescindible circular, exige un acompañante que opere el ordenador; el conductor no debe mirar ni manipular la aplicación.

CRITERIO DE TERMINACIÓN
La integración solo puede considerarse completa cuando:
- la identidad técnica y las ambigüedades están documentadas;
- una base vacía permite crear el coche sin datos precargados;
- OBD genérico sigue funcionando si falla la capa propietaria;
- cada señal visible tiene ECU, identificador, fórmula, unidad, estado y evidencia;
- cada señal catalogada aparece en el cuadro dinámico y puede localizarse tanto con datos como sin ellos;
- las no aplicables/no soportadas se excluyen de los relojes en directo, pero permanecen visibles y explicadas en el inventario completo; las desconocidas conservan evidencia;
- el planificador mantiene una captura estable y reporta cobertura real;
- cálculos, informe e IA distinguen procedencia y limitaciones;
- pasan pruebas, build y smoke test;
- no se añadieron escrituras, datos personales ni dependencias de mi coche local;
- las señales que requieren coche real están validadas o declaradas honestamente PENDIENTES.

ENTREGABLES FINALES
1. Identidad resuelta, variantes descartadas y dato pendiente mínimo.
2. Fuentes/PDF con versión, URL y páginas relevantes.
3. Matriz de cobertura final con estados y causa de cada ausencia.
4. Cambios implementados, archivos y motivo.
5. Peticiones de lectura, fórmulas, unidades y evidencia propietaria.
6. Resumen de cobertura: catalogadas, consultadas, respondidas, decodificadas, guardadas, condicionales, no disponibles, no aplicables y pendientes.
7. Resultados de pruebas, traducciones, build y smoke test.
8. Limitaciones reales y, solo si hace falta, la siguiente prueba exacta.
9. Confirmación expresa de que no se añadieron comandos de escritura ni datos personales.

Empieza ahora. Audita e investiga, crea la matriz como herramienta interna y continúa inmediatamente con la implementación y las pruebas. No cierres la tarea con una propuesta de trabajo si puedes ejecutar ese trabajo en el repositorio. Si la ECU real es el único bloqueo, deja todo preparado para que una sola captura dirigida permita terminar la validación.
```

## Resultado esperable

El agente debería completar en una sola tarea todo lo que no dependa físicamente del coche. Si necesita una prueba real, la primera respuesta seguirá dejando una integración ejecutable, pruebas automatizadas y una única captura claramente definida.

La respuesta del coche continúa siendo imprescindible para confirmar señales propietarias. El prompt reduce iteraciones evitables; no convierte documentación potencial en compatibilidad demostrada.
