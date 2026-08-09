# Guía para añadir e integrar un vehículo con IA

Esta guía permite ampliar **Mi Coche por Dentro** para un coche nuevo con ayuda de Codex u otro agente de programación con acceso al repositorio, Internet y documentos técnicos.

> **Resultado realista:** el agente debe investigar y catalogar todas las métricas posibles, pero ningún prompt garantiza que la ECU permita leerlas todas. Los parámetros propietarios dependen del motor, la ECU y su software; cada candidata conserva su estado y la integración solo queda confirmada después de probarla con el vehículo real.

## 1. Dos niveles de incorporación

### Añadirlo al garaje

Se hace desde **Añadir vehículo**. No requiere programar y permite utilizar los PIDs OBD-II/EOBD genéricos que el coche anuncie y responda.

### Crear compatibilidad avanzada

Añade identificación específica, transporte del fabricante, señales propietarias, fórmulas, unidades, presentación dinámica y reglas diagnósticas para una variante concreta. Requiere investigación, código, pruebas automáticas y una validación segura con el coche real.

## 2. Lo único que debe escribir el usuario

En la mayoría de los casos basta con una línea bien formulada:

```text
Volkswagen Golf VII, 2016, 2.0 TDI 150 CV, diésel, mercado europeo
```

Los datos mínimos recomendados son:

| Dato | Por qué ayuda |
|---|---|
| Marca, modelo y generación | Evita mezclar plataformas con el mismo nombre comercial |
| Año aproximado | Acota restylings, normativa y familia electrónica |
| Combustible, motor/cilindrada y potencia | Suele distinguir variantes mecánicas y ECUs |
| Mercado, si se conoce | Un mismo modelo puede cambiar entre Europa, EE. UU. u otros mercados |

No hace falta conocer de antemano código de motor, tipo de inyección, ECU, protocolo, norma de emisiones o equipamiento anticontaminación. El agente debe investigarlos. Si descubre dos variantes todavía posibles, pedirá **solo el dato que realmente las diferencie**: por ejemplo, código de motor, potencia en kW, mes de fabricación o referencia de ECU.

Son opcionales, pero aceleran mucho el trabajo:

- código de motor o foto anonimizada de la etiqueta técnica;
- referencia y software de la ECU obtenidos por diagnosis;
- capturas de la aplicación y lista de señales que quedan en `--`;
- una sesión OBD anonimizada;
- manuales o documentación técnica que el usuario posea legalmente.

No se necesita matrícula ni VIN completo. Si excepcionalmente hacen falta caracteres del VIN para distinguir una variante, comparte únicamente los mínimos y no los publiques en el repositorio.

## 3. Cómo debe identificar el agente el coche

El nombre comercial no es una identidad técnica. Antes de aplicar PIDs o fórmulas, el agente debe construir este expediente:

```text
modelo y plataforma
→ intervalo de fabricación y mercado
→ familia de motor, potencia y sistema de inyección/propulsión
→ código de motor probable o confirmado
→ sistemas de emisiones instalados
→ familia, referencia y software de ECU
→ protocolo y direccionamiento de diagnóstico
```

Cada elemento se marca como `confirmado`, `probable`, `ambiguo` o `desconocido`, junto a su fuente. Un perfil parecido sirve para orientar la búsqueda, no para copiar identificadores o escalas.

La investigación debe detener la implementación propietaria si siguen existiendo variantes incompatibles. El OBD-II genérico puede mantenerse operativo mientras se resuelve la identidad.

## 4. Investigación documental, incluidos PDF

El agente debe buscar activamente documentación técnica y conservar una trazabilidad breve de lo encontrado.

### Prioridad de fuentes

1. Portales, manuales de taller, boletines, documentación de diagnosis y programas de formación del fabricante.
2. Normas SAE/ISO y documentación oficial del proveedor de ECU, adaptador o herramienta.
3. Catálogos de recambios y homologaciones que permitan confirmar motor, potencia, emisiones o ECU.
4. Proyectos técnicos reproducibles, documentación de herramientas reconocidas y bases comunitarias con respuestas crudas verificables.
5. Foros o vídeos, únicamente como pistas que deben contrastarse.

