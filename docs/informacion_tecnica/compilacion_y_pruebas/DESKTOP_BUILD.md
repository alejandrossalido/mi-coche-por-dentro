# Compilación de escritorio para Windows

## Requisitos de compilación

- Windows 10/11 de 64 bits.
- Node.js y npm para exportar el dashboard.
- El entorno `.venv` con `requirements.txt` instalado.

El equipo de destino no necesita Python ni Node.js. La distribución elegida es
PyInstaller `onedir`, porque evita la extracción temporal y reduce los fallos de
inicio con FastAPI, PyArrow, Polars y PyWebView.

## Compilar y probar

Desde PowerShell, en la raíz del proyecto:

```powershell
.\scripts\build_windows.ps1
.\scripts\smoke_test_windows.ps1
```

El paquete resultante está en:

```text
dist\MiCochePorDentro\
```

Debe copiarse la carpeta completa. El ejecutable es
`dist\MiCochePorDentro\MiCochePorDentro.exe`.

El proceso de compilación también incluye `Crear_Acceso_Directo.bat` y su
script auxiliar. El usuario puede ejecutarlo desde la carpeta descomprimida
para crear en el escritorio un acceso directo al ejecutable real.

Los datos modificables no se guardan en el paquete. Se conservan entre
actualizaciones en:

```text
%LOCALAPPDATA%\MiCochePorDentro\
```

La aplicación escucha únicamente en `127.0.0.1`. Intenta el puerto 8000 y elige
otro puerto local libre cuando está ocupado.

## Actualizaciones e instalación

Para actualizar una copia portátil, cierre la aplicación y sustituya la carpeta
del programa. No elimine `%LOCALAPPDATA%\MiCochePorDentro`.

El ejecutable no está firmado digitalmente. Windows SmartScreen puede mostrar
una advertencia hasta que se use un certificado de firma de código válido.

## Artefactos de publicación

La compilación genera un ZIP versionado en `dist` y su archivo `.sha256`. El
paquete incluye obligatoriamente `LICENSE`, `README.md` e `INSTALACION.md`;
nunca debe publicarse una distribución sin esos avisos y sin verificar el hash.

Antes de crear el ZIP, el proceso rechaza bases de datos, telemetría, archivos
`.env` y registros, y arranca el ejecutable con un perfil temporal cuyo garaje
debe estar vacío. `scripts/verify_public_release.ps1` permite repetir solo la
comprobación de limpieza.
