import { getActiveLanguage } from '@/lib/i18n';

const PID_LABELS: Record<string, string> = {
  RPM: 'Revoluciones del motor (RPM)',
  SPEED: 'Velocidad del vehículo',
  ENGINE_LOAD: 'Carga calculada del motor',
  THROTTLE_POS: 'Posición del acelerador',
  THROTTLE_ACTUATOR: 'Apertura ordenada de la mariposa',
  ACCELERATOR_POS_D: 'Posición del pedal del acelerador D',
  ACCELERATOR_POS_E: 'Posición del pedal del acelerador E',
  RELATIVE_ACCEL_POS: 'Posición relativa del pedal del acelerador',
  RUN_TIME: 'Tiempo de funcionamiento',
  COOLANT_TEMP: 'Temperatura del refrigerante',
  INTAKE_TEMP: 'Temperatura del aire de admisión',
  OIL_TEMP: 'Temperatura del aceite',
  AMBIANT_AIR_TEMP: 'Temperatura ambiente',
  CATALYST_TEMP_B1S1: 'Temperatura del catalizador B1S1',
  CATALYST_TEMP_B2S1: 'Temperatura del catalizador B2S1',
  CATALYST_TEMP_B1S2: 'Temperatura del catalizador B1S2',
  CATALYST_TEMP_B2S2: 'Temperatura del catalizador B2S2',
  MAF: 'Caudal de aire (MAF)',
  INTAKE_PRESSURE: 'Presión del colector (MAP)',
  BAROMETRIC_PRESSURE: 'Presión barométrica',
  COMMANDED_EGR: 'Apertura ordenada de la EGR',
  EGR_ERROR: 'Error de posición de la EGR',
  SHORT_FUEL_TRIM_1: 'Corrección de mezcla a corto plazo (STFT)',
  LONG_FUEL_TRIM_1: 'Corrección de mezcla a largo plazo (LTFT)',
  COMMANDED_EQUIV_RATIO: 'Relación equivalente ordenada',
  FUEL_PRESSURE: 'Presión del combustible',
  FUEL_RAIL_PRESSURE_DIRECT: 'Presión relativa del rail de combustible',
  FUEL_RAIL_PRESSURE_ABS: 'Presión absoluta del rail de combustible',
  FUEL_INJECT_TIMING: 'Avance de inyección',
  FUEL_RATE: 'Caudal de combustible',
  FUEL_STATUS: 'Estado del control de combustible',
  CONTROL_MODULE_VOLTAGE: 'Tensión del módulo de control',
  ELM_VOLTAGE: 'Tensión de alimentación del adaptador OBD',
  VAG_OIL_TEMP: 'Temperatura del aceite (Volkswagen)',
  VAG_AMBIENT_TEMP: 'Temperatura ambiente (Volkswagen)',
  VAG_RADIATOR_OUTLET_TEMP: 'Refrigerante a la salida del radiador',
  VAG_COOLING_FAN_COMMAND: 'Mando del ventilador del radiador',
  VAG_ALTERNATOR_LOAD: 'Carga del alternador',
  VAG_CAMSHAFT_SPEED: 'Velocidad del árbol de levas',
  VAG_EXHAUST_TEMP_1: 'Temperatura de escape 1',
  VAG_EXHAUST_TEMP_2: 'Temperatura de escape 2',
  VAG_BAROMETRIC_PRESSURE: 'Presión barométrica (Volkswagen)',
  VAG_ACCELERATOR_POSITION: 'Posición del pedal (Volkswagen)',
  VAG_EGR_COMMAND: 'EGR ordenada (Volkswagen)',
  VAG_EGR_ACTUAL: 'EGR real (Volkswagen)',
  VAG_EGR_DUTY_CYCLE: 'Mando de la EGR',
  VAG_AIR_MASS_ACTUAL: 'Masa de aire real por ciclo',
  VAG_RAIL_PRESSURE_REQUESTED: 'Presión del rail solicitada',
  VAG_RAIL_PRESSURE_ACTUAL: 'Presión del rail real',
  VAG_BOOST_PRESSURE_REQUESTED: 'Presión de turbo solicitada',
  VAG_BOOST_PRESSURE_ACTUAL: 'Presión de turbo real',
  VAG_INJECTION_TIMING: 'Avance de inyección (Volkswagen)',
  VAG_INJECTION_DURATION: 'Duración de inyección',
  VAG_INJECTION_DURATION_2: 'Duración de inyección (bloque 4)',
  VAG_TORSION_VALUE: 'Torsión de la distribución',
  VAG_FUEL_TEMP: 'Temperatura del combustible',
  VAG_FUEL_RATE: 'Caudal de combustible (Volkswagen)',
  VAG_ENGINE_TORQUE: 'Par calculado del motor',
  VAG_DRIVER_TORQUE_REQUEST: 'Par solicitado por el conductor',
  VAG_INJECTION_QUANTITY: 'Cantidad de inyección',
  VAG_INJECTOR_DEVIATION_1: 'Corrección del inyector 1',
  VAG_INJECTOR_DEVIATION_2: 'Corrección del inyector 2',
  VAG_INJECTOR_DEVIATION_3: 'Corrección del inyector 3',
  VAG_INJECTOR_DEVIATION_4: 'Corrección del inyector 4',
  VAG_INJECTOR_STATUS_1: 'Estado del inyector 1',
  VAG_INJECTOR_STATUS_2: 'Estado del inyector 2',
  VAG_INJECTOR_STATUS_3: 'Estado del inyector 3',
  VAG_INJECTOR_STATUS_4: 'Estado del inyector 4',
  VAG_INJECTOR_SWITCH_TIME_1: 'Desviación de conmutación del inyector 1',
  VAG_INJECTOR_SWITCH_TIME_2: 'Desviación de conmutación del inyector 2',
  VAG_INJECTOR_SWITCH_TIME_3: 'Desviación de conmutación del inyector 3',
  VAG_INJECTOR_SWITCH_TIME_4: 'Desviación de conmutación del inyector 4',
  VAG_DPF_SOOT_CALCULATED: 'Hollín calculado del DPF',
  VAG_DPF_SOOT_MEASURED: 'Hollín medido del DPF',
  VAG_DPF_SOOT_PERCENT: 'Carga de hollín del DPF',
  VAG_DPF_ASH_MASS: 'Masa de ceniza del DPF',
  VAG_DPF_DIFFERENTIAL_PRESSURE: 'Presión diferencial del DPF',
  VAG_DPF_DISTANCE_SINCE_REGEN: 'Distancia desde la última regeneración',
  VAG_DPF_TIME_SINCE_REGEN: 'Tiempo desde la última regeneración',
  VAG_DPF_REGEN_STATUS: 'Estado de regeneración del DPF',
  VAG_ECU_VOLTAGE: 'Tensión medida por la ECU Volkswagen'
};

