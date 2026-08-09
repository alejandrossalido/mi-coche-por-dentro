# Mi Coche por Dentro

Aplicación local para registrar telemetría OBD-II, guardar sesiones de diagnóstico, comparar pruebas y generar informes comprensibles. Combina lecturas OBD estándar con perfiles específicos de fabricante cuando existen datos técnicos y capturas reales suficientes para verificarlos.

> Estado: versión pública en preparación. La aplicación es de solo lectura para diagnóstico; no sustituye a un profesional ni debe utilizarse para codificar, adaptar o modificar una ECU.

## Las dos guías principales

1. Este documento explica cómo instalar, abrir y utilizar la aplicación por primera vez.
2. La [Guía de uso e importación de vehículos con IA](docs/GUIA_USO_E_IMPORTACION_CON_IA.md) explica el uso avanzado y contiene un prompt completo para ampliar la compatibilidad de un coche con Codex u otro agente de programación.

## Qué hace la aplicación

- Crea un garaje local con los vehículos del usuario.
- Detecta adaptadores serie y excluye puertos que claramente no son OBD.
- Se conecta a la ECU mediante OBD-II y comprueba el protocolo disponible.
- Descubre las señales que realmente responde cada vehículo.
- Ejecuta pruebas guiadas de motor, refrigeración, admisión, combustible y emisiones.
- Registra telemetría sincronizada y permite marcar tirones, vibraciones, humo, ruidos o pérdidas de potencia.
- Lee DTC, Freeze Frame, monitores de emisiones y Modo 06 cuando la ECU los ofrece.
- Analiza sesiones terminadas y genera informes en lenguaje comprensible.
- Compara capturas de antes y después de una reparación.
- Mantiene separados los datos medidos, calculados, simulados y no disponibles.

La cantidad de datos depende del vehículo, la ECU, el protocolo y el adaptador. RPM o temperatura suelen ser estándar; inyección, turbo, EGR y DPF suelen requerir PIDs o bloques propietarios. Una señal no verificada no debe presentarse como una medición real.

## Requisitos

### Para utilizar el código fuente

- Windows 10 u 11 de 64 bits.
- Python 3.11 de 64 bits.
- Node.js 20 LTS y npm.
- Aproximadamente 3 GB libres durante la instalación y compilación.
- Un adaptador OBD-II USB compatible para lecturas reales.

Se recomienda una conexión USB estable. Los clones ELM327 baratos pueden perder respuestas, bloquearse con muchas peticiones o no soportar protocolos ampliados.

### Para usar un ejecutable publicado

Cuando exista una versión en GitHub Releases, solo será necesario Windows y el adaptador. Siempre se debe descargar y descomprimir la carpeta completa del programa, no únicamente el archivo `.exe`.

## Instalación desde el código

Abre PowerShell dentro de la carpeta del proyecto y ejecuta:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Set-Location dashboard
npm ci
npm run build
Set-Location ..

Copy-Item .env.example .env
```

La primera instalación puede tardar varios minutos porque incluye las bibliotecas de análisis, la interfaz web y las herramientas de escritorio.

### Configuración opcional

El funcionamiento local no necesita una clave de IA. El proveedor remoto está desactivado de forma predeterminada.

En desarrollo se puede editar el archivo `.env` situado en la raíz. En un ejecutable instalado se puede crear:

```text
%LOCALAPPDATA%\MiCochePorDentro\config\.env
```

Las variables ya definidas en Windows tienen prioridad y nunca son sobrescritas por esos archivos. No publiques `.env` ni claves API.

## Cómo abrir la aplicación

### Desde el código

Haz doble clic en `Iniciar_App.bat` o ejecuta:

```powershell
.\start.ps1
```

Si PowerShell bloquea temporalmente el script:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\start.ps1
```

### Desde un paquete compilado

Abre `MiCochePorDentro.exe` dentro de la carpeta descomprimida. Windows puede mostrar SmartScreen mientras el ejecutable no tenga firma digital; comprueba siempre que procede de la página oficial del proyecto.

La aplicación inicia un servidor exclusivamente local en `127.0.0.1`. Si el puerto 8000 está ocupado, selecciona automáticamente otro. Solo se permite una ventana por perfil de datos.

## Primera puesta en marcha

1. Elige **Modo guiado** si es tu primera vez. El modo profesional muestra más controles y datos técnicos.
2. Pulsa **Añadir vehículo**.
3. Introduce marca, modelo, año y tipo de propulsión.
4. Añade, si los conoces, generación, variante, motor, código de motor y mercado.
5. No es necesario introducir matrícula ni VIN.

Una instalación pública nueva comienza con el garaje vacío. Añadir un coche al garaje permite utilizar inmediatamente la cobertura OBD genérica. La compatibilidad propietaria avanzada se explica en la segunda guía.

## Conectar el adaptador OBD

