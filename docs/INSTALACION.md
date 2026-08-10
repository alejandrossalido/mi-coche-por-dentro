# Instalación y apertura

## Sistemas compatibles

La versión actual está preparada y probada para **Windows 10 y Windows 11 de 64 bits**. No es exclusiva de Windows 11.

Linux y macOS todavía no están soportados como producto terminado. Parte del código podría adaptarse, pero faltan un instalador, rutas de datos, ventana de escritorio y conexión OBD validados para esos sistemas.

## Opción más sencilla: carpeta y acceso directo

Cuando haya una versión en **GitHub Releases**:

1. Descarga y descomprime la carpeta completa donde quieras conservarla.
2. Abre la carpeta y haz doble clic en `Crear_Acceso_Directo.bat`.
3. Aparecerá **Mi Coche por Dentro** en el escritorio.
4. A partir de entonces, abre la aplicación haciendo doble clic en ese acceso directo.

No necesita Python, Node.js ni utilizar la terminal. No copies únicamente `MiCochePorDentro.exe`: el programa necesita toda su carpeta.

El acceso directo recuerda la ubicación elegida. Si después mueves la carpeta, vuelve a ejecutar `Crear_Acceso_Directo.bat` desde la nueva ubicación.

Windows puede mostrar un aviso de SmartScreen mientras el programa no tenga firma digital. Comprueba que la descarga proceda del repositorio oficial.

## Desde el código, también sin escribir comandos

Si has descargado el código del repositorio:

1. Guarda la carpeta en una ubicación permanente y sencilla, por ejemplo el Escritorio o Documentos.
2. Comprueba que tienes Python 3.11 y Node.js 20 o posterior.
3. Haz doble clic en `Instalar_MiCochePorDentro.bat`.
4. El instalador preparará las dependencias, compilará la interfaz y creará el acceso directo del escritorio.

La primera instalación puede tardar varios minutos. Después se abre desde **Mi Coche por Dentro** en el escritorio o haciendo doble clic en `Iniciar_App.bat` dentro de la carpeta.

## Programas necesarios para instalar desde el código

Solo hacen falta:

- **Python 3.11 de 64 bits**.
- **Node.js 20 o posterior**, que ya incluye npm.
- Aproximadamente 3 GB libres durante la instalación.

Abre PowerShell y utiliza únicamente el comando del programa que te falte:

```powershell
winget install -e --id Python.Python.3.11
winget install -e --id OpenJS.NodeJS.LTS
```

Estos identificadores se han comprobado en el catálogo de `winget`. Si tu Windows no incluye `winget`, descarga Python 3.11 desde [python.org](https://www.python.org/downloads/) y Node.js LTS desde [nodejs.org](https://nodejs.org/).

Después cierra y vuelve a abrir la carpeta antes de ejecutar el instalador. Git solo es necesario si quieres clonar el repositorio mediante comandos; si descargaste el ZIP de GitHub, no lo necesitas.

Para comprobar lo instalado:

```powershell
py -3.11 --version
node --version
npm --version
```

## Instalación manual desde PowerShell

Esta alternativa hace lo mismo que `Instalar_MiCochePorDentro.bat`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Set-Location dashboard
npm ci
npm run build
Set-Location ..

Copy-Item .env.example .env
.\scripts\create_desktop_shortcut.ps1
```

También puedes abrirla sin crear el acceso directo:

```powershell
.\start.ps1
```

## Primera apertura

1. Selecciona el idioma.
2. Elige **Modo guiado** si es tu primera vez.
3. Pulsa **Añadir vehículo**.
4. Introduce como mínimo marca, modelo, año y tipo de motor.

La instalación pública comienza con el garaje vacío. Tus vehículos y sesiones se guardan fuera de la carpeta del programa:

```text
%LOCALAPPDATA%\MiCochePorDentro
```

Puedes actualizar o sustituir la carpeta de la aplicación sin perderlos. No borres la ruta anterior si quieres conservar tus datos.

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

Para crear y verificar un paquete de publicación consulta la [guía técnica de compilación](informacion_tecnica/compilacion_y_pruebas/DESKTOP_BUILD.md).
