# Guía de uso e importación de vehículos con IA

Esta es la guía avanzada de **Mi Coche por Dentro**. Explica cómo utilizar las capturas con rigor y cómo ampliar la compatibilidad de un vehículo mediante Codex u otro agente capaz de inspeccionar, modificar y probar el repositorio.

## 1. Dos operaciones diferentes

### Añadir un vehículo al garaje

Se hace desde **Añadir vehículo** y no requiere programación. El coche obtiene cobertura OBD-II genérica y solo se muestran las señales que responden.

### Integrar compatibilidad avanzada

Significa investigar e implementar señales propietarias, referencias OEM y reglas específicas para una combinación concreta de vehículo, motor y ECU. Requiere código, documentación técnica, pruebas automatizadas y al menos una validación con el coche real.

Un perfil de `Volkswagen Passat B6` no es suficiente por sí solo: BKP/BMP con inyector-bomba y CBAB/CBBB common-rail pueden utilizar centralitas, bloques y magnitudes diferentes. La clave correcta suele ser:

```text
marca + modelo + generación + año + mercado + motor + código de motor + referencia/calibración de ECU
```

## 2. Información que debe reunir el usuario

No inventes los campos desconocidos. Es preferible indicar `DESCONOCIDO` y dejar que el agente prepare una fase segura de identificación.

### Identidad del vehículo

- Marca y modelo exactos.
- Generación o plataforma.
- Año y, si se conoce, mes de fabricación.
- Mercado: Europa, Estados Unidos, Latinoamérica u otro.
- Acabado o variante.
- Tipo de propulsión: gasolina, diésel, híbrido, PHEV o eléctrico.
- Cilindrada, potencia y tipo de inyección.
- Código de motor exacto.
- Norma de emisiones.
- Presencia de turbo, EGR, DPF/GPF, SCR/AdBlue y sensores relevantes.

### Identidad electrónica

- Marca/familia de ECU si se conoce.
- Número de pieza de ECU y versión de software o calibración.
- Protocolo detectado por la aplicación.
- Dirección de diagnóstico si aparece en una herramienta fiable.
- Adaptador utilizado, conexión USB/Bluetooth y versión de firmware.
- Captura del mensaje de conexión y del inventario de capacidades.

No es necesario compartir matrícula ni VIN completo. Si un documento incluye datos personales, anonimizarlos antes de adjuntarlo.

### Evidencia de funcionamiento

- Qué señales aparecen y cuáles quedan en `--`.
- Una sesión corta a ralentí con motor caliente.
- Si es seguro, una sesión controlada con variación de RPM y carga.
- Valores mostrados por una herramienta de referencia, indicando herramienta y unidad.
- Transcripción OBD anonimizada o respuestas crudas necesarias para decodificar.
- Síntomas reales, DTC y condiciones en las que ocurren.

## 3. Principios obligatorios de una integración correcta

1. **Solo lectura.** No se permiten codificación, adaptación, borrado, actuadores, rutinas ni escrituras de memoria.
2. **Nada inventado.** Un nombre parecido en Internet no demuestra que la ECU responda ese PID ni que utilice la misma escala.
3. **Separar procedencias.** Diferenciar dato medido por ECU, dato calculado, estimación, simulación y dato ausente.
4. **Verificar identidad antes de decodificar.** Una fórmula válida para otra variante puede producir cifras plausibles pero falsas.
5. **Conservar evidencia.** Cada señal propietaria debe poder relacionarse con una respuesta, una fórmula, una unidad y una fuente.
6. **Ocultar lo no disponible.** Si la ECU no ofrece una magnitud o no puede validarse, la tarjeta no debe aparecer como si estuviera pendiente eternamente.
7. **No usar simulación como respaldo de producción.** Los valores simulados solo pertenecen al modo de demostración y a pruebas.
8. **Validar comportamiento, no solo rango.** Una presión debe reaccionar coherentemente a la carga; una temperatura debe evolucionar con continuidad.
9. **Controlar carga del bus.** Más PIDs no siempre significan mejores datos. Hay que medir latencia, frecuencia y respuestas perdidas.
10. **Probar todo cambio.** Backend, interfaz, inicio, cierre, base vacía y paquete Windows.

## 4. Flujo recomendado con Codex

