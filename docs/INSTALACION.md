# Instalación

## Sistemas compatibles

La versión actual está preparada y probada para **Windows 10 y Windows 11 de 64 bits**. No es exclusiva de Windows 11.

Linux y macOS todavía no están soportados como producto terminado. Parte del código podría adaptarse, pero faltan un instalador, rutas de datos, ventana de escritorio y conexión OBD validados para esos sistemas.

## Opción recomendada: aplicación preparada

Cuando haya una versión publicada en **GitHub Releases**:

1. Descarga el archivo de la versión.
2. Descomprime la carpeta completa.
3. Abre `MiCochePorDentro.exe`.

No copies únicamente el `.exe`: necesita los demás archivos de su carpeta. El ordenador de destino no necesitará Python ni Node.js.

Windows puede mostrar un aviso de SmartScreen mientras el programa no tenga firma digital. Comprueba que la descarga proceda del repositorio oficial.

## Instalación desde el código fuente

Necesitas:

- Windows 10/11 de 64 bits.
- Python 3.11 de 64 bits.
- Node.js 20 y npm.
- Aproximadamente 3 GB libres durante la instalación.

Abre PowerShell en la carpeta del proyecto y ejecuta:

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

Para abrirla:

```powershell
.\start.ps1
```

También puedes hacer doble clic en `Iniciar_App.bat`.

Si PowerShell bloquea el script, permite su ejecución solo para esa ventana:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\start.ps1
```

## Primera apertura

1. Selecciona el idioma.
2. Elige **Modo guiado** si es tu primera vez.
3. Pulsa **Añadir vehículo**.
4. Introduce como mínimo marca, modelo, año y tipo de motor.

La instalación pública comienza con el garaje vacío. Tus vehículos y sesiones no se guardan dentro de la carpeta del proyecto, sino en:

```text
%LOCALAPPDATA%\MiCochePorDentro
```

Por eso puedes actualizar el programa sin perderlos, siempre que no borres esa carpeta.

## Conectar el adaptador

1. Con el coche detenido, conecta el adaptador al puerto OBD-II.
2. Conecta el USB al ordenador y espera a que aparezca el puerto COM.
3. Pon el contacto; arranca únicamente si la prueba lo pide.
4. Cierra otros programas de diagnosis que estén usando el adaptador.
5. Selecciona el coche y el puerto recomendado.
6. Pulsa **Conectar OBD**.

## Problemas habituales

**No aparece el adaptador:** revisa el Administrador de dispositivos, el controlador, el cable y el puerto USB.

**El adaptador aparece pero la ECU no responde:** pon el contacto, comprueba el COM y cierra VCDS, FORScan, Torque u otros programas OBD.

**Faltan datos:** `--` no significa avería. Puede indicar que la ECU no ofrece esa señal o que el coche necesita compatibilidad avanzada.

Para compilar y verificar un paquete de publicación consulta la [guía técnica de compilación](informacion_tecnica/compilacion_y_pruebas/DESKTOP_BUILD.md).
