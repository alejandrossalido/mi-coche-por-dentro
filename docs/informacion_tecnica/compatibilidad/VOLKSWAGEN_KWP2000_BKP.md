# Lecturas Volkswagen del Passat B6 BKP

La ECU identificada en la prueba real es `03G 906 018 FG`, correspondiente a
un motor BKP 2.0 TDI de 103 kW con sistema inyector-bomba. No es una ECU CBAB
common-rail. Por tanto, no existe presión de rail que se pueda recuperar.

Desde la versión 1.7 la aplicación abre un canal Volkswagen TP2.0 y consulta
exclusivamente bloques de medición KWP2000 mediante el servicio de lectura
`0x21`. No envía escritura, codificación, adaptación, rutinas, regeneración ni
borrado.

## Primera conexión después de actualizar

1. Conectar el Vgate vLinker FS al coche y al ordenador.
2. Poner el contacto y arrancar el motor.
3. Abrir `MiCochePorDentro.exe`, seleccionar el Passat y pulsar **Conectar**.
4. Esperar a que finalice la identificación Volkswagen sin iniciar una captura.
5. Revisar el resumen: cada señal aparecerá como verificada o no ofrecida.
6. Iniciar después un diagnóstico completo guiado.

Se prueban los bloques de RPM, refrigerante, velocidad, admisión, pedal, EGR,
turbo, cantidad e inicio de inyección, correcciones de los cuatro inyectores,
temperaturas, tensión de ECU y, si el equipamiento los incluye, valores DPF.
La aplicación solo guarda y muestra un canal propietario cuando el tipo binario
y el rango de su respuesta son compatibles; una ausencia nunca se convierte en
cero.

El Vgate debe permanecer conectado durante toda la identificación y captura.
KWP2000/TP2.0 y OBD-II estándar usan configuraciones distintas del adaptador;
la aplicación restaura automáticamente OBD-II al finalizar o abortar.

Desde la versión 1.9.3 también se aceptan respuestas idénticas duplicadas
por el vLinker durante la apertura del canal. El Passat puede contestar una sola
vez y el adaptador entregar dos copias de la misma trama `201`; ambas representan
una única respuesta válida del gateway.

## Particularidad comprobada en la ECU PPD1.5

La referencia `03G 906 018 FG`, software `0907`, responde con ocho valores de
tres bytes en cada bloque, aunque los cuatro primeros mantienen la disposición
documentada por la familia BKP. La versión 1.7.1 acepta esta respuesta extendida
y conserva los campos auxiliares sin asignarles un significado no confirmado.

Las pruebas reales verifican, entre otros canales, RPM, velocidad, temperaturas
de refrigerante, radiador, admisión, aceite, combustible y ambiente, presión
barométrica, pedal, masa de aire, EGR, turbo, inicio/cantidad/duración de
inyección, consumo, par, correcciones y estados de los inyectores, tensión de
ECU, carga del alternador, velocidad del árbol de levas y mando del ventilador.
Cada nombre conserva la trama cruda que permitió validarlo. Los bloques 068 y
069 devolvieron únicamente marcadores vacíos; como este BKP concreto no lleva
DPF de fábrica, esos recuadros no se presentan como ceros ni como datos reales.

En la sesión real usada para validar la ampliación, el radiador entregó
45–48 °C, el mando del ventilador 46,5–56,3 %, la carga del alternador 31–49 %
y el árbol de levas 400–920 rpm. Son lecturas KWP2000 directas de la ECU, no
estimaciones calculadas por la interfaz.

## Diagnóstico específico de consumo (versión 1.8)

El BKP utiliza inyectores-bomba piezoeléctricos y no dispone de un rail común.
La pantalla de combustible ya no muestra presión de rail, correcciones STFT/LTFT
ni control de mezcla de gasolina como datos pendientes para este motor.

La identificación amplía la lectura segura a los grupos relacionados con el
consumo: temperatura de combustible, duración e inicio de inyección, valor de
torsión de la distribución, par calculado, estados BIP y desviaciones de
conmutación de los cuatro inyectores. Todos deben superar la misma comprobación
de tipo y plausibilidad antes de declararse disponibles.

El perfil **Consumo e inyección** dura 12 minutos y separa ralentí caliente,
circulación urbana, velocidad constante, carga progresiva, retención y ralentí
final. El informe evalúa cantidad de inyección, equilibrio de inyectores,
torsión, temperatura de servicio, seguimiento EGR y seguimiento del turbo. Una
señal ausente se informa como cobertura pendiente; nunca se usa como evidencia
de avería.