### Fase 1: abrir el proyecto y aportar el contexto

Abre en Codex la carpeta de la versión pública. Adjunta la información del vehículo, capturas y registros anonimizados. Pega el prompt maestro de la sección 7.

### Fase 2: auditoría sin conectar el coche

El agente debe inspeccionar la arquitectura existente, localizar los perfiles parecidos y presentar:

- cobertura estándar esperable;
- posibles protocolos propietarios;
- datos que faltan para identificar la variante;
- riesgos de confundir motores o ECUs;
- plan de implementación y validación.

La primera fase no debe asumir que todos los PIDs encontrados en una lista externa son compatibles.

### Fase 3: crear el vehículo básico

Añade el coche desde el Garaje. Introduce el código de motor si está confirmado. La aplicación asignará un UUID local; el código no debe depender de ese UUID ni precargar el coche en instalaciones ajenas.

### Fase 4: identificación y descubrimiento seguro

Con contacto puesto y el vehículo detenido:

1. Conecta el adaptador.
2. Guarda puerto, protocolo, latencia y tensión.
3. Ejecuta la identificación de fabricante si existe.
4. Conserva el número de pieza/calibración y los grupos que responden.
5. No continúes enviando peticiones si la ECU deja de responder o la tensión es inadecuada.

Si el agente necesita una nueva captura, debe indicar exactamente qué prueba hacer, cuánto debe durar, qué condiciones son seguras y qué archivo o captura devolver.

### Fase 5: implementar por capas

Orden recomendado:

1. Identidad del vehículo y resolución de ficha técnica.
2. PIDs OBD-II estándar realmente soportados.
3. Transporte de fabricante y direccionamiento de solo lectura.
4. Catálogo de señales propietarias con fórmulas y unidades.
5. Descubrimiento de capacidades por ECU.
6. Presentación dinámica: mostrar solo señales aplicables y verificadas.
7. Reglas diagnósticas y referencias específicas.
8. Pruebas, documentación y paquete de escritorio.

### Fase 6: validar con datos reales

Para cada señal se debe registrar:

| Campo | Ejemplo de resultado |
|---|---|
| Nombre canónico | `BOOST_ACTUAL` |
| Servicio/PID/grupo | Identificador exacto |
| Respuesta cruda | Bytes anonimizados |
| Fórmula | Conversión reproducible |
| Unidad | kPa absolutos |
| Procedencia | `measured_manufacturer` |
| Estado | verificada / pendiente / no soportada |
| Evidencia | captura, fuente y prueba |
| Rango observado | mínimo y máximo reales |
| Comportamiento | variación coherente con carga |

Una cifra plausible no basta. Conviene comparar con otra herramienta y repetir en más de una condición.

## 5. Casos especialmente delicados

### Consumo de combustible

Prioridad de fuentes:

1. Caudal de combustible ofrecido directamente por la ECU.
2. Cantidad de inyección por ciclo combinada con RPM y arquitectura confirmada del motor.
3. Cálculo mediante MAF y relación aire/combustible, claramente etiquetado y con limitaciones.

El consumo instantáneo en `L/100 km` no es estable a velocidad muy baja. El consumo medio del trayecto debe integrar combustible y distancia durante toda la sesión, excluir periodos inválidos y mostrar cobertura/calidad. Nunca se debe presentar un valor calculado como si lo hubiese enviado directamente la ECU.

### DPF y emisiones

Hollín calculado, hollín medido, masa de ceniza, presión diferencial, temperaturas EGT y distancia desde regeneración pueden estar en servicios propietarios diferentes. Algunas ECUs no los ofrecen. No mezclar `I/M Readiness` con carga real del DPF ni inferir una regeneración solo por una temperatura aislada.

### Turbo y EGR

Confirmar si las presiones son absolutas o relativas. Comparar valor solicitado y real solo cuando ambos proceden de grupos correctamente decodificados y sincronizados. En EGR, masa de aire objetivo/real no equivale necesariamente a apertura porcentual de válvula.

### Vehículos eléctricos

No aplicar PIDs de motor térmico. Muchos EV necesitan DoIP, CAN pasivo, un arnés específico o documentación DBC. Nunca sondear buses de seguridad ni enviar tramas de control sin un proyecto separado y revisado.

