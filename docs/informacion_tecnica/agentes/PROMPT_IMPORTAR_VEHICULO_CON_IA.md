# Prompt maestro para importar un vehículo con IA

## Cómo usarlo

1. Abre la carpeta de **Mi Coche por Dentro** en Codex o en otro agente de programación con acceso al repositorio e Internet.
2. Copia el bloque completo de abajo.
3. Sustituye únicamente `MI VEHÍCULO` por la identificación más precisa que conozcas.
4. Adjunta capturas, sesiones o documentos si los tienes. No son obligatorios para comenzar.

Una entrada suficiente suele ser:

```text
MI VEHÍCULO: [marca, modelo, generación si se conoce, año, combustible, motor/cilindrada, potencia y mercado]
```

Ejemplo ficticio de formato: `Marca Modelo, generación X, 2018, diésel 2.0 de 110 kW, Europa`.

---

## Prompt

```text
Quiero que investigues e integres con el máximo rigor y de forma segura la compatibilidad de este coche en el proyecto local "Mi Coche por Dentro".

MI VEHÍCULO:
[ESCRIBE AQUÍ MARCA, MODELO, GENERACIÓN SI LA CONOCES, AÑO, COMBUSTIBLE, MOTOR/CILINDRADA, POTENCIA Y MERCADO]

INFORMACIÓN OPCIONAL QUE YA TENGO:
- Código de motor: [DESCONOCIDO O CÓDIGO]
- ECU, referencia o versión de software: [DESCONOCIDO O DATO]
- Norma/equipamiento de emisiones: [DESCONOCIDO O DATO]
- Adaptador y conexión: [DESCONOCIDO O MODELO]
- Datos que ya aparecen: [DESCONOCIDO O LISTA]
- Datos que faltan o quedan en "--": [DESCONOCIDO O LISTA]
- Capturas, sesiones, logs, manuales o PDF adjuntos: [NINGUNO O LISTA]

RESULTADO QUE BUSCO
Quiero la mayor cobertura REAL y ÚTIL que permita esta variante: identidad de ECU, motor, RPM, velocidad, carga, temperaturas, admisión, MAF/MAP, turbo solicitado/real, EGR, combustible, sistema de inyección, consumo instantáneo y medio del trayecto, sistema eléctrico, escape, DPF/GPF/SCR, DTC, Freeze Frame, readiness y Modo 06, además de otras señales que la documentación y la ECU justifiquen.

La lista anterior es un objetivo de investigación, no permiso para inventar datos ni mostrar relojes vacíos. Una señal solo debe incorporarse si es aplicable, está decodificada con rigor y tiene una ruta real de validación.

PRINCIPIO DE IDENTIFICACIÓN
No me obligues a rellenar una ficha técnica enorme. Empieza con la línea MI VEHÍCULO e investiga tú el resto. Debes distinguir con precisión:
- modelo, generación/plataforma, intervalo de fabricación y mercado;
- combustible, familia de motor, cilindrada, potencia y tecnología de propulsión/inyección;
- códigos de motor compatibles y cuál corresponde probablemente a mi unidad;
- turbo, EGR y sistemas DPF/GPF/SCR realmente instalados;
- familia, referencia y software/calibración de ECU;
- protocolo, dirección y sesión de diagnóstico aplicables.

Marca cada dato como CONFIRMADO, PROBABLE, AMBIGUO o DESCONOCIDO y enlaza su evidencia. Si hay varias variantes incompatibles, no elijas una por intuición: explica la diferencia y pídeme solamente el dato mínimo que permita resolverla. Si puede obtenerse con una lectura de identificación inocua, prepara esa lectura.

INVESTIGACIÓN WEB Y DOCUMENTAL OBLIGATORIA
Busca de forma activa documentación técnica específica del coche. Prioriza:
1. documentación oficial del fabricante: manuales de taller, boletines, documentación de diagnosis, diagramas y programas de autoestudio/formación;
2. normas SAE/ISO y documentación oficial del proveedor de ECU, adaptador o herramienta;
3. catálogos OEM, homologaciones y referencias que confirmen motor, potencia, emisiones y ECU;
4. fuentes técnicas reproducibles y proyectos que aporten peticiones, respuestas crudas, fórmulas y variante exacta;
5. foros o vídeos solo como pistas, nunca como única prueba de una fórmula.

Haz búsquedas combinando entre comillas modelo, plataforma, código de motor, referencia ECU y términos como workshop manual, service manual, self-study programme, diagnostic protocol, live data, measuring blocks, PID, DID, data identifier, KWP2000, UDS, CAN, injection, turbo, EGR, DPF/GPF, SCR y filetype:pdf. Busca también en el idioma habitual del fabricante cuando ayude.

LOCALIZACIÓN Y ANÁLISIS DE PDF
Para cada PDF o documento relevante:
- comprueba autor/editor, título, revisión, fecha, mercado, motorización y ECU a los que aplica;
- usa una fuente legítima; no eludas pagos, credenciales ni controles de acceso;
- descárgalo al espacio de trabajo temporal cuando sea legal y necesario para analizarlo;
- léelo completo o busca todas las menciones relevantes; si es un escaneo, aplica OCR y revisa visualmente tablas, diagramas, subíndices, signos y fórmulas;
- registra URL, título, versión, páginas exactas y la afirmación que respalda;
- compara tablas, unidades, endianess, factores y offsets con otra fuente o con respuestas reales;
- no añadas al repositorio PDF de pago, con copyright incompatible o con datos personales. Conserva únicamente referencias, enlaces, páginas citadas, notas propias y conocimiento derivado permitido;
- si un documento imprescindible solo está en un portal autorizado inaccesible, dime su título o referencia exacta y qué páginas/datos debo aportar legalmente.

No confundas documentación de una generación, código de motor, potencia, mercado o firmware cercano con evidencia de mi ECU. Úsala como candidata hasta validarla.

REGLAS DE SEGURIDAD INNEGOCIABLES
1. Todo el producto y todas las pruebas serán SOLO LECTURA.
2. No implementes ni ejecutes codificación, adaptación, borrado de DTC, pruebas de actuadores, rutinas, desbloqueo de seguridad, escritura de memoria, flasheo ni comandos de control.
3. Antes de utilizar el coche real, audita el código y enumera las peticiones exactas que se enviarían, justificando que son lecturas.
4. No inventes PID, DID, bloques, direcciones, fórmulas, bytes, endianess, signo, factor, offset, unidades, rangos ni compatibilidad.
5. Un nombre parecido en Internet o una cifra plausible no constituyen validación.
6. Distingue OBD-II/SAE estándar de protocolos propietarios como UDS, KWP2000, TP2.0 o CAN específico, y confirma el direccionamiento y la ECU.
7. Separa siempre: MEDIDO POR ECU, CALCULADO, INFERIDO, SIMULADO, OBSOLETO, ERROR TEMPORAL y AUSENTE/NO SOPORTADO.
8. Nunca conviertas ausencia de respuesta, timeout, byte de no disponible o cero artificial en una medición.
9. No uses simulación como fallback de producción.
10. Oculta tarjetas no aplicables o definitivamente no soportadas. Mantén una tarjeta pendiente solo si existe una prueba concreta para resolverla.
11. No leas ni publiques matrícula, VIN completo, ubicación, claves, bases personales ni rutas privadas. Usa datos y directorios temporales en las pruebas.
12. Detén el sondeo si hay tensión inadecuada, latencia extrema, errores repetidos o la ECU deja de responder.

FASE 1 — AUDITORÍA DEL PROYECTO
Antes de modificar nada:
- lee README.md, docs/IMPORTAR_VEHICULO.md, esta carpeta técnica, la especificación y las decisiones de arquitectura relevantes;
- localiza resolución de fichas, perfiles existentes, transporte ELM/STN, descubrimiento, captura, catálogo de señales, capacidades, interfaz, informes y pruebas;
- busca una integración existente técnicamente cercana, pero no copies identificadores sin demostrar aplicabilidad;
- ejecuta las pruebas y el build actuales; separa fallos previos de los introducidos;
- protege la copia pública: no precargues coches, sesiones, VIN, matrículas, secretos o rutas personales.

FASE 2 — EXPEDIENTE DE IDENTIDAD Y FUENTES
Entrégame primero una tabla con:
- dato de identidad;
- valor encontrado;
- estado: confirmado/probable/ambiguo/desconocido;
- fuente y páginas;
- variantes descartadas y motivo;
- dato mínimo aún necesario.

Incluye una bibliografía técnica concisa. Para cada fuente indica si es primaria, secundaria o solo una pista. No avances con señales propietarias si la identidad sigue permitiendo ECUs con decodificaciones incompatibles.

FASE 3 — MATRIZ DE COMPATIBILIDAD
Antes de programar, crea una matriz por señal con:
- nombre canónico y utilidad diagnóstica;
- prioridad;
- estándar o propietaria;
- ECU/familia/software aplicable;
- protocolo, dirección, servicio y PID/DID/grupo;
- formato de petición y respuesta esperada;
- longitud, bytes de estado, endianess, signo, factor, offset y fórmula;
- unidad canónica y rango físico razonable;
- fuente, documento y páginas;
- estado de evidencia: VERIFICADA, CANDIDATA, PENDIENTE DE MAPEAR, NO SOPORTADA u OCULTA;
- prueba necesaria para validarla.

No es necesario implementar todas las candidatas a la vez. Prioriza señales fiables que, combinadas, mejoren el diagnóstico sin saturar el bus.

FASE 4 — IMPLEMENTACIÓN POR CAPAS
1. Añade o mejora la resolución de identidad sin depender del UUID local del coche.
2. Conserva la cobertura OBD-II genérica y verifica lo que la ECU realmente soporta.
3. Implementa el transporte/direccionamiento del fabricante solo cuando esté documentado.
4. Añade un catálogo trazable de señales propietarias y decodificadores puros.
5. Descubre capacidades por ECU real: documentado no significa respondido.
6. Presenta dinámicamente solo señales aplicables y disponibles.
7. Integra las señales en captura, análisis e informe con su procedencia y calidad.
8. Añade cálculos derivados únicamente con entradas válidas y método visible.
9. No rompas otros vehículos, el simulador, una base vacía ni el funcionamiento sin IA.

VALIDACIÓN TÉCNICA
Para cada decodificador prueba respuestas normales, límites, no disponible, truncadas, negativas cuando proceda, ECU equivocada y errores. Verifica:
- coherencia física y temporal;
- reacción esperada a RPM, carga, temperatura o deceleración;
- comparación solicitado/real cuando ambas señales estén sincronizadas;
- contraste con una herramienta fiable si está disponible;
- latencia, frecuencia, tasa de respuestas válidas y carga total del bus.

Una señal no pasa a VERIFICADA porque caiga dentro de un rango: su origen, fórmula y comportamiento también deben concordar.

REGLAS ESPECÍFICAS DE CÁLCULO
- Consumo: prioriza caudal medido. Si es derivado, documenta entradas y arquitectura. Integra combustible y distancia para el consumo medio; no promedies L/100 km instantáneos y excluye muestras inválidas o velocidad demasiado baja.
- Turbo: confirma presión absoluta/relativa y no mezcles objetivo y real de instantes distintos.
- EGR: no conviertas automáticamente masa de aire objetivo/real en porcentaje de apertura.
- DPF/GPF/SCR: no confundas readiness con hollín, ceniza o regeneración. Cada magnitud necesita evidencia propia.
- Híbridos/EV: no apliques PIDs de combustión; identifica cada ECU y evita buses de seguridad.

CICLO CON EL COCHE REAL
Cuando necesites evidencia real, pausa el desarrollo y dame un protocolo breve que especifique:
- propósito y señales que se quieren confirmar;
- contacto o motor encendido, frío/caliente y detenido/en marcha;
- duración y acciones exactas;
- límites prudentes de RPM/carga;
- peticiones de solo lectura que realizará la aplicación;
- capturas, identificador de sesión y archivos anonimizados que debo devolver;
- criterios de aborto por tensión, latencia o pérdida de respuestas.

Empieza siempre con el vehículo detenido. Si fuera imprescindible circular, exige un acompañante que opere el ordenador; el conductor no debe mirar ni manipular la aplicación.

PRUEBAS Y TERMINACIÓN
- añade pruebas unitarias y de integración de identidad, transporte, decodificación, capacidades, interfaz dinámica, cálculos e informes;
- ejecuta la suite Python completa y el build del dashboard;
- si el entorno lo permite, genera el paquete Windows y ejecuta su smoke test;
- revisa que una instalación nueva arranque sin datos personales y permita crear este coche desde cero;
- confirma que la conexión genérica sigue disponible si falla la capa propietaria.

ENTREGABLES FINALES
1. Identidad técnica confirmada, ambigüedades y fuentes enlazadas.
2. Bibliografía/PDF consultados con versión y páginas relevantes.
3. Archivos modificados y motivo de cada cambio.
4. Tabla final: medida por ECU, calculada, pendiente, no soportada y oculta.
5. Fórmulas, unidades, aplicabilidad y evidencia de cada señal propietaria.
6. Resultados de pruebas, build y smoke test.
7. Limitaciones abiertas y siguiente prueba real recomendada.
8. Confirmación expresa de que no se añadieron escrituras ni datos personales.

FORMA DE COLABORAR
Trabaja con autonomía: investiga, audita, implementa y prueba todo lo que pueda demostrarse sin el coche. No me hagas preguntas generales que puedas resolver con el repositorio o las fuentes. Pregunta solo cuando falte un dato que cambie materialmente la variante o cuando necesites una captura real. No declares la integración completa mientras queden señales sin validar en el vehículo.

Empieza ahora por la auditoría, el expediente de identidad y la búsqueda documental. Después presenta la matriz de compatibilidad y continúa con los cambios respaldados por evidencia.
```

## Qué esperar

La primera respuesta útil del agente no debería ser una lista de PIDs copiada de Internet, sino:

- la identidad técnica más probable y las alternativas;
- las fuentes y PDF encontrados;
- lo que ya soporta el proyecto;
- una matriz inicial de señales;
- qué puede implementar inmediatamente;
- una única pregunta o prueba concreta si falta un dato bloqueante.

La integración será progresiva: investigar e implementar sin el coche, capturar evidencia real, corregir fórmulas o compatibilidad y repetir hasta que la tabla final sea honesta y estable.
