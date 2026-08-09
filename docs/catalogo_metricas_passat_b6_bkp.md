# Catálogo de métricas — Passat B6 BKP / ECU 03G 906 018 FG

Este catálogo contiene los bloques de medida documentados para la familia Siemens/VDO PPD1.5. Una métrica es **potencial** hasta que la ECU concreta la devuelve; la aplicación solo la marca **confirmada** después de una lectura real con evidencia bruta.

- Bloques documentados: **69**
- Posiciones documentadas: **214**
- Método: KWP2000 `ReadDataByLocalIdentifier (0x21)` sobre TP2.0, exclusivamente lectura.
- Fuentes de contraste: identificación pública de la referencia `03G 906 018 FG`, catálogo abierto de la familia `03G-906-018` y comprobación directa contra la ECU.

## Combustible, mezcla y emisiones

- **Bloque 001 — Cantidad de inyección:** `001.1` Revoluciones del motor; `001.2` Cantidad de inyección; `001.3` Duración de inyección solicitada; `001.4` Temperatura del refrigerante
- **Bloque 004 — Sistema inyector-bomba:** `004.1` Revoluciones del motor; `004.2` Inicio de inyección solicitado; `004.3` Duración de inyección solicitada; `004.4` Valor de torsión de la distribución
- **Bloque 008 — Límites de inyección I:** `008.1` Revoluciones del motor; `008.2` Par solicitado por el conductor; `008.3` Límite de par; `008.4` Límite de humo
- **Bloque 009 — Límites de inyección II:** `009.1` Revoluciones del motor; `009.2` Par solicitado por el control de crucero; `009.3` Límite de la transmisión; `009.4` Restricción de par
- **Bloque 013 — Equilibrado de inyectores:** `013.1` Corrección del inyector 1; `013.2` Corrección del inyector 2; `013.3` Corrección del inyector 3; `013.4` Corrección del inyector 4
- **Bloque 015 — Consumo y par:** `015.1` Revoluciones del motor; `015.2` Par calculado del motor; `015.3` Caudal de combustible; `015.4` Par solicitado por el conductor
- **Bloque 018 — Estado eléctrico de inyectores:** `018.1` Estado del inyector 1; `018.2` Estado del inyector 2; `018.3` Estado del inyector 3; `018.4` Estado del inyector 4
- **Bloque 023 — Conmutación de los inyectores:** `023.1` Tiempo de conmutación del inyector 1; `023.2` Tiempo de conmutación del inyector 2; `023.3` Tiempo de conmutación del inyector 3; `023.4` Tiempo de conmutación del inyector 4
- **Bloque 030 — Control de oxígeno I:** `030.1` Calibración de la sonda; `030.2` Tensión de compensación; `030.3` Concentración de oxígeno; `030.4` Estado de regulación
- **Bloque 031 — Control de oxígeno II:** `031.1` Caudal total de aire; `031.2` Control de calefacción; `031.3` Señal de temperatura; `031.4` Señal de tensión de oxígeno
- **Bloque 032 — Control de oxígeno III:** `032.1` Caudal total de aire; `032.2` Temperatura exterior; `032.3` Presión de aire de la sonda; `032.4` Señal de tensión de oxígeno
- **Bloque 033 — Control de oxígeno IV:** `033.1` Revoluciones del motor; `033.2` Temperatura de escape; `033.3` Contrapresión de escape; `033.4` Caudal másico de escape
- **Bloque 034 — Diagnóstico de la sonda de oxígeno:** `034.1` Señal de oxígeno; `034.2` Electrónica de la sonda; `034.3` Plausibilidad de la sonda; `034.4` Diagnóstico de la sonda
- **Bloque 040 — Sonda de oxígeno:** `040.1` Revoluciones del motor; `040.2` Cantidad de inyección; `040.3` Estado de calefacción de la sonda; `040.4` Valor de oxígeno
- **Bloque 067 — DPF: temperaturas y presión:** `067.1` Temperatura antes del turbo; `067.2` Temperatura en el DPF; `067.3` Presión diferencial del DPF; `067.4` Compensación de presión diferencial
- **Bloque 068 — DPF: hollín y ceniza:** `068.1` Carga de hollín; `068.2` Masa de ceniza; `068.3` Aprendizaje de ceniza
- **Bloque 069 — DPF: estado de regeneración I:** `069.1` Estado de regeneración 1; `069.4` Estado de regeneración 4
- **Bloque 070 — DPF: estado de regeneración II:** `070.1` Estado de regeneración; `070.2` Tiempo de regeneración; `070.3` Regeneraciones fallidas; `070.4` Regeneraciones correctas
- **Bloque 071 — DPF: postinyección:** `071.1` Revoluciones del motor; `071.2` Cantidad de postinyección; `071.3` Habilitación de la inyección; `071.4` Periodo de alimentación
- **Bloque 073 — DPF: datos desde regeneración:** `073.1` Consumo desde la regeneración; `073.2` Distancia desde la regeneración; `073.3` Tiempo desde la regeneración
- **Bloque 074 — DPF: emisiones III:** `074.1` Revoluciones del motor; `074.2` Temperatura antes del turbo; `074.3` Valor de oxígeno; `074.4` Compensación de inyección
- **Bloque 075 — DPF: emisiones IV:** `075.1` Temperatura antes del turbo; `075.2` Temperatura antes del DPF; `075.3` Carga de hollín; `075.4` Temperatura después del DPF
- **Bloque 090 — EOBD de la EGR I:** `090.1` Revoluciones del motor; `090.2` Cantidad de inyección; `090.3` EGR solicitada; `090.4` Estado de desviación
- **Bloque 091 — EOBD de la EGR II:** bloque de identificación/estado; sus campos se enumeran si la ECU responde.