const PID_LABELS_LOCALIZED: Record<'en' | 'it' | 'de', Record<string, string>> = {
  en: {
    RPM: 'Engine speed (RPM)', SPEED: 'Vehicle speed', ENGINE_LOAD: 'Calculated engine load', THROTTLE_POS: 'Throttle position',
    THROTTLE_ACTUATOR: 'Commanded throttle actuator', ACCELERATOR_POS_D: 'Accelerator pedal position D', ACCELERATOR_POS_E: 'Accelerator pedal position E',
    RELATIVE_ACCEL_POS: 'Relative accelerator pedal position', RUN_TIME: 'Engine run time', COOLANT_TEMP: 'Engine coolant temperature',
    INTAKE_TEMP: 'Intake air temperature', OIL_TEMP: 'Engine oil temperature', AMBIANT_AIR_TEMP: 'Ambient air temperature',
    CATALYST_TEMP_B1S1: 'Catalyst temperature B1S1', CATALYST_TEMP_B2S1: 'Catalyst temperature B2S1',
    CATALYST_TEMP_B1S2: 'Catalyst temperature B1S2', CATALYST_TEMP_B2S2: 'Catalyst temperature B2S2', MAF: 'Air flow (MAF)',
    INTAKE_PRESSURE: 'Intake manifold pressure (MAP)', BAROMETRIC_PRESSURE: 'Barometric pressure', COMMANDED_EGR: 'Commanded EGR opening',
    EGR_ERROR: 'EGR position error', SHORT_FUEL_TRIM_1: 'Short-term fuel trim (STFT)', LONG_FUEL_TRIM_1: 'Long-term fuel trim (LTFT)',
    COMMANDED_EQUIV_RATIO: 'Commanded equivalence ratio', FUEL_PRESSURE: 'Fuel pressure', FUEL_RAIL_PRESSURE_DIRECT: 'Relative fuel rail pressure',
    FUEL_RAIL_PRESSURE_ABS: 'Absolute fuel rail pressure', FUEL_INJECT_TIMING: 'Injection timing', FUEL_RATE: 'Fuel flow rate',
    FUEL_STATUS: 'Fuel control status', CONTROL_MODULE_VOLTAGE: 'Control module voltage', ELM_VOLTAGE: 'OBD adapter supply voltage',
    VAG_OIL_TEMP: 'Oil temperature (Volkswagen)', VAG_AMBIENT_TEMP: 'Ambient temperature (Volkswagen)', VAG_RADIATOR_OUTLET_TEMP: 'Radiator outlet coolant temperature', VAG_COOLING_FAN_COMMAND: 'Radiator fan command', VAG_ALTERNATOR_LOAD: 'Alternator load', VAG_CAMSHAFT_SPEED: 'Camshaft speed', VAG_EXHAUST_TEMP_1: 'Exhaust temperature 1',
    VAG_EXHAUST_TEMP_2: 'Exhaust temperature 2', VAG_BAROMETRIC_PRESSURE: 'Barometric pressure (Volkswagen)',
    VAG_ACCELERATOR_POSITION: 'Pedal position (Volkswagen)', VAG_EGR_COMMAND: 'Commanded EGR (Volkswagen)', VAG_EGR_ACTUAL: 'Actual EGR (Volkswagen)',
    VAG_EGR_DUTY_CYCLE: 'EGR duty command', VAG_AIR_MASS_ACTUAL: 'Actual air mass per stroke', VAG_RAIL_PRESSURE_REQUESTED: 'Requested rail pressure',
    VAG_RAIL_PRESSURE_ACTUAL: 'Actual rail pressure', VAG_BOOST_PRESSURE_REQUESTED: 'Requested boost pressure', VAG_BOOST_PRESSURE_ACTUAL: 'Actual boost pressure',
    VAG_INJECTION_TIMING: 'Injection timing (Volkswagen)', VAG_INJECTION_DURATION: 'Injection duration', VAG_INJECTION_DURATION_2: 'Injection duration (block 4)',
    VAG_TORSION_VALUE: 'Camshaft torsion value', VAG_FUEL_TEMP: 'Fuel temperature', VAG_FUEL_RATE: 'Fuel flow rate (Volkswagen)',
    VAG_ENGINE_TORQUE: 'Calculated engine torque', VAG_DRIVER_TORQUE_REQUEST: 'Driver requested torque', VAG_INJECTION_QUANTITY: 'Injection quantity',
    VAG_INJECTOR_DEVIATION_1: 'Injector correction 1', VAG_INJECTOR_DEVIATION_2: 'Injector correction 2', VAG_INJECTOR_DEVIATION_3: 'Injector correction 3',
    VAG_INJECTOR_DEVIATION_4: 'Injector correction 4', VAG_INJECTOR_STATUS_1: 'Injector status 1', VAG_INJECTOR_STATUS_2: 'Injector status 2',
    VAG_INJECTOR_STATUS_3: 'Injector status 3', VAG_INJECTOR_STATUS_4: 'Injector status 4', VAG_INJECTOR_SWITCH_TIME_1: 'Injector switch-time deviation 1',
    VAG_INJECTOR_SWITCH_TIME_2: 'Injector switch-time deviation 2', VAG_INJECTOR_SWITCH_TIME_3: 'Injector switch-time deviation 3',
    VAG_INJECTOR_SWITCH_TIME_4: 'Injector switch-time deviation 4', VAG_DPF_SOOT_CALCULATED: 'Calculated DPF soot mass',
    VAG_DPF_SOOT_MEASURED: 'Measured DPF soot mass', VAG_DPF_SOOT_PERCENT: 'DPF soot load', VAG_DPF_ASH_MASS: 'DPF ash mass',
    VAG_DPF_DIFFERENTIAL_PRESSURE: 'DPF differential pressure', VAG_DPF_DISTANCE_SINCE_REGEN: 'Distance since last regeneration',
    VAG_DPF_TIME_SINCE_REGEN: 'Time since last regeneration', VAG_DPF_REGEN_STATUS: 'DPF regeneration status', VAG_ECU_VOLTAGE: 'Voltage measured by Volkswagen ECU'
  },
  it: {
    RPM: 'Regime motore (RPM)', SPEED: 'Velocità veicolo', ENGINE_LOAD: 'Carico motore calcolato', THROTTLE_POS: 'Posizione farfalla',
    THROTTLE_ACTUATOR: 'Comando attuatore farfalla', ACCELERATOR_POS_D: 'Posizione pedale acceleratore D', ACCELERATOR_POS_E: 'Posizione pedale acceleratore E',
    RELATIVE_ACCEL_POS: 'Posizione relativa pedale acceleratore', RUN_TIME: 'Tempo di funzionamento motore', COOLANT_TEMP: 'Temperatura liquido refrigerante',
    INTAKE_TEMP: 'Temperatura aria aspirata', OIL_TEMP: 'Temperatura olio motore', AMBIANT_AIR_TEMP: 'Temperatura ambiente',
    CATALYST_TEMP_B1S1: 'Temperatura catalizzatore B1S1', CATALYST_TEMP_B2S1: 'Temperatura catalizzatore B2S1',
    CATALYST_TEMP_B1S2: 'Temperatura catalizzatore B1S2', CATALYST_TEMP_B2S2: 'Temperatura catalizzatore B2S2', MAF: 'Portata aria (MAF)',
    INTAKE_PRESSURE: 'Pressione collettore aspirazione (MAP)', BAROMETRIC_PRESSURE: 'Pressione barometrica', COMMANDED_EGR: 'Apertura EGR comandata',
    EGR_ERROR: 'Errore posizione EGR', SHORT_FUEL_TRIM_1: 'Correzione carburante breve (STFT)', LONG_FUEL_TRIM_1: 'Correzione carburante lunga (LTFT)',
    COMMANDED_EQUIV_RATIO: 'Rapporto equivalente comandato', FUEL_PRESSURE: 'Pressione carburante', FUEL_RAIL_PRESSURE_DIRECT: 'Pressione rail relativa',
    FUEL_RAIL_PRESSURE_ABS: 'Pressione rail assoluta', FUEL_INJECT_TIMING: 'Anticipo iniezione', FUEL_RATE: 'Portata carburante',
    FUEL_STATUS: 'Stato controllo carburante', CONTROL_MODULE_VOLTAGE: 'Tensione modulo di controllo', ELM_VOLTAGE: 'Tensione alimentazione adattatore OBD',
    VAG_OIL_TEMP: 'Temperatura olio (Volkswagen)', VAG_AMBIENT_TEMP: 'Temperatura ambiente (Volkswagen)', VAG_RADIATOR_OUTLET_TEMP: 'Temperatura refrigerante uscita radiatore', VAG_COOLING_FAN_COMMAND: 'Comando ventola radiatore', VAG_ALTERNATOR_LOAD: 'Carico alternatore', VAG_CAMSHAFT_SPEED: 'Regime albero a camme', VAG_EXHAUST_TEMP_1: 'Temperatura scarico 1',
    VAG_EXHAUST_TEMP_2: 'Temperatura scarico 2', VAG_BAROMETRIC_PRESSURE: 'Pressione barometrica (Volkswagen)', VAG_ACCELERATOR_POSITION: 'Posizione pedale (Volkswagen)',
    VAG_EGR_COMMAND: 'EGR comandata (Volkswagen)', VAG_EGR_ACTUAL: 'EGR reale (Volkswagen)', VAG_EGR_DUTY_CYCLE: 'Comando EGR',
    VAG_AIR_MASS_ACTUAL: 'Massa aria reale per ciclo', VAG_RAIL_PRESSURE_REQUESTED: 'Pressione rail richiesta', VAG_RAIL_PRESSURE_ACTUAL: 'Pressione rail reale',
    VAG_BOOST_PRESSURE_REQUESTED: 'Pressione turbo richiesta', VAG_BOOST_PRESSURE_ACTUAL: 'Pressione turbo reale', VAG_INJECTION_TIMING: 'Anticipo iniezione (Volkswagen)',
    VAG_INJECTION_DURATION: 'Durata iniezione', VAG_INJECTION_DURATION_2: 'Durata iniezione (blocco 4)', VAG_TORSION_VALUE: 'Valore torsione albero a camme',
    VAG_FUEL_TEMP: 'Temperatura carburante', VAG_FUEL_RATE: 'Portata carburante (Volkswagen)', VAG_ENGINE_TORQUE: 'Coppia motore calcolata',
    VAG_DRIVER_TORQUE_REQUEST: 'Coppia richiesta dal conducente', VAG_INJECTION_QUANTITY: 'Quantità iniezione', VAG_INJECTOR_DEVIATION_1: 'Correzione iniettore 1',
    VAG_INJECTOR_DEVIATION_2: 'Correzione iniettore 2', VAG_INJECTOR_DEVIATION_3: 'Correzione iniettore 3', VAG_INJECTOR_DEVIATION_4: 'Correzione iniettore 4',
    VAG_INJECTOR_STATUS_1: 'Stato iniettore 1', VAG_INJECTOR_STATUS_2: 'Stato iniettore 2', VAG_INJECTOR_STATUS_3: 'Stato iniettore 3', VAG_INJECTOR_STATUS_4: 'Stato iniettore 4',
    VAG_INJECTOR_SWITCH_TIME_1: 'Deviazione commutazione iniettore 1', VAG_INJECTOR_SWITCH_TIME_2: 'Deviazione commutazione iniettore 2',
    VAG_INJECTOR_SWITCH_TIME_3: 'Deviazione commutazione iniettore 3', VAG_INJECTOR_SWITCH_TIME_4: 'Deviazione commutazione iniettore 4',
    VAG_DPF_SOOT_CALCULATED: 'Massa fuliggine DPF calcolata', VAG_DPF_SOOT_MEASURED: 'Massa fuliggine DPF misurata', VAG_DPF_SOOT_PERCENT: 'Carico fuliggine DPF',
    VAG_DPF_ASH_MASS: 'Massa ceneri DPF', VAG_DPF_DIFFERENTIAL_PRESSURE: 'Pressione differenziale DPF', VAG_DPF_DISTANCE_SINCE_REGEN: 'Distanza dall’ultima rigenerazione',
    VAG_DPF_TIME_SINCE_REGEN: 'Tempo dall’ultima rigenerazione', VAG_DPF_REGEN_STATUS: 'Stato rigenerazione DPF', VAG_ECU_VOLTAGE: 'Tensione misurata dalla ECU Volkswagen'
  },
  de: {
    RPM: 'Motordrehzahl (RPM)', SPEED: 'Fahrzeuggeschwindigkeit', ENGINE_LOAD: 'Berechnete Motorlast', THROTTLE_POS: 'Drosselklappenstellung',
    THROTTLE_ACTUATOR: 'Sollwert Drosselklappensteller', ACCELERATOR_POS_D: 'Fahrpedalstellung D', ACCELERATOR_POS_E: 'Fahrpedalstellung E',
    RELATIVE_ACCEL_POS: 'Relative Fahrpedalstellung', RUN_TIME: 'Motorlaufzeit', COOLANT_TEMP: 'Kühlmitteltemperatur', INTAKE_TEMP: 'Ansauglufttemperatur',
    OIL_TEMP: 'Motoröltemperatur', AMBIANT_AIR_TEMP: 'Außentemperatur', CATALYST_TEMP_B1S1: 'Katalysatortemperatur B1S1',
    CATALYST_TEMP_B2S1: 'Katalysatortemperatur B2S1', CATALYST_TEMP_B1S2: 'Katalysatortemperatur B1S2', CATALYST_TEMP_B2S2: 'Katalysatortemperatur B2S2',
    MAF: 'Luftmassenstrom (MAF)', INTAKE_PRESSURE: 'Saugrohrdruck (MAP)', BAROMETRIC_PRESSURE: 'Umgebungsdruck', COMMANDED_EGR: 'AGR-Sollöffnung',
    EGR_ERROR: 'AGR-Positionsabweichung', SHORT_FUEL_TRIM_1: 'Kurzzeit-Gemischkorrektur (STFT)', LONG_FUEL_TRIM_1: 'Langzeit-Gemischkorrektur (LTFT)',
    COMMANDED_EQUIV_RATIO: 'Soll-Äquivalenzverhältnis', FUEL_PRESSURE: 'Kraftstoffdruck', FUEL_RAIL_PRESSURE_DIRECT: 'Relativer Raildruck',
    FUEL_RAIL_PRESSURE_ABS: 'Absoluter Raildruck', FUEL_INJECT_TIMING: 'Einspritzbeginn', FUEL_RATE: 'Kraftstoffdurchfluss', FUEL_STATUS: 'Kraftstoffregelstatus',
    CONTROL_MODULE_VOLTAGE: 'Steuergerätespannung', ELM_VOLTAGE: 'Versorgungsspannung des OBD-Adapters', VAG_OIL_TEMP: 'Öltemperatur (Volkswagen)',
    VAG_AMBIENT_TEMP: 'Außentemperatur (Volkswagen)', VAG_RADIATOR_OUTLET_TEMP: 'Kühlmitteltemperatur am Kühlerausgang', VAG_COOLING_FAN_COMMAND: 'Kühlerlüfter-Ansteuerung', VAG_ALTERNATOR_LOAD: 'Generatorlast', VAG_CAMSHAFT_SPEED: 'Nockenwellendrehzahl', VAG_EXHAUST_TEMP_1: 'Abgastemperatur 1', VAG_EXHAUST_TEMP_2: 'Abgastemperatur 2',
    VAG_BAROMETRIC_PRESSURE: 'Umgebungsdruck (Volkswagen)', VAG_ACCELERATOR_POSITION: 'Pedalstellung (Volkswagen)', VAG_EGR_COMMAND: 'AGR-Sollwert (Volkswagen)',
    VAG_EGR_ACTUAL: 'AGR-Istwert (Volkswagen)', VAG_EGR_DUTY_CYCLE: 'AGR-Ansteuerung', VAG_AIR_MASS_ACTUAL: 'Luftmasse Ist pro Hub',
    VAG_RAIL_PRESSURE_REQUESTED: 'Raildruck Soll', VAG_RAIL_PRESSURE_ACTUAL: 'Raildruck Ist', VAG_BOOST_PRESSURE_REQUESTED: 'Ladedruck Soll',
    VAG_BOOST_PRESSURE_ACTUAL: 'Ladedruck Ist', VAG_INJECTION_TIMING: 'Einspritzbeginn (Volkswagen)', VAG_INJECTION_DURATION: 'Einspritzdauer',
    VAG_INJECTION_DURATION_2: 'Einspritzdauer (Block 4)', VAG_TORSION_VALUE: 'Nockenwellen-Torsionswert', VAG_FUEL_TEMP: 'Kraftstofftemperatur',
    VAG_FUEL_RATE: 'Kraftstoffdurchfluss (Volkswagen)', VAG_ENGINE_TORQUE: 'Berechnetes Motordrehmoment', VAG_DRIVER_TORQUE_REQUEST: 'Fahrerwunschmoment',
    VAG_INJECTION_QUANTITY: 'Einspritzmenge', VAG_INJECTOR_DEVIATION_1: 'Injektorkorrektur 1', VAG_INJECTOR_DEVIATION_2: 'Injektorkorrektur 2',
    VAG_INJECTOR_DEVIATION_3: 'Injektorkorrektur 3', VAG_INJECTOR_DEVIATION_4: 'Injektorkorrektur 4', VAG_INJECTOR_STATUS_1: 'Injektorstatus 1',
    VAG_INJECTOR_STATUS_2: 'Injektorstatus 2', VAG_INJECTOR_STATUS_3: 'Injektorstatus 3', VAG_INJECTOR_STATUS_4: 'Injektorstatus 4',
    VAG_INJECTOR_SWITCH_TIME_1: 'Schaltzeitabweichung Injektor 1', VAG_INJECTOR_SWITCH_TIME_2: 'Schaltzeitabweichung Injektor 2',
    VAG_INJECTOR_SWITCH_TIME_3: 'Schaltzeitabweichung Injektor 3', VAG_INJECTOR_SWITCH_TIME_4: 'Schaltzeitabweichung Injektor 4',
    VAG_DPF_SOOT_CALCULATED: 'Berechnete DPF-Rußmasse', VAG_DPF_SOOT_MEASURED: 'Gemessene DPF-Rußmasse', VAG_DPF_SOOT_PERCENT: 'DPF-Rußbeladung',
    VAG_DPF_ASH_MASS: 'DPF-Aschemasse', VAG_DPF_DIFFERENTIAL_PRESSURE: 'DPF-Differenzdruck', VAG_DPF_DISTANCE_SINCE_REGEN: 'Strecke seit letzter Regeneration',
    VAG_DPF_TIME_SINCE_REGEN: 'Zeit seit letzter Regeneration', VAG_DPF_REGEN_STATUS: 'DPF-Regenerationsstatus', VAG_ECU_VOLTAGE: 'Von Volkswagen-ECU gemessene Spannung'
  }
};

