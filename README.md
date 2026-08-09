# Mi Coche por Dentro

Aplicación de escritorio para conectar un adaptador OBD-II, ver datos reales del coche, guardar trayectos, ejecutar pruebas guiadas y generar informes comprensibles.

Es una aplicación de **solo lectura**: no codifica, no reprograma y no modifica la ECU.

## Empieza aquí

| Quiero… | Documento |
|---|---|
| Instalarla y crear un acceso directo en el escritorio | **[Instalación](docs/INSTALACION.md)** |
| Añadir o integrar mi coche | **[Importar un vehículo](docs/IMPORTAR_VEHICULO.md)** |
| Saber todo lo que ofrece | **[Qué hace la aplicación](docs/QUE_HACE_LA_APLICACION.md)** |

## En pocas palabras

1. Añade tu coche al garaje.
2. Conecta un adaptador OBD-II compatible.
3. Selecciona una prueba o inicia una captura.
4. La aplicación guarda los datos y prepara un informe.

La cantidad de información disponible depende del vehículo. RPM, velocidad o temperatura suelen utilizar OBD-II estándar; turbo, inyección, EGR o DPF pueden necesitar una integración específica.

## Compatibilidad del programa

- **Sistema soportado actualmente:** Windows 10 u 11 de 64 bits.
- **Linux y macOS:** todavía no disponen de instalación, paquete ni conexión OBD validados oficialmente.
- **Vehículos:** coches con OBD-II/EOBD; la cobertura exacta depende de la ECU y del adaptador.

## Seguridad y privacidad

- No utilices la pantalla mientras conduces.
- La aplicación no sustituye a un diagnóstico profesional.
- Los vehículos y las sesiones se guardan localmente en el ordenador.
- No es necesario introducir matrícula ni VIN completo.

## Información técnica

La arquitectura, las pruebas de publicación, los protocolos y los casos específicos —incluida la investigación del Volkswagen Passat— se conservan aparte para desarrolladores y agentes de programación:

**[Información técnica y material adicional](docs/informacion_tecnica/README.md)**

## Licencia

Publicado bajo la [PolyForm Noncommercial License 1.0.0](LICENSE): uso personal, educativo y no comercial. El uso comercial requiere permiso escrito del autor.