## Motor, marcha y mandos

- **Bloque 002 — Ralentí:** `002.1` Revoluciones del motor; `002.2` Posición del pedal del acelerador; `002.3` Estado de funcionamiento; `002.4` Temperatura del refrigerante
- **Bloque 005 — Condiciones del último arranque:** `005.1` Revoluciones del motor; `005.2` Par de arranque; `005.3` Sincronización de arranque; `005.4` Temperatura del refrigerante
- **Bloque 006 — Control de crucero:** `006.1` Velocidad real; `006.2` Supervisión de pedales; `006.3` Posición del pedal del acelerador; `006.4` Supervisión de mandos
- **Bloque 020 — Límites de par solicitados por ABS:** `020.1` Revoluciones del motor; `020.2` Par del motor; `020.3` Límite ASR; `020.4` Límite MSR
- **Bloque 025 — Arranque y salida:** `025.1` Revoluciones del motor; `025.2` Estado del terminal 50; `025.3` Estado del motor; `025.4` Motivo de salida abortada
- **Bloque 027 — Limitador de velocidad:** `027.3` Velocidad; `027.4` Límite de velocidad
- **Bloque 028 — Sensores del pedal del acelerador:** `028.1` Sensor 1 del pedal; `028.2` Sensor 2 del pedal; `028.3` Estado de funcionamiento; `028.4` Posición calculada del pedal
- **Bloque 051 — Reconocimiento de giro:** `051.1` Revoluciones del motor; `051.2` Velocidad del árbol de levas; `051.3` Sincronización de arranque; `051.4` Corte de la secuencia de inyección

## Admisión, EGR y turbo

- **Bloque 003 — Recirculación de gases EGR:** `003.1` Revoluciones del motor; `003.2` Masa de aire EGR solicitada; `003.3` Masa de aire EGR real; `003.4` Mando de la EGR
- **Bloque 010 — Control de sobrealimentación I:** `010.1` Masa de aire real; `010.2` Presión atmosférica; `010.3` Presión de turbo real; `010.4` Posición del pedal del acelerador
- **Bloque 011 — Control de sobrealimentación II:** `011.1` Revoluciones del motor; `011.2` Presión de turbo solicitada; `011.3` Presión de turbo real; `011.4` Mando del turbo
- **Bloque 041 — EGR y colector de admisión I:** `041.1` Posición solicitada del colector; `041.2` Posición solicitada de EGR; `041.3` Posición real de EGR; `041.4` Mando de EGR
- **Bloque 042 — EGR y colector de admisión II:** `042.1` Aprendizaje de cierre de EGR; `042.2` Adaptación de EGR; `042.3` Posición real del colector; `042.4` Posición real de EGR
- **Bloque 043 — Compuerta de sobrealimentación:** `043.1` Mando de la compuerta; `043.2` Posición de la compuerta
- **Bloque 044 — Colector y enfriador EGR:** `044.1` Revoluciones del motor; `044.2` Masa de aire real; `044.3` Enfriador EGR; `044.4` Válvula del colector
- **Bloque 045 — Presión y masa de admisión:** `045.2` Presión del volumen de admisión; `045.3` Masa de aire real; `045.4` Presión de turbo real
- **Bloque 046 — Colector de admisión I:** `046.1` Posición solicitada; `046.2` Regulador de posición; `046.3` Posición real; `046.4` Mando del colector
- **Bloque 047 — Colector de admisión II:** `047.1` Aprendizaje de posición cerrada; `047.2` Aprendizaje de posición abierta; `047.3` Mando del colector; `047.4` Posición real

## Temperaturas y refrigeración

