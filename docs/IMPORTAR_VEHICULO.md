# Añadir o integrar un vehículo

Existen dos formas. La primera sirve para empezar inmediatamente; la segunda permite obtener datos más específicos del modelo.

## 1. Añadirlo al garaje

Abre **Garaje → Añadir vehículo** e introduce marca, modelo, año y tipo de motor. La aplicación probará automáticamente los datos OBD-II estándar que responda el coche. No requiere programación ni inteligencia artificial.

## 2. Crear compatibilidad avanzada con un agente

Algunos datos —inyección, turbo, EGR, DPF, regeneraciones o métricas propias del fabricante— no son universales. Para incorporarlos, un agente de programación debe:

1. identificar con precisión la variante, motor y ECU;
2. investigar manuales, documentación técnica y PDF fiables;
3. encontrar y verificar los identificadores, fórmulas y unidades;
4. adaptar el proyecto y añadir pruebas;
5. confirmar los resultados con una captura real del coche.

El agente debe intentar catalogar **todas** las métricas posibles del vehículo, no solo las que considere más interesantes. Las que consiga demostrar aparecerán como confirmadas; las demás permanecerán en el inventario como pendientes, condicionales, no disponibles, no aplicables o inaccesibles. Que una métrica no pueda leerse no bloquea la importación y nunca se sustituye por un valor inventado.

Utiliza un agente potente con acceso al repositorio, Internet y lectura de PDF; por ejemplo, **Codex con GPT-5.6 Sol**, o una herramienta equivalente. No basta con un chat que no pueda inspeccionar y modificar el proyecto.

### Qué debe indicar el usuario

Normalmente basta con una línea:

```text
Marca, modelo/generación, año, combustible, motor o cilindrada, potencia y mercado si se conoce.
```

Ejemplo de formato:

```text
Marca Modelo, generación X, 2018, diésel 2.0 de 110 kW, Europa.
```

Si conoces el código de motor o la referencia de ECU, añádelos. Si no, el agente debe investigarlos y pedir únicamente el dato que realmente necesite para distinguir variantes.

### Prompt preparado

Copia el siguiente archivo completo en el agente y cambia la línea `MI VEHÍCULO`:

**[Prompt maestro para integrar un vehículo](informacion_tecnica/agentes/PROMPT_IMPORTAR_VEHICULO_CON_IA.md)**

El prompt le indica cómo buscar documentación, analizar PDF, trabajar en modo de solo lectura, modificar el código y preparar una prueba segura.

## Importante

No se puede garantizar que cualquier ECU entregue todas las señales. La integración correcta muestra únicamente datos comprobados en los relojes de diagnóstico, pero conserva en **Garaje → Todas las métricas investigadas** el catálogo completo y el motivo exacto de cada ausencia.