## 6. Cuándo considerar terminada la integración

- El coche se crea desde una base vacía sin datos precargados.
- La ficha se resuelve por identidad técnica, no por un ID personal.
- La conexión genérica sigue funcionando si falla la capa propietaria.
- Las señales verificadas muestran unidad, fuente y estado correctos.
- Las no soportadas se ocultan o se explican claramente.
- No aparecen datos simulados en producción.
- La aplicación detecta respuestas obsoletas sin declarar falsamente una desconexión.
- Los cálculos derivados incluyen sus condiciones de validez.
- Pasan las pruebas Python, la compilación de la interfaz y la prueba del ejecutable.
- Existe una tabla final de cobertura: recibida, calculada, pendiente y no disponible.

## 7. Prompt rápido para empezar

Si solo quieres empezar sin rellenar todos los campos, copia este bloque y cambia la línea `COCHE EXACTO`. Después adjunta capturas de la app, logs, sesiones OBD o documentación técnica que tengas.

```text
Quiero que integres y maximices de forma segura la compatibilidad de este coche en el proyecto local "Mi Coche por Dentro".

COCHE EXACTO:
[MARCA, MODELO, GENERACIÓN, AÑO, MOTOR, CÓDIGO DE MOTOR, MERCADO Y ECU SI SE CONOCE]

OBJETIVO:
Investiga la documentación técnica disponible, protocolos OBD-II/UDS/KWP2000/CAN aplicables, PIDs estándar, identificadores propietarios, bloques de medición, fórmulas, unidades y limitaciones de esta variante concreta. Quiero obtener la máxima cantidad de datos reales y útiles posible: motor, temperaturas, admisión, turbo, EGR, combustible, inyección, consumo instantáneo y medio, sistema eléctrico, emisiones, DPF/GPF/SCR, DTC, Freeze Frame, monitores y Modo 06 cuando existan.

REGLAS:
- Trabaja solo en lectura. No implementes escrituras, codificación, adaptación, borrado de errores, actuadores, rutinas ni flasheo.
- No inventes PIDs, fórmulas ni compatibilidad. Si algo no está probado para esta ECU, márcalo como pendiente o no soportado.
- Separa datos medidos por ECU, calculados, inferidos, simulados y ausentes.
- Muestra en la interfaz solo señales reales, verificadas o con una ruta clara de validación. Oculta lo no soportado.
- Protege privacidad: no uses VIN completo, matrícula, ubicación, claves ni datos personales.
- Antes de pedir pruebas con el coche real, dime exactamente qué captura hacer, cuánto debe durar, qué condiciones usar y cuándo abortar.

FORMA DE TRABAJO:
Primero audita el repositorio completo. Después crea una matriz de compatibilidad con señal, protocolo/fuente, PID/DID/bloque, fórmula, unidad, evidencia, estado y método de validación. Implementa por capas, añade pruebas y ejecuta la suite antes de terminar. Si falta evidencia real, prepara un protocolo de captura seguro en vez de suponer resultados.
```

Este prompt está pensado para usarse con un modelo de programación potente, con acceso al repositorio y capacidad de leer documentación técnica. Cuanto más exacto sea el coche, mejor: no es lo mismo `Passat B6 2.0 TDI` que `Volkswagen Passat B6 2.0 TDI BKP, inyector-bomba, Europa, ECU EDC16`.

## 8. Prompt maestro para integrar un vehículo con Codex

Copia el bloque completo, sustituye los campos entre corchetes y adjunta las capturas o archivos disponibles. Si un dato no se conoce, escribe `DESCONOCIDO`.