- **Bloque 007 — Temperaturas:** `007.1` Temperatura del combustible; `007.3` Temperatura del aire de admisión; `007.4` Temperatura del refrigerante
- **Bloque 029 — Aceite del motor:** `029.1` Temperatura del aceite; `029.2` Nivel de aceite; `029.3` Índice de desgaste; `029.4` Índice de hollín
- **Bloque 062 — Temperaturas de refrigeración:** `062.1` Refrigerante a la salida del motor; `062.2` Refrigerante a la salida del radiador; `062.3` Temperatura ambiente; `062.4` Temperatura del aire de admisión
- **Bloque 063 — Refrigeración y climatización:** `063.1` Presión del refrigerante del climatizador; `063.2` Par de carga del climatizador; `063.3` Petición de refrigeración; `063.4` Desconexión del climatizador
- **Bloque 064 — Refrigeración del motor:** `064.1` Temperatura del refrigerante; `064.2` Refrigerante a la salida del radiador; `064.3` Mando del ventilador 1

## Sistema eléctrico, ECU y comunicaciones

- **Bloque 012 — Precalentamiento:** `012.1` Estado de calentadores; `012.2` Tiempo de precalentamiento; `012.3` Tensión de alimentación; `012.4` Temperatura del refrigerante
- **Bloque 016 — Calefacción auxiliar y alternador:** `016.1` Carga del alternador; `016.4` Tensión de alimentación
- **Bloque 017 — Disponibilidad EOBD:** `017.1` Estado EOBD A; `017.2` Estado EOBD B; `017.3` Estado EOBD C; `017.4` Estado EOBD D
- **Bloque 021 — Estado del bus CAN del tren motriz:** `021.1` Electrónica del motor; `021.2` Electrónica de la transmisión; `021.3` Electrónica de frenos; `021.4` Control de estabilidad ESP
- **Bloque 022 — Motivos de desconexión:** `022.1` Desconexión del control de crucero; `022.2` Mandos del control de crucero; `022.3` Desconexión del control de turbo; `022.4` Desconexión del climatizador
- **Bloque 026 — Suma de comprobación:** `026.1` Suma de comprobación
- **Bloque 080 — Identificación avanzada de la ECU I:** bloque de identificación/estado; sus campos se enumeran si la ECU responde.
- **Bloque 081 — Identificación avanzada de la ECU II:** `081.1` Número VIN; `081.2` Identificador del inmovilizador
- **Bloque 082 — Identificación avanzada de la ECU III:** bloque de identificación/estado; sus campos se enumeran si la ECU responde.
- **Bloque 086 — Datos EOBD I:** bloque de identificación/estado; sus campos se enumeran si la ECU responde.
- **Bloque 087 — Datos EOBD II:** bloque de identificación/estado; sus campos se enumeran si la ECU responde.
- **Bloque 089 — Datos EOBD III:** bloque de identificación/estado; sus campos se enumeran si la ECU responde.
- **Bloque 110 — Control del motor de arranque I:** `110.1` Estado del terminal 50
- **Bloque 111 — Control del motor de arranque II:** `111.2` Condición de corte 1; `111.3` Condición de corte 2; `111.4` Tensión de servicios
- **Bloque 125 — Comunicación CAN I:** `125.1` Transmisión; `125.2` Electrónica de frenos; `125.3` Cuadro de instrumentos; `125.4` Airbag
- **Bloque 126 — Comunicación CAN II:** `126.1` Climatizador; `126.3` Central eléctrica
- **Bloque 127 — Comunicación CAN III:** `127.4` Electrónica del volante
- **Bloque 128 — Comunicación CAN IV:** `128.1` Pasarela CAN
- **Bloque 225 — Tiempo de espera CAN I:** `225.1` Transmisión; `225.2` Electrónica de frenos; `225.3` Cuadro de instrumentos; `225.4` Airbag
- **Bloque 226 — Tiempo de espera CAN II:** `226.1` Climatizador; `226.3` Central eléctrica
- **Bloque 227 — Tiempo de espera CAN III:** `227.3` Electrónica del volante
- **Bloque 228 — Tiempo de espera CAN IV:** `228.1` Pasarela CAN

## Interpretación de estados

- **Confirmada:** la ECU devolvió el campo, el tipo binario se pudo decodificar y se guardó su trama.
- **Pendiente:** está documentada pero todavía no se ha ejecutado el inventario completo con el coche conectado.
- **No disponible:** la ECU devolvió un marcador vacío, omitió el campo o rechazó el bloque.
- **Sin decodificar:** la ECU devolvió bytes reales, pero su tipo todavía no tiene una conversión fiable; los bytes se conservan para poder añadirla después.
