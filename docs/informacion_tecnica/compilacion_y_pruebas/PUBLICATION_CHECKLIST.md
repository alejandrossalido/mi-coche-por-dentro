# Lista de publicación

## Automatizado en cada cambio

- Suite completa de Python.
- Auditoría de vulnerabilidades de Python y npm.
- Comprobación de tipos de la interfaz.
- Cobertura de traducción ES/EN/IT/DE.
- Compilación estática de producción.
- Construcción y arranque real del ejecutable con un garaje temporal vacío.
- Rechazo automático de bases de datos, telemetría, `.env` y registros en el paquete.
- CI en Windows con permisos mínimos.
- Dependabot semanal para Python y npm.

## Verificación de cada paquete para GitHub Releases

1. Construir desde un clon limpio mediante `scripts/build_windows.ps1`.
2. Ejecutar `scripts/smoke_test_windows.ps1` con un perfil temporal y garaje vacío.
3. Comprobar el ZIP en Windows 10 u 11 de 64 bits sin Python ni Node instalados.
4. Verificar que SmartScreen identifica el origen esperado y publicar el SHA-256 del ZIP.
5. Conectar físicamente un adaptador compatible y realizar una captura corta de solo lectura.
6. Confirmar que no hay vehículos, bases de datos, telemetría, registros, `.env` ni claves dentro del paquete.
7. Crear la versión de GitHub Releases únicamente después de superar los pasos anteriores.

## Límites que deben declararse

- La cobertura depende del vehículo, ECU, protocolo y adaptador.
- Una tarjeta pendiente no equivale a una señal compatible.
- `--` significa que no existe una lectura válida en ese momento.
- El programa no sustituye a un taller ni garantiza superar una ITV.
- No utilizar la pantalla mientras se conduce.

## Nuevos vehículos y PIDs propietarios

1. Identificar de forma inequívoca variante, motor y ECU.
2. Confirmar protocolo usando exclusivamente servicios de lectura.
3. Documentar el origen de cada identificador, fórmula, unidad y rango.
4. Marcar por separado candidatos, señales anunciadas y lecturas verificadas.
5. Validar varias condiciones operativas y añadir pruebas automatizadas.
6. No publicar VIN, matrículas, telemetría personal ni documentación sin permiso.