const MONITOR_LABELS: Record<string, string> = {
  misfire: 'Fallos de combustión',
  'fuel system': 'Sistema de combustible',
  components: 'Componentes integrales',
  catalyst: 'Catalizador',
  'heated catalyst': 'Catalizador calentado',
  'evaporative system': 'Sistema evaporativo',
  'secondary air system': 'Sistema de aire secundario',
  'oxygen sensor': 'Sensor de oxígeno',
  'oxygen sensor heater': 'Calentador del sensor de oxígeno',
  'egr/vvt system': 'Sistema EGR o distribución variable',
  'nmhc catalyst': 'Catalizador de hidrocarburos no metánicos',
  'nox/scr aftertreatment': 'Postratamiento de NOx/SCR',
  'boost pressure': 'Presión de sobrealimentación',
  'exhaust gas sensor': 'Sensor de gases de escape',
  'pm filter': 'Filtro de partículas'
};

export const telemetryLabel = (pid: string): string => {
  const language = getActiveLanguage();
  if (language !== 'es') return PID_LABELS_LOCALIZED[language]?.[pid] || PID_LABELS[pid] || pid;
  return PID_LABELS[pid] || pid;
};

const METRIC_WORDS: Record<'es' | 'en' | 'it' | 'de', Record<string, string>> = {
  es: {
    ENGINE: 'motor', SPEED: 'velocidad', LOAD: 'carga', CALCULATED: 'calculada', DRIVER: 'conductor', REQUEST: 'solicitud', REQUESTED: 'solicitada', TORQUE: 'par', SELECTED: 'seleccionada', GEAR: 'marcha', STATE: 'estado', CAMSHAFT: 'árbol de levas', CAM: 'árbol de levas', CRANK: 'cigüeñal', SYNC: 'sincronización', OIL: 'aceite', PRESSURE: 'presión', MISFIRE: 'fallos de combustión', COUNT: 'recuento', TOTAL: 'total', CLUTCH: 'embrague', POSITION: 'posición', COOLANT: 'refrigerante', TEMP: 'temperatura', TEMPERATURE: 'temperatura', INTAKE: 'admisión', AIR: 'aire', AMBIANT: 'ambiente', AMBIENT: 'ambiente', FUEL: 'combustible', RADIATOR: 'radiador', OUTLET: 'salida', TRANSMISSION: 'transmisión', CHARGE: 'carga', COOLING: 'refrigeración', FAN: 'ventilador', COMMAND: 'mando', COMMANDED: 'ordenada', MAF: 'MAF', BAROMETRIC: 'barométrica', THROTTLE: 'mariposa', BOOST: 'turbo', ACTUAL: 'real', ACTUATOR: 'actuador', EGR: 'EGR', SWIRL: 'turbulencia', FLAP: 'mariposa', RATE: 'caudal', RAIL: 'rail', INJECTION: 'inyección', QUANTITY: 'cantidad', DURATION: 'duración', INJECT: 'inyección', TIMING: 'avance', EQUIV: 'equivalente', RATIO: 'relación', SHORT: 'corta', LONG: 'larga', TRIM: 'corrección', INJECTOR: 'inyector', CORRECTION: 'corrección', EXHAUST: 'escape', PRE: 'antes', POST: 'después', TURBO: 'turbo', DPF: 'DPF', GPF: 'GPF', DIFFERENTIAL: 'diferencial', SOOT: 'hollín', MEASURED: 'medida', ASH: 'ceniza', MASS: 'masa', REGEN: 'regeneración', DISTANCE: 'distancia', SINCE: 'desde', TIME: 'tiempo', NOX: 'NOx', UPSTREAM: 'antes', DOWNSTREAM: 'después', ADBLUE: 'AdBlue', LEVEL: 'nivel', SCR: 'SCR', DOSING: 'dosificación', CONTROL: 'control', MODULE: 'módulo', VOLTAGE: 'tensión', ELM: 'adaptador OBD', ALTERNATOR: 'alternador', CURRENT: 'corriente', BATTERY: 'batería', SOC: 'estado de carga', SOH: 'estado de salud', STARTER: 'arranque', CAN: 'CAN', ABS: 'ABS', ERROR: 'error', SENSOR: 'sensor', OXYGEN: 'oxígeno', STATUS: 'estado'
  },
  en: {
    ENGINE: 'engine', SPEED: 'speed', LOAD: 'load', CALCULATED: 'calculated', DRIVER: 'driver', REQUEST: 'request', REQUESTED: 'requested', TORQUE: 'torque', SELECTED: 'selected', GEAR: 'gear', STATE: 'state', CAMSHAFT: 'camshaft', CAM: 'camshaft', CRANK: 'crankshaft', SYNC: 'synchronisation', OIL: 'oil', PRESSURE: 'pressure', MISFIRE: 'misfire', COUNT: 'count', TOTAL: 'total', CLUTCH: 'clutch', POSITION: 'position', COOLANT: 'coolant', TEMP: 'temperature', TEMPERATURE: 'temperature', INTAKE: 'intake', AIR: 'air', AMBIANT: 'ambient', AMBIENT: 'ambient', FUEL: 'fuel', RADIATOR: 'radiator', OUTLET: 'outlet', TRANSMISSION: 'transmission', CHARGE: 'charge', COOLING: 'cooling', FAN: 'fan', COMMAND: 'command', COMMANDED: 'commanded', MAF: 'MAF', BAROMETRIC: 'barometric', THROTTLE: 'throttle', BOOST: 'boost', ACTUAL: 'actual', ACTUATOR: 'actuator', EGR: 'EGR', SWIRL: 'swirl', FLAP: 'flap', RATE: 'rate', RAIL: 'rail', INJECTION: 'injection', QUANTITY: 'quantity', DURATION: 'duration', INJECT: 'injection', TIMING: 'timing', EQUIV: 'equivalence', RATIO: 'ratio', SHORT: 'short-term', LONG: 'long-term', TRIM: 'trim', INJECTOR: 'injector', CORRECTION: 'correction', EXHAUST: 'exhaust', PRE: 'pre', POST: 'post', TURBO: 'turbo', DPF: 'DPF', GPF: 'GPF', DIFFERENTIAL: 'differential', SOOT: 'soot', MEASURED: 'measured', ASH: 'ash', MASS: 'mass', REGEN: 'regeneration', DISTANCE: 'distance', SINCE: 'since', TIME: 'time', NOX: 'NOx', UPSTREAM: 'upstream', DOWNSTREAM: 'downstream', ADBLUE: 'AdBlue', LEVEL: 'level', SCR: 'SCR', DOSING: 'dosing', CONTROL: 'control', MODULE: 'module', VOLTAGE: 'voltage', ELM: 'OBD adapter', ALTERNATOR: 'alternator', CURRENT: 'current', BATTERY: 'battery', SOC: 'state of charge', SOH: 'state of health', STARTER: 'starting', CAN: 'CAN', ABS: 'ABS', ERROR: 'error', SENSOR: 'sensor', OXYGEN: 'oxygen', STATUS: 'status'
  },
  it: {
    ENGINE: 'motore', SPEED: 'velocità', LOAD: 'carico', CALCULATED: 'calcolato', DRIVER: 'conducente', REQUEST: 'richiesta', REQUESTED: 'richiesta', TORQUE: 'coppia', SELECTED: 'selezionata', GEAR: 'marcia', STATE: 'stato', CAMSHAFT: 'albero a camme', CAM: 'albero a camme', CRANK: 'albero motore', SYNC: 'sincronizzazione', OIL: 'olio', PRESSURE: 'pressione', MISFIRE: 'mancate accensioni', COUNT: 'conteggio', TOTAL: 'totale', CLUTCH: 'frizione', POSITION: 'posizione', COOLANT: 'refrigerante', TEMP: 'temperatura', TEMPERATURE: 'temperatura', INTAKE: 'aspirazione', AIR: 'aria', AMBIANT: 'ambiente', AMBIENT: 'ambiente', FUEL: 'carburante', RADIATOR: 'radiatore', OUTLET: 'uscita', TRANSMISSION: 'trasmissione', CHARGE: 'carica', COOLING: 'raffreddamento', FAN: 'ventola', COMMAND: 'comando', COMMANDED: 'comandata', MAF: 'MAF', BAROMETRIC: 'barometrica', THROTTLE: 'farfalla', BOOST: 'turbo', ACTUAL: 'reale', ACTUATOR: 'attuatore', EGR: 'EGR', SWIRL: 'turbolenza', FLAP: 'farfalla', RATE: 'portata', RAIL: 'rail', INJECTION: 'iniezione', QUANTITY: 'quantità', DURATION: 'durata', INJECT: 'iniezione', TIMING: 'anticipo', EQUIV: 'equivalente', RATIO: 'rapporto', SHORT: 'breve', LONG: 'lunga', TRIM: 'correzione', INJECTOR: 'iniettore', CORRECTION: 'correzione', EXHAUST: 'scarico', PRE: 'prima', POST: 'dopo', TURBO: 'turbo', DPF: 'DPF', GPF: 'GPF', DIFFERENTIAL: 'differenziale', SOOT: 'fuliggine', MEASURED: 'misurata', ASH: 'cenere', MASS: 'massa', REGEN: 'rigenerazione', DISTANCE: 'distanza', SINCE: 'dalla', TIME: 'tempo', NOX: 'NOx', UPSTREAM: 'a monte', DOWNSTREAM: 'a valle', ADBLUE: 'AdBlue', LEVEL: 'livello', SCR: 'SCR', DOSING: 'dosaggio', CONTROL: 'controllo', MODULE: 'modulo', VOLTAGE: 'tensione', ELM: 'adattatore OBD', ALTERNATOR: 'alternatore', CURRENT: 'corrente', BATTERY: 'batteria', SOC: 'stato di carica', SOH: 'stato di salute', STARTER: 'avviamento', CAN: 'CAN', ABS: 'ABS', ERROR: 'errore', SENSOR: 'sensore', OXYGEN: 'ossigeno', STATUS: 'stato'
  },
  de: {
    ENGINE: 'Motor', SPEED: 'Geschwindigkeit', LOAD: 'Last', CALCULATED: 'berechnet', DRIVER: 'Fahrer', REQUEST: 'Anforderung', REQUESTED: 'Soll', TORQUE: 'Drehmoment', SELECTED: 'gewählt', GEAR: 'Gang', STATE: 'Status', CAMSHAFT: 'Nockenwelle', CAM: 'Nockenwelle', CRANK: 'Kurbelwelle', SYNC: 'Synchronisation', OIL: 'Öl', PRESSURE: 'Druck', MISFIRE: 'Verbrennungsaussetzer', COUNT: 'Anzahl', TOTAL: 'gesamt', CLUTCH: 'Kupplung', POSITION: 'Position', COOLANT: 'Kühlmittel', TEMP: 'Temperatur', TEMPERATURE: 'Temperatur', INTAKE: 'Ansaugung', AIR: 'Luft', AMBIANT: 'Umgebung', AMBIENT: 'Umgebung', FUEL: 'Kraftstoff', RADIATOR: 'Kühler', OUTLET: 'Ausgang', TRANSMISSION: 'Getriebe', CHARGE: 'Ladung', COOLING: 'Kühlung', FAN: 'Lüfter', COMMAND: 'Ansteuerung', COMMANDED: 'Soll', MAF: 'Luftmasse', BAROMETRIC: 'Umgebungsdruck', THROTTLE: 'Drosselklappe', BOOST: 'Ladedruck', ACTUAL: 'Ist', ACTUATOR: 'Steller', EGR: 'AGR', SWIRL: 'Drall', FLAP: 'Klappe', RATE: 'Durchfluss', RAIL: 'Rail', INJECTION: 'Einspritzung', QUANTITY: 'Menge', DURATION: 'Dauer', INJECT: 'Einspritzung', TIMING: 'Beginn', EQUIV: 'Äquivalenz', RATIO: 'Verhältnis', SHORT: 'Kurzzeit', LONG: 'Langzeit', TRIM: 'Korrektur', INJECTOR: 'Injektor', CORRECTION: 'Korrektur', EXHAUST: 'Abgas', PRE: 'vor', POST: 'nach', TURBO: 'Turbolader', DPF: 'DPF', GPF: 'OPF', DIFFERENTIAL: 'Differenz', SOOT: 'Ruß', MEASURED: 'gemessen', ASH: 'Asche', MASS: 'Masse', REGEN: 'Regeneration', DISTANCE: 'Strecke', SINCE: 'seit', TIME: 'Zeit', NOX: 'NOx', UPSTREAM: 'vor', DOWNSTREAM: 'nach', ADBLUE: 'AdBlue', LEVEL: 'Füllstand', SCR: 'SCR', DOSING: 'Dosierung', CONTROL: 'Steuerung', MODULE: 'Steuergerät', VOLTAGE: 'Spannung', ELM: 'OBD-Adapter', ALTERNATOR: 'Generator', CURRENT: 'Strom', BATTERY: 'Batterie', SOC: 'Ladezustand', SOH: 'Gesundheitszustand', STARTER: 'Start', CAN: 'CAN', ABS: 'ABS', ERROR: 'Abweichung', SENSOR: 'Sensor', OXYGEN: 'Sauerstoff', STATUS: 'Status'
  }
};

