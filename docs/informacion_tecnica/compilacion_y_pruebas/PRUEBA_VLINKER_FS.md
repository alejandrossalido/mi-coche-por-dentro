# Lista de comprobación — primera prueba con Vgate vLinker FS USB

## Antes de bajar al coche

- [ ] Cierra la versión antigua de Mi Coche por Dentro.
- [ ] Abre `dist-1.4.0\MiCochePorDentro\MiCochePorDentro.exe`.
- [ ] Lleva el portátil con batería suficiente y desactiva la suspensión automática.
- [ ] Ten creado el vehículo correcto con marca, modelo, año, motor y combustible.
- [ ] No actualices el firmware “por si acaso”. Si Windows no crea un puerto COM,
      descarga primero el paquete oficial `vLinker FS_USB` del centro de descargas
      de Vgate.

Fuentes oficiales:

- Producto: https://vgatemall.com/products-detail/i-19/
- Descargas: https://www.vgatemall.com/downloadcenter/?page=1

## Primera conexión, con el coche parado

- [ ] Conecta el vLinker FS al USB y comprueba en el Administrador de dispositivos
      que aparece un puerto COM.
- [ ] Enchufa el adaptador al conector OBD-II del coche.
- [ ] Pon el contacto sin arrancar.
- [ ] Abre la aplicación, selecciona el vehículo y pulsa **Conectar OBD**.
- [ ] Anota o captura el puerto COM, protocolo y latencia que muestra la aplicación.
- [ ] Si no lo detecta, prueba otro puerto USB. Algunos equipos pueden necesitar un
      concentrador USB como puente, según el aviso de compatibilidad publicado por Vgate.

## Comprobaciones sin circular

- [ ] Ejecuta la prevalidación y comprueba que existen PIDs verificados.
- [ ] Haz un escaneo DTC manual y **no borres ningún código**.
- [ ] Comprueba si aparece freeze frame real asociado al DTC.
- [ ] Revisa **ITV / Monitores** con el contacto puesto.
- [ ] Revisa **Modo 06**. Que no aparezcan resultados puede significar que la ECU o
      el protocolo no los ofrece; no es motivo para inventar valores.
- [ ] Arranca el motor y registra una prueba corta de ralentí caliente de 3–5 minutos.
- [ ] Finaliza desde la aplicación y espera a que complete el escaneo DTC final.

## Primera prueba en carretera

- [ ] Hazla solo si la conexión en parado ha sido estable.
- [ ] Configura antes de salir el perfil, título, síntoma y kilometraje.
- [ ] El conductor no debe tocar el portátil ni la aplicación durante la marcha.
      Utiliza un acompañante para marcar tirones, ruidos o pérdidas de potencia.
- [ ] Empieza con un recorrido corto y seguro, sin provocar cargas extremas.
- [ ] Finaliza la captura estando ya detenido y espera a que se guarden datos y DTC.

## Qué verificar al terminar

- [ ] En **Sesiones**, confirma duración, número de lecturas, señales y origen “medido”.
- [ ] En el asistente pregunta: “¿En qué datos exactos te basas?”.
- [ ] Comprueba que la respuesta identifica la sesión, el número de lecturas, los PIDs,
      el alcance DTC y, cuando exista, el histórico del propio coche.
- [ ] Pregunta por un PID concreto y contrasta mínimo, media y máximo con la telemetría.
- [ ] Exporta una copia ZIP del vehículo desde **Garaje**.
- [ ] Repite tres capturas limpias y comparables para que la aplicación pueda construir
      una referencia histórica del vehículo.

## Si algo falla

- Sin puerto COM: instala el controlador incluido en el paquete oficial de Vgate.
- Puerto COM pero sin ECU: revisa contacto, conector, vehículo seleccionado y prueba
  otro USB.
- Conexión inestable: prueba `fast=False` en desarrollo o un puerto/concentrador USB
  distinto; conserva el registro de la aplicación.
- No actualices firmware durante una prueba ni interrumpas una actualización iniciada.
- No confundas la conmutación HS/MS-CAN que ofrece el hardware para FORScan con soporte
  automático de PIDs OEM en esta aplicación: aquí solo se muestran definiciones
  propietarias cuando exista un paquete verificado.