### Búsqueda recomendada

Combina la denominación exacta, plataforma, código de motor, ECU y términos técnicos. Ejemplos:

```text
"[modelo]" "[código motor]" workshop manual filetype:pdf
"[código motor]" ECU diagnostic protocol measuring blocks
"[referencia ECU]" PID DID data identifier
site:[dominio oficial] "[modelo/plataforma]" filetype:pdf
"[modelo]" self study programme engine management pdf
"[modelo]" DPF differential pressure regeneration diagnostic
```

Al encontrar un PDF, el agente debe:

1. verificar autor/editor, título, versión, fecha, mercado y variante aplicable;
2. descargarlo solo desde una fuente legítima y leerlo completo o buscar dentro por modelo, código de motor, ECU, `diagnosis`, `data identifier`, `measuring block`, `live data`, `injection`, `turbo`, `EGR`, `DPF/GPF`, `SCR`, `CAN`, `KWP`, `UDS` y unidades;
3. usar OCR si es un escaneo y comprobar manualmente tablas o fórmulas importantes;
4. anotar URL, título, revisión, páginas relevantes y qué afirmación respalda;
5. contrastar identificadores, escalas y unidades con otra fuente o con una respuesta real de la ECU;
6. no subir al repositorio PDF con copyright, de pago, datos personales o licencia incompatible; guardar en el proyecto únicamente citas, enlaces, metadatos y conocimiento derivado permitido.

No se deben eludir pagos, credenciales ni controles de acceso. Si la documentación esencial está en un portal autorizado al que el agente no puede acceder, debe indicar exactamente qué documento necesita que aporte el usuario.

### Fuerza de la evidencia

| Nivel | Evidencia | Uso permitido |
|---|---|---|
| A | Documento primario aplicable + respuesta real coherente | Señal verificada |
| B | Fuente técnica sólida + respuesta real coherente | Implementación con trazabilidad |
| C | Fuente de variante cercana o sin captura real | Candidata pendiente, nunca dato confirmado |
| D | Foro, lista sin procedencia o deducción | Pista de investigación, no implementación productiva |

## 5. Flujo de integración

### 1. Auditar antes de cambiar

El agente lee `README.md`, esta guía, la arquitectura, perfiles existentes, transportes, descubrimiento, informes y pruebas. Ejecuta la suite actual para separar fallos previos de los nuevos.

### 2. Resolver la identidad

Investiga el coche con los datos mínimos, crea una tabla de variantes posibles y descarta cada una con fuentes. Si queda una ambigüedad bloqueante, formula una única pregunta concreta o prepara una lectura de identificación segura.

### 3. Crear el perfil básico

El vehículo se crea desde el Garaje. El código nunca debe depender del UUID local del coche ni añadir vehículos personales a una instalación nueva.

### 4. Crear una matriz de cobertura

Antes de implementar, registrar por señal:

| Campo | Contenido |
|---|---|
| Señal canónica | Nombre estable en la aplicación |
| Utilidad | Qué permite observar o diagnosticar |
| Fuente | OBD estándar, DID, bloque, cálculo, etc. |
| Identificador y respuesta | Servicio, PID/DID/grupo y bytes esperados |
| Decodificación | Longitud, endianess, signo, factor, offset y fórmula |
| Unidad y rango | Unidad canónica y límites físicos |
| Aplicabilidad | Motor/ECU/software al que corresponde |
| Evidencia | Fuente, páginas y captura real |
| Estado | verificada, candidata, no soportada u oculta |

### 5. Implementar por capas

Orden recomendado:

1. resolución de ficha e identidad;
2. PIDs OBD-II realmente soportados;
3. transporte y direccionamiento de fabricante, solo lectura;
4. catálogo de señales propietarias;
5. inventario de capacidades de esa ECU;
6. interfaz que muestre solo señales aplicables;
7. cálculos derivados y reglas diagnósticas;
8. pruebas, documentación, compilación y paquete Windows.