/** Localise every catalog card, including future OEM candidates.
 * Known signals use curated wording. Unknown signals are derived from their
 * stable identifier, so an English library description never leaks into a
 * Spanish, Italian or German interface.
 */
export const localizedMetricLabel = (pid: string, catalogLabel?: string): string => {
  const language = getActiveLanguage();
  const curated = language === 'es' ? PID_LABELS[pid] : PID_LABELS_LOCALIZED[language]?.[pid];
  if (curated) return curated;
  // OEM/VAG providers use Spanish as their canonical authored label.  Generic
  // python-OBD descriptions are English, so unknown standard names are always
  // localised from the stable PID identifier instead of leaking that text.
  if (language === 'es' && /^(OEM|VAG)_/.test(pid) && catalogLabel) return catalogLabel;
  const words = String(pid || '')
    .replace(/^(OEM|VAG)_/, '')
    .split('_')
    .filter(Boolean)
    .map((word) => METRIC_WORDS[language][word] || (/^B\dS\d$/.test(word) ? word : word.toLowerCase()));
  const result = words.join(' ').trim();
  return result ? result.charAt(0).toUpperCase() + result.slice(1) : pid;
};

export const monitorLabel = (name: string): string => {
  const normalized = String(name || '').trim().toLowerCase();
  const localized: Record<'en' | 'it' | 'de', Record<string, string>> = {
    en: { misfire: 'Misfire', 'fuel system': 'Fuel system', components: 'Comprehensive components', catalyst: 'Catalyst', 'heated catalyst': 'Heated catalyst', 'evaporative system': 'Evaporative system', 'secondary air system': 'Secondary air system', 'oxygen sensor': 'Oxygen sensor', 'oxygen sensor heater': 'Oxygen sensor heater', 'egr/vvt system': 'EGR or VVT system', 'nmhc catalyst': 'NMHC catalyst', 'nox/scr aftertreatment': 'NOx/SCR aftertreatment', 'boost pressure': 'Boost pressure', 'exhaust gas sensor': 'Exhaust gas sensor', 'pm filter': 'Particulate filter' },
    it: { misfire: 'Mancate accensioni', 'fuel system': 'Sistema carburante', components: 'Componenti completi', catalyst: 'Catalizzatore', 'heated catalyst': 'Catalizzatore riscaldato', 'evaporative system': 'Sistema evaporativo', 'secondary air system': 'Sistema aria secondaria', 'oxygen sensor': 'Sensore ossigeno', 'oxygen sensor heater': 'Riscaldatore sensore ossigeno', 'egr/vvt system': 'Sistema EGR o VVT', 'nmhc catalyst': 'Catalizzatore NMHC', 'nox/scr aftertreatment': 'Post-trattamento NOx/SCR', 'boost pressure': 'Pressione sovralimentazione', 'exhaust gas sensor': 'Sensore gas di scarico', 'pm filter': 'Filtro antiparticolato' },
    de: { misfire: 'Verbrennungsaussetzer', 'fuel system': 'Kraftstoffsystem', components: 'Umfassende Komponenten', catalyst: 'Katalysator', 'heated catalyst': 'Beheizter Katalysator', 'evaporative system': 'Verdunstungssystem', 'secondary air system': 'Sekundärluftsystem', 'oxygen sensor': 'Sauerstoffsensor', 'oxygen sensor heater': 'Sauerstoffsensor-Heizung', 'egr/vvt system': 'AGR- oder VVT-System', 'nmhc catalyst': 'NMHC-Katalysator', 'nox/scr aftertreatment': 'NOx-/SCR-Nachbehandlung', 'boost pressure': 'Ladedruck', 'exhaust gas sensor': 'Abgassensor', 'pm filter': 'Partikelfilter' }
  };
  const language = getActiveLanguage();
  if (language !== 'es') return localized[language][normalized] || MONITOR_LABELS[normalized] || name;
  return MONITOR_LABELS[normalized] || name;
};