```text
Quiero que integres y maximices de forma segura la compatibilidad del siguiente vehículo en el proyecto local "Mi Coche por Dentro".

DATOS DEL PROYECTO
- Carpeta abierta en Codex: [RUTA DEL PROYECTO]
- Versión de la aplicación: [VERSIÓN]
- Sistema operativo: [WINDOWS 10/11]
- Esta es una copia pública: no debe contener mis coches, VIN, matrículas, claves, sesiones ni rutas personales.

IDENTIDAD DEL VEHÍCULO
- Marca: [MARCA]
- Modelo: [MODELO]
- Generación/plataforma: [GENERACIÓN]
- Año/mes de fabricación: [AÑO Y MES O DESCONOCIDO]
- Mercado: [EU/US/LATAM/OTRO]
- Variante/acabado: [VARIANTE]
- Tipo de propulsión: [GASOLINA/DIÉSEL/HÍBRIDO/PHEV/EV]
- Motor y cilindrada: [MOTOR]
- Código exacto de motor: [CÓDIGO O DESCONOCIDO]
- Potencia: [KW/CV]
- Tipo de inyección: [TIPO O DESCONOCIDO]
- Norma de emisiones: [NORMA O DESCONOCIDO]
- Turbo/EGR/DPF/GPF/SCR: [EQUIPAMIENTO CONFIRMADO O DESCONOCIDO]
- ECU/familia: [ECU O DESCONOCIDO]
- Referencia de ECU/calibración/software: [REFERENCIAS O DESCONOCIDO]

CONEXIÓN Y EVIDENCIA DISPONIBLE
- Adaptador y firmware: [MODELO/FIRMWARE]
- Tipo de conexión: [USB/BLUETOOTH]
- Puerto: [COM O DESCONOCIDO]
- Protocolo detectado: [PROTOCOLO O DESCONOCIDO]
- Herramienta de referencia utilizada: [HERRAMIENTA O NINGUNA]
- Datos que ya se reciben: [LISTA CON UNIDADES]
- Datos que faltan o quedan en "--": [LISTA]
- Síntomas/DTC: [DETALLE O NINGUNO]
- Capturas, sesiones, logs o transcripciones adjuntas: [LISTA DE ARCHIVOS]

OBJETIVO
Quiero obtener la máxima cobertura diagnóstica realista: identidad de ECU, RPM, velocidad, carga, temperaturas, admisión, MAF/MAP, turbo solicitado/real, EGR, combustible e inyección, consumo instantáneo y medio de trayecto, correcciones relevantes, sistema eléctrico, escape, DPF/GPF/SCR, monitores, DTC y Freeze Frame. Esta lista es un objetivo, no una autorización para inventar señales: implementa y muestra solo lo que esta variante ofrezca y pueda verificarse.

REGLAS DE SEGURIDAD OBLIGATORIAS
1. Trabaja exclusivamente en modo de solo lectura. No implementes ni ejecutes escritura de ECU, codificación, adaptación, borrado de DTC, actuadores, rutinas, desbloqueo de seguridad, flasheo ni comandos potencialmente destructivos.
2. No pruebes comandos sobre el coche hasta haber auditado el código y presentado la lista exacta de peticiones de solo lectura.
3. No inventes PIDs, DID, bloques, fórmulas, offsets, escalas, unidades, rangos OEM ni compatibilidad. Una fuente de otro motor o firmware no es evidencia suficiente.
4. Distingue siempre SAE/ISO OBD-II estándar de UDS, KWP2000, TP2.0 u otros protocolos propietarios. Verifica direccionamiento, sesión y variante de ECU.
5. Prioriza documentación primaria: manuales del fabricante, normas oficiales, documentación del proveedor de ECU/adaptador y fuentes técnicas reproducibles. Cita cada fuente y marca claramente cualquier inferencia.
6. Nunca uses valores simulados como fallback en producción. Nunca conviertas un timeout, cero artificial o ausencia de respuesta en un dato real.
7. Mantén estados separados: ofrecido por ECU, respuesta verificada, pendiente de mapear, no soportado, error temporal y dato obsoleto.
8. Oculta en la interfaz las tarjetas no aplicables o definitivamente no soportadas. Mantén visibles como pendientes solo las que tengan una vía concreta de identificación.
9. Protege la privacidad: no leas ni publiques VIN completo, matrícula, ubicación, claves, base de datos personal ni rutas del usuario.
10. Usa un MICOCHE_HOME temporal para pruebas y no modifiques los datos reales del usuario.

FORMA DE TRABAJO
A. Inspecciona primero todo el repositorio relevante: arquitectura, adaptadores, transportes, descubrimiento de capacidades, perfiles existentes, especificaciones, etiquetas, interfaz, informes y pruebas. No empieces creando archivos aislados sin entender el flujo completo.
B. Comprueba el estado actual ejecutando las pruebas y la compilación. Informa de cualquier fallo previo antes de atribuirlo al nuevo vehículo.
C. Investiga la identidad exacta del vehículo y explica qué datos faltan para distinguir variantes. Si falta un dato bloqueante, prepara una identificación segura o formula una pregunta concreta.
D. Crea una matriz de cobertura propuesta con estas columnas: señal, prioridad, fuente/protocolo, identificador, fórmula, unidad, aplicabilidad, evidencia, estado y método de validación.
E. Implementa por capas y reutiliza la arquitectura existente. No hardcodees el UUID de mi coche ni preinsertes vehículos en la base de datos pública.
F. Para señales propietarias, conserva evidencia bruta suficiente para depurar, pero anonimizada. Valida longitud, bytes de estado, valores no disponibles, signo, endianess, offset, factor y unidad.
G. Valida coherencia física y temporal: rangos, continuidad, reacción a carga/RPM, comparación objetivo-real y contraste con una herramienta fiable cuando exista.
H. Evalúa la carga del bus: latencia, frecuencia de muestreo, porcentaje de respuestas válidas, timeouts y agrupación de peticiones. Prioriza calidad sobre cantidad.
I. Para consumo, diferencia caudal medido y cálculo derivado. El consumo medio debe integrar combustible/distancia con criterios de validez y cobertura; no promedies directamente valores instantáneos inestables.
J. Para DPF/GPF/SCR, no confundas readiness con carga de hollín ni regeneración. Implementa cada magnitud solo si la ECU y la evidencia la sostienen.
K. Añade pruebas unitarias del decodificador, transporte, estados de capacidad, selección de tarjetas, cálculos derivados y resolución de ficha. Incluye respuestas normales, no disponibles, truncadas y erróneas.
L. Ejecuta al final la suite Python completa, npm build y, si el entorno lo permite, el empaquetado y smoke test de Windows.

CICLO CON EL COCHE REAL
Cuando necesites datos reales, detén el desarrollo y entrégame un protocolo de prueba breve y seguro que indique:
- contacto o motor encendido;
- motor frío/caliente;
- vehículo detenido o prueba en carretera;
- duración aproximada;
- acciones exactas y límites de RPM/carga;
- señales objetivo;
- archivo, captura o transcripción que debo devolverte;
- criterio para abortar por tensión, latencia o pérdida de respuestas.
No continúes suponiendo resultados mientras esperas esa evidencia.

ENTREGABLES FINALES
1. Resumen de la identidad confirmada y sus fuentes.
2. Cambios implementados, con archivos y motivo.
3. Tabla de cobertura final: medida, calculada, pendiente, no soportada y oculta.
4. Lista de fórmulas/unidades y evidencia de cada señal propietaria.
5. Resultados de pruebas, compilación y smoke test.
6. Limitaciones que siguen abiertas y siguiente captura concreta recomendada.
7. Confirmación expresa de que no se añadieron comandos de escritura ni datos personales.

Empieza ahora por la auditoría del repositorio y la matriz de compatibilidad. Haz cambios directos cuando estén respaldados por el código y la evidencia disponible; si el coche real es imprescindible, prepara el protocolo de captura y espera mis resultados.
```

## 9. Qué debe devolver el usuario después de cada prueba

Para que el agente pueda avanzar, responde con:

- captura del banner de conexión;
- captura de cada categoría de instrumentos;
- identificador de la sesión;
- duración y condiciones de la prueba;
- si el motor estaba frío o caliente;
- qué acciones se realizaron;
- mensajes de error exactos;
- herramienta de contraste y valores observados;
- archivo de telemetría o log solicitado, anonimizado.

Evita resumir un error como “no funciona”. El texto exacto, el momento y las condiciones permiten distinguir incompatibilidad, timeout, saturación del bus, fórmula incorrecta o una señal que la ECU simplemente no ofrece.

## 10. Resultado esperado

Una buena integración no es la que muestra más relojes, sino la que puede explicar de dónde sale cada valor, cuándo es válido y qué limitaciones tiene. El objetivo final es que una sesión con muchas señales coherentes permita analizar relaciones —por ejemplo, aire, turbo, EGR, inyección y consumo— sin confundir ausencia de datos con ausencia de avería.
