# Guía de Hardware y Compatibilidad de Garaje — Mi Coche por Dentro

## 1. Elección de Hardware OBD-II / Interfaz

### 1.1. Adaptador Principal Recomendado: **Vgate vLinker FS USB V2**
* **Tipo de Conexión:** USB directo a puerto COM serie virtual (Chipset FTDI / Silicon Labs a 3.000.000 bps).
* **Chipset Interno:** MIC3322 (compatible con el juego de comandos STN2120 / STN2255 y ELM327 v2.2).
* **Precio aproximado:** ~30 € - 35 €.
* **Razones técnicas de la elección:**
  * **Estabilidad en Windows:** Elimina completamente los cortes de reconexión y retardos de la pila Bluetooth en portátiles PC.
  * **Latencia Ultrabaja (<5 ms):** Crucial para correlacionar eventos dinámicos (tirones, caídas de presión de turbo en milisegundos).
  * **Conmutación Electrónica de Buses:** Conmuta automáticamente entre HS-CAN (alta velocidad 500k) y MS-CAN (media velocidad 125k) sin conmutadores manuales.
  * **Soporte de Comandos STN (`ST...`):** Permite peticiones multi-PID en una sola trama CAN, aumentando la tasa de muestreo de ~15 PIDs/s a **60-100 PIDs/s**.
  * **Relación Calidad/Precio:** Aporta el 95% de las capacidades de adaptadores de >140 € (como OBDLink MX+) por solo ~35 €.

### 1.2. Alternativa Inalámbrica: **Vgate vLinker MC+ (Bluetooth 4.0 / BLE / 3.0)**
* **Precio:** ~40 € - 45 €.
* **Uso:** Recomendado solo si se requiere operación sin cables desde dispositivos móviles o si se prefiere evitar el cable USB.

### 1.3. Equipamiento Desaconsejado y Análisis Pragmático de Costes
* **Clones ELM327 económicos (5 € - 15 €):** Desaconsejados por tener búferes diminutos (<256 bytes), perder tramas en muestreo rápido y no soportar la extensión de comandos STN.
* **Herramientas de Taller Comercial (Autel MaxiSys 1.200 €, Ross-Tech VCDS Original 250 €):** Desaconsejadas para la fase de lectura y desarrollo del proyecto. Disparan el presupuesto innecesariamente. Con el **vLinker FS USB (35 €)** y programas de PC de libre acceso como **FORScan** (para Mazda), el usuario dispone del 100% de las capacidades necesarias sin desembolsos abultados.

---

## 2. Análisis de Compatibilidad por Vehículo del Garaje

### 2.1. Volkswagen Passat B6 2.0 TDI (2005 - 2010)
* **Motorización:** 2.0 TDI (Motores Inyector-Bomba BKP/BMP/BMR entre 2005-2007; Common Rail CBAB/CBBB a partir de 2008).
* **Protocolo:** ISO 15765-4 CAN (11-bit, 500 kbps) / KWP2000.
* **Estado de Compatibilidad OBD-II:** **Confirmado (Probable en PIDs específicos)**.
* **PIDs y Métricas Clave:**
  * Presión de admisión (MAP absoluto) y Masa de aire (MAF en g/s).
  * Temperatura de refrigerante (ECT) y temperatura de admisión (IAT).
  * Presión de Rail Common Rail (únicamente en versiones post-2008 CBBB/CBAB; no aplica a versiones Inyector-Bomba).
  * Códigos de avería DTC (Modo 03) y Freeze Frame (Modo 02).
  * Monitores de emisiones diésel (EGR, DPF, Catalizador DOC) en `I/M Readiness`.

### 2.2. Mazda 1.5 Skyactiv-D
* **Motorización:** 1.5 Diésel Euro6 de baja compresión (Motor S5-DPTS).
* **Protocolo:** HS-CAN (ISO 15765-4 500k) + MS-CAN (125k).
* **Estado de Compatibilidad OBD-II:** **Confirmado (Excelente respuesta)**.
* **PIDs y Métricas Clave:**
  * Presión de turbo (MAP) y caudalímetro (MAF).
  * Sensores de temperatura de gases de escape (EGT).
  * Presión diferencial del DPF y estado de regeneraciones.
  * Compatibilidad nativa adicional con **FORScan** a través del vLinker FS.

### 2.3. Opel Vectra C 1.9 CDTI
* **Motorización:** 1.9 CDTI 8v/16v (Motores Fiat/GM Z19DT / Z19DTH con ECU Bosch EDC16).
* **Protocolo:** ISO 15765-4 CAN (500 kbps) / KWP2000.
* **Estado de Compatibilidad OBD-II:** **Confirmado (Alta respuesta)**.
* **PIDs y Métricas Clave:**
  * MAF y MAP (medición de desviación para diagnóstico de EGR y geometría variable del turbo).
  * Presión en rampa de alta presión Common Rail.
  * Monitores de estado de emisiones.

### 2.4. Tesla Model 3 (2025 - Highland / EV 100%)
* **Motorización:** Eléctrico (Sin motor térmico ni emisiones contaminantes).
* **Estado de Compatibilidad OBD-II Genérico:** **No disponible mediante OBD-II estándar (Modo 01 ICE)**.
* **Estrategia de Integración Futura (`tesla-can` / `tesla-doip`):**
  * Requiere subsistema independiente al margen de la librería `generic-obd`.
  * Exige cable adaptador T-Harness específico verificado para la versión *Highland 2024-2025* (~20 €) para derivar el bus CAN del vehículo.
  * Captura de tramas pasivas (*Raw CAN Sniffing*) decodificadas mediante matriz DBC validada para extraer: SoC (%), SoH (%), temperatura de batería, kW de potencia y regeneración, y RPM de motores eléctricos.
