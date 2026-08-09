# ADR 0001: Uso Dual de SQLite para Metadatos y Apache Parquet para Telemetría

- **Estado:** Aprobado
- **Fecha:** 2026-07-23

## Contexto
El sistema necesita almacenar dos tipos de datos fundamentalmente distintos:
1. Metadatos relacionales estructurados (vehículos, escaneos DTC, sesiones, reparaciones, marcadores de eventos).
2. Series temporales continuas de telemetría de alta frecuencia (muestras por milisegundo de RPM, MAP, MAF, temperaturas).

## Decisión
Utilizar una arquitectura de persistencia dual:
- **SQLite** para entidades relacionales y metadatos del expediente.
- **Apache Parquet** comprimido (Snappy) por cada sesión de telemetría (`session_<id>.parquet`).

## Consecuencias
- Velocidad máxima de lectura y procesamiento vectorial de telemetría mediante Polars / PyArrow.
- Portabilidad total sin necesidad de servidores de base de datos externos (PostgreSQL/TimescaleDB).
- Archivos comprimidos de pequeño tamaño ideales para backups ZIP.
