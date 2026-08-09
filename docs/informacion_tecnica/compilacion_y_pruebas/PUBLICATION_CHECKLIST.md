# Lista de preparación para la publicación

## Ya realizado en la copia pública

- Separar la copia pública de la carpeta privada.
- Excluir bases de datos, telemetría, variables de entorno, registros y compilaciones.
- Hacer que una instalación nueva arranque sin vehículos personales.
- Añadir instrucciones iniciales de instalación y privacidad.
- Compilar la interfaz desde una instalación limpia de npm.
- Ejecutar la suite aislada de los datos privados: 108 pruebas superadas.
- Corregir el reconocimiento OEM de nombres habituales como `Passat B6` sin depender de IDs precargados.
- Crear las dos guías principales: instalación/primer uso e importación avanzada con IA.
- Crear un entorno Python 3.11 desde cero y corregir el rango incompatible de MCP 2.0.
- Generar y superar el smoke test del ejecutable con un garaje nuevo vacío.

## Pendiente antes de GitHub

- Revisar en un segundo ordenador que la instalación y los controladores OBD se comportan igual.
- Validar la conexión física con un adaptador OBD real; durante la preparación solo estaba disponible un puerto Intel AMT no OBD.
- Actualizar de forma controlada Next.js y ECharts; la auditoría actual conserva vulnerabilidades que requieren cambios incompatibles y no deben corregirse con `--force` sin pruebas.
- Preparar una captura de ejemplo anonimizada o datos simulados.
- Elegir una licencia.
- Revisar nombre, descripción, iconos y capturas del proyecto.
- Generar un ejecutable limpio y probarlo en un equipo o usuario de Windows sin datos previos.
- Inicializar Git local, revisar el primer commit y conectar el remoto solo con autorización.

## Regla para nuevos vehículos y PIDs propietarios

1. Añadir el vehículo desde el Garaje.
2. Confirmar el protocolo y la centralita con comandos de solo lectura.
3. Registrar una sesión breve y conservar las respuestas brutas necesarias para depuración, sin VIN ni datos personales.
4. Mapear cada señal con documentación o evidencia reproducible.
5. Validar unidades, escala, rango y comportamiento en distintas condiciones.
6. Ocultar las señales que la ECU no ofrezca o que no hayan sido verificadas.
7. Añadir pruebas automatizadas antes de incorporar el perfil al proyecto.