### 6. Probar con el coche real

El agente debe entregar una prueba corta y segura: estado del contacto/motor, temperatura, duración, acciones, límites de RPM/carga, señales objetivo, archivos que devolver y criterios de aborto por tensión, latencia o pérdida de respuestas.

Primero se valida detenido. Una prueba en carretera exige acompañante: el conductor nunca debe manejar el ordenador.

## 6. Reglas que nunca deben romperse

- Solo lectura: sin codificación, adaptación, borrado de DTC, actuadores, rutinas, desbloqueos ni flasheo.
- No inventar PIDs, DID, grupos, bytes, fórmulas, unidades o compatibilidad.
- Separar datos medidos, calculados, inferidos, simulados, obsoletos y ausentes.
- Un timeout o un cero artificial nunca es una medición.
- Ocultar tarjetas definitivamente no soportadas; dejar pendientes solo si existe una vía concreta de validación.
- No usar simulación como respaldo en producción.
- Verificar comportamiento temporal, no solo que un número parezca razonable.
- Vigilar latencia y carga del bus; más señales no compensan una captura inestable.
- Usar datos temporales para las pruebas y no modificar el garaje real del desarrollador.
- Añadir pruebas de respuestas válidas, no disponibles, truncadas, erróneas y de otra variante.

## 7. Magnitudes delicadas

### Consumo

Priorizar caudal de combustible medido. Si no existe, calcular solo con entradas verificadas —por ejemplo, cantidad por ciclo, RPM y arquitectura confirmada— y etiquetarlo como derivado. El consumo medio integra combustible y distancia; no es la media aritmética del consumo instantáneo. Debe informar cobertura y excluir velocidad o muestras inválidas.

### DPF, GPF y SCR

Hollín calculado, hollín medido, ceniza, presión diferencial, EGT, regeneración y AdBlue suelen estar en servicios distintos. `I/M Readiness` no representa la carga del filtro. No deducir regeneración a partir de una sola temperatura.

### Turbo y EGR

Confirmar presión absoluta frente a relativa y sincronizar valores solicitado/real. Masa de aire objetivo/real no equivale necesariamente al porcentaje de apertura EGR.

### Híbridos y eléctricos

No reutilizar perfiles térmicos. Pueden requerir ECUs múltiples, DoIP o acceso CAN específico. No sondear buses de seguridad ni enviar tramas de control.

## 8. Prompt listo para copiar

El prompt completo, mantenido por separado para que sea fácil copiarlo, está en:

**[`PROMPT_IMPORTAR_VEHICULO_CON_IA.md`](PROMPT_IMPORTAR_VEHICULO_CON_IA.md)**

Solo es obligatorio sustituir la línea `MI VEHÍCULO`. El resto de campos son opcionales: el agente debe investigar lo que falte y preguntar únicamente cuando una ambigüedad impida continuar con rigor.

## 9. Qué devolver después de una prueba

- identificador y duración de la sesión;
- contacto o motor encendido, frío/caliente y vehículo detenido/en marcha;
- acciones realizadas;
- texto exacto de cualquier error y momento aproximado;
- capturas solicitadas y archivo de telemetría/log anonimizado;
- valores de una herramienta de contraste, si existe.

## 10. Cuándo está terminada

- La identidad técnica y sus incertidumbres están documentadas.
- El coche funciona desde una base vacía y conserva el modo OBD genérico si falla la capa propietaria.
- Cada señal visible tiene procedencia, unidad, estado y evidencia.
- Las señales no soportadas se ocultan o explican con claridad.
- Los datos derivados indican método y condiciones de validez.
- No hay valores simulados ni datos personales en producción.
- Pasan las pruebas Python, el build de la interfaz y el smoke test del ejecutable.
- Existe una tabla final: medida, calculada, pendiente, no soportada y oculta.

Una buena integración no es la que muestra más relojes: es la que puede demostrar de dónde sale cada valor y cuándo merece confianza.