export const dtcStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    confirmed: 'Confirmado',
    pending: 'Pendiente',
    permanent: 'Permanente'
  };
  const localized = {
    en: { confirmed: 'Confirmed', pending: 'Pending', permanent: 'Permanent', fallback: 'Recorded' },
    it: { confirmed: 'Confermato', pending: 'In attesa', permanent: 'Permanente', fallback: 'Registrato' },
    de: { confirmed: 'Bestätigt', pending: 'Ausstehend', permanent: 'Permanent', fallback: 'Erfasst' }
  };
  const language = getActiveLanguage();
  const normalized = String(status || '').toLowerCase();
  if (language !== 'es') return localized[language][normalized as 'confirmed' | 'pending' | 'permanent'] || localized[language].fallback;
  return labels[normalized] || 'Registrado';
};

export const dtcDescriptionLabel = (code: string, description?: string): string => {
  const descriptions: Record<string, string> = {
    P0100: 'Fallo en el circuito del caudalímetro de aire.',
    P0101: 'Rango o funcionamiento incorrecto del caudalímetro de aire.',
    P0115: 'Fallo en el circuito del sensor de temperatura del refrigerante.',
    P0128: 'Temperatura del refrigerante inferior a la regulada por el termostato.',
    P0171: 'Mezcla demasiado pobre en el banco 1.',
    P0172: 'Mezcla demasiado rica en el banco 1.',
    P0234: 'Presión de sobrealimentación excesiva.',
    P0299: 'Presión de sobrealimentación insuficiente.',
    P0300: 'Fallos de combustión aleatorios o en varios cilindros.',
    P0301: 'Fallo de combustión detectado en el cilindro 1.',
    P0302: 'Fallo de combustión detectado en el cilindro 2.',
    P0303: 'Fallo de combustión detectado en el cilindro 3.',
    P0304: 'Fallo de combustión detectado en el cilindro 4.',
    P0400: 'Fallo en el sistema de recirculación de gases de escape.',
    P0401: 'Caudal insuficiente en la recirculación de gases de escape.',
    P0402: 'Caudal excesivo en la recirculación de gases de escape.',
    P0420: 'Eficiencia del catalizador por debajo del umbral en el banco 1.',
    P0562: 'Tensión del sistema demasiado baja.',
    P0563: 'Tensión del sistema demasiado alta.'
  };
  return descriptions[String(code || '').toUpperCase()]
    || (description && /[áéíóúñ¿¡]/i.test(description)
      ? description
      : 'Descripción específica no disponible en castellano.');
};
