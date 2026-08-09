# Lecturas Volkswagen para el Passat B6 CBAB

> Esta ruta no corresponde al coche identificado durante la prueba real. La
> referencia leída fue `03G 906 018 FG`, familia BKP inyector-bomba, y desde la
> versión 1.7 la aplicación la deriva automáticamente a KWP2000/TP2.0. Este
> documento se conserva únicamente para vehículos que sí monten una ECU CBAB
> UDS.

La aplicación 1.6 incorpora una capa UDS Volkswagen independiente del OBD-II
genérico. Está limitada por código al servicio `0x22` (lectura de datos por
identificador) y a la dirección de la ECU de motor `7E0/7E8`.

No contiene operaciones de escritura, codificación, adaptación, regeneración,
rutinas, desbloqueo de seguridad ni borrado de averías.

## Primera conexión

1. Conectar el Vgate vLinker FS y poner el contacto.
2. Seleccionar el Passat y pulsar **Conectar OBD**.
3. La aplicación consulta la referencia, el hardware y el software de la ECU.
4. El resultado diferencia entre señal verificada, respuesta rechazada y señal
   pendiente de mapa para esa versión exacta de la centralita.

No se debe iniciar la marcha hasta que termine esta identificación. Después se
puede realizar el diagnóstico guiado habitual.

## Parámetros previstos

La capa admite temperatura de aceite y escape, presión barométrica, pedal,
turbo solicitado/real, EGR solicitada/real, rail solicitado/real, avance y
caudal de inyección, correcciones de los cuatro inyectores, tensión de ECU y
estado completo del DPF.

Los nombres VCDS `IDE...` no son identificadores UDS utilizables directamente.
La escala, posición de bytes y DID se habilitan únicamente después de
confirmarlos para la referencia y versión de software leídas del coche.

La plantilla persistente se crea en:

```text
%LOCALAPPDATA%\MiCochePorDentro\config\vag_cbab_readonly.json
```

Un valor con `did: null` significa «pendiente de mapear» y nunca se consulta.
La aplicación tampoco convierte una ausencia de respuesta en el número cero.

## Criterio de validación

Una definición solo debe activarse cuando:

- coincide con la referencia de ECU indicada en `ecu_part_numbers`;
- responde tres veces sin errores;
- la unidad y escala se contrastan con una herramienta VAG conocida;
- el valor reacciona de forma coherente durante ralentí, aceleración suave y
  retención;
- permanece dentro de los límites físicos configurados.

Hasta entonces los diez parámetros OBD-II ya comprobados siguen capturándose
con normalidad y los canales propietarios permanecen separados y visibles como
pendientes.
