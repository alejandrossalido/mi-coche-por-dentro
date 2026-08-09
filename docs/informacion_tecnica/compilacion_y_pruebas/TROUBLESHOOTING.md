# Diagnóstico de la aplicación de escritorio

## La aplicación no abre

Revise el log persistente:

```text
%LOCALAPPDATA%\MiCochePorDentro\logs\app.log
```

El log registra versión, ejecutable, recursos, datos, dashboard, puerto,
migraciones, inicio de FastAPI, excepciones y cierre.

## Puerto ocupado

No es necesario liberar manualmente el puerto 8000. El launcher selecciona otro
puerto local y lo registra en `app.log`. El servidor nunca escucha en
`0.0.0.0`.

## Dashboard ausente

Copie siempre la carpeta `dist\MiCochePorDentro` completa. Si faltan
`_internal\dashboard\out` o `index.html`, `/health` falla y la interfaz no se
abre. El diálogo de error permite abrir la carpeta de logs o copiar el mensaje.

## Base de datos o permisos

La base de datos está en:

```text
%LOCALAPPDATA%\MiCochePorDentro\data\vehicle_ai.db
```

Las copias previas a migraciones se guardan en `backups`. No borre la base de
datos para resolver un error. Si está bloqueada, cierre otras instancias y
revise el log.

## Segunda instancia

Solo se permite una instancia por usuario. Una segunda apertura muestra un
mensaje y termina sin iniciar otro servidor.

## Prueba reproducible

Ejecute:

```powershell
.\scripts\smoke_test_windows.ps1 -KeepArtifacts
```

La prueba copia el paquete a una carpeta temporal, lo ejecuta con otro directorio
de trabajo, consulta `/health`, la API, el dashboard y un recurso estático, y
comprueba el cierre sin procesos huérfanos.