1. Con el vehículo detenido y en un lugar ventilado, conecta el adaptador al puerto OBD-II.
2. Conecta el cable USB al ordenador y espera a que Windows cree el puerto COM.
3. Pon el contacto. Arranca el motor solo si la prueba seleccionada lo requiere.
4. Cierra VCDS, FORScan, Torque u otros programas que puedan estar utilizando el mismo puerto.
5. Selecciona el vehículo correcto en la aplicación.
6. Selecciona el puerto marcado como recomendado y pulsa **Conectar OBD**.
7. Comprueba el mensaje superior: puerto, protocolo, latencia y estado de la ECU.

En vehículos Volkswagen compatibles, la aplicación puede intentar identificar de forma segura la centralita y sus señales propietarias. Esa identificación es de solo lectura. Si el canal ampliado no abre, la conexión OBD genérica puede seguir funcionando.

## Hacer un diagnóstico

1. Conecta la ECU antes de iniciar una captura.
2. Escoge una prueba guiada: diagnóstico completo, batería, refrigeración, ralentí, admisión/turbo, combustible o emisiones.
3. Lee las instrucciones de seguridad y confirma si el motor está frío, templado o caliente.
4. Pulsa **Validar OBD e iniciar**. La aplicación comprueba primero que existen señales reales compatibles.
5. Sigue la prueba sin manipular el ordenador durante la conducción. Los marcadores de incidencias debe accionarlos un acompañante o utilizarse con el coche detenido.
6. Pulsa **Finalizar y analizar**.
7. Abre **Informe** para ver el resumen, la calidad de los datos, hallazgos y limitaciones.

No interpretes `--` como una avería: significa que esa ECU no ha ofrecido la señal, todavía no se ha identificado o no existe suficiente evidencia para mostrarla.

## Módulos principales

- **Diagnóstico:** captura actual, instrumentos, incidencias, DTC y pruebas guiadas.
- **Sesiones:** historial de capturas y selección de una sesión concreta.
- **Asistente de diagnóstico:** explicación de la sesión seleccionada sin mezclar datos de otros trayectos.
- **Antes / Después:** comparación controlada de dos sesiones del mismo coche.
- **Garaje:** ficha, cobertura, capacidades, línea base y reparaciones.
- **ITV / Monitores:** estado digital que informa la ECU; no garantiza superar una inspección oficial.
- **Modo 06:** resultados internos de monitores cuando el vehículo los expone.

## Dónde se guardan los datos

Los datos personales no se guardan dentro del proyecto:

```text
%LOCALAPPDATA%\MiCochePorDentro
```

Allí se almacenan base de datos, telemetría, registros, copias de seguridad y configuración. Borrar la carpeta del código no elimina las sesiones. Para probar un perfil independiente se puede definir `MICOCHE_HOME` antes de abrir la aplicación.

## Problemas frecuentes

### No aparece el adaptador

- Comprueba el Administrador de dispositivos de Windows.
- Instala el controlador USB del fabricante.
- Cambia de cable o puerto USB.
- Verifica que el puerto no sea Intel AMT, Bluetooth genérico u otro dispositivo no OBD.

### El adaptador aparece, pero no responde la ECU

- Pon el contacto.
- Confirma que has elegido el COM correcto.
- Cierra cualquier otro software de diagnóstico.
- Desconecta el adaptador durante diez segundos y vuelve a conectarlo.
- Evita concentradores USB sin alimentación.

### La ECU parece desconectarse durante una captura

Una respuesta lenta no siempre es una desconexión. Revisa latencia, porcentaje de lecturas correctas y el tiempo desde el último dato válido. Si ocurre repetidamente, reduce la cantidad de señales solicitadas, revisa el adaptador y guarda el registro para analizarlo.

### Faltan datos de DPF, turbo o inyección

Es habitual: muchos no son PIDs OBD estándar. No copies fórmulas de otro motor sin validar. Sigue la [guía avanzada](docs/GUIA_USO_E_IMPORTACION_CON_IA.md) para investigar e integrar el vehículo.

## Verificación para desarrolladores

```powershell
$env:MICOCHE_HOME = Join-Path $env:TEMP "MiCochePorDentro-Test"
.\.venv\Scripts\python.exe -m pytest -q

Set-Location dashboard
npm run build
Set-Location ..

.\scripts\build_windows.ps1
```

Antes de publicar un ejecutable debe ejecutarse también `scripts/smoke_test_windows.ps1` sobre el paquete generado.

## Seguridad

- No uses la interfaz mientras conduces.
- No borres DTC antes de guardar el estado y reparar la causa.
- No conectes simultáneamente varios programas al mismo adaptador.
- No añadas comandos de escritura, codificación, adaptación, actuadores o rutinas sin un diseño de seguridad independiente.
- Los resultados dependen de la calidad y cobertura de las lecturas; no sustituyen las pruebas mecánicas.

## Licencia

Este proyecto se publica bajo la [PolyForm Noncommercial License 1.0.0](LICENSE).

Puedes usarlo, estudiarlo, modificarlo y compartirlo para fines personales, educativos o no comerciales. No está permitido venderlo, redistribuirlo como producto comercial, integrarlo en servicios de pago o utilizarlo con finalidad comercial sin permiso escrito del autor.
