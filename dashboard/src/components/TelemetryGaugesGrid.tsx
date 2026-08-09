import React, { useMemo, useState } from 'react';
import { Car, Eye, EyeOff, Factory, Fuel, Layers3, LayoutDashboard, Thermometer, Wind, Zap } from 'lucide-react';
import { Gauge } from './Gauge';
import { telemetryLabel } from '@/lib/telemetryLabels';

interface TelemetryValues {
  [key: string]: number | undefined;
}

interface PIDCapability {
  pid_name: string;
  label?: string;
  category?: string;
  unit?: string;
  status?: string;
  supported_reported?: boolean;
  supported_verified?: boolean;
}

interface TelemetryGaugesGridProps {
  values: TelemetryValues;
  capabilities?: PIDCapability[];
  powertrainType?: 'gasoline' | 'diesel' | 'hybrid' | 'phev' | 'bev';
  engineCode?: string;
  tripMetrics?: {
    available?: boolean;
    average_l_per_100km?: number;
    distance_km?: number;
    confidence?: string;
    reason?: string;
  };
}

type Category = 'motor' | 'temp' | 'intake' | 'fuel' | 'dpf' | 'elec';
type VisibilityMode = 'data' | 'all' | 'missing' | 'diagnostic';

const categoryForCapability = (item: PIDCapability): Category => {
  const text = `${item.pid_name} ${(item as any).category || ''}`.toLowerCase();
  if (text.includes('temperatur') || text.includes('refriger')) return 'temp';
  if (text.includes('admis') || text.includes('aire') || text.includes('turbo') || text.includes('egr')) return 'intake';
  if (text.includes('dpf') || text.includes('escape') || text.includes('scr') || text.includes('catal')) return 'dpf';
  if (text.includes('eléctr') || text.includes('electr') || text.includes('voltage') || text.includes('bater') || text.includes('altern')) return 'elec';
  if (text.includes('combust') || text.includes('mezcla') || text.includes('inyec') || text.includes('fuel') || text.includes('o2_')) return 'fuel';
  return 'motor';
};

const gaugeRange = (pid: string, unit = '') => {
  const normalized = unit.toLowerCase();
  if (normalized.includes('°c')) return { min: -40, max: pid.includes('EXHAUST') || pid.includes('CATALYST') ? 1000 : 160 };
  if (normalized === 'v') return { min: 0, max: 18 };
  if (normalized.includes('rpm')) return { min: 0, max: 9000 };
  if (normalized.includes('km/h')) return { min: 0, max: 340 };
  if (normalized.includes('kpa')) return { min: 0, max: 300 };
  if (normalized.includes('bar')) return { min: 0, max: 2000 };
  if (normalized.includes('mg/str')) return { min: -10, max: 1600 };
  if (normalized.includes('nm')) return { min: -100, max: 600 };
  if (normalized.includes('%')) return { min: 0, max: 100 };
  return { min: 0, max: 100 };
};

const FUEL_STATUS_LABELS: Record<number, string> = {
  0: 'Sin estado informado',
  1: 'Bucle abierto: motor frío',
  2: 'Bucle cerrado',
  4: 'Bucle abierto: carga o retención',
  8: 'Bucle abierto: fallo del sistema',
  16: 'Bucle cerrado con fallo de realimentación'
};

export const TelemetryGaugesGrid: React.FC<TelemetryGaugesGridProps> = ({
  values,
  capabilities = [],
  powertrainType,
  engineCode,
  tripMetrics
}) => {
  const [category, setCategory] = useState<Category>('motor');
  const [visibility, setVisibility] = useState<VisibilityMode>('data');
  const capabilityMap = useMemo(
    () => new Map(capabilities.map((item) => [item.pid_name, item])),
    [capabilities]
  );
  const pickValue = (...pids: string[]) => {
    for (const pid of pids) {
      const value = values[pid];
      if (typeof value === 'number' && Number.isFinite(value)) return value;
    }
    return undefined;
  };
  const statusFor = (value: number | undefined, ...pids: string[]) => {
    if (typeof value === 'number' && Number.isFinite(value)) return 'Dato real de la ECU';
    if (!capabilities.length) return 'Pendiente de comprobar';
    const matches = pids.map((pid) => capabilityMap.get(pid)).filter(Boolean) as PIDCapability[];
    if (matches.some((item) => item.supported_verified)) return 'Esperando lectura';
    if (matches.some((item) => item.status === 'unresponsive')) return 'La ECU no respondió';
    if (matches.some((item) => item.status === 'mapping_required')) return 'Pendiente de identificar en esta ECU';
    if (matches.some((item) => item.status === 'negative_response')) return 'Lectura rechazada por la ECU';
    if (matches.some((item) => item.status === 'type_mismatch')) return 'Formato distinto en esta ECU';
    if (matches.some((item) => item.status === 'not_tested')) return 'Sin comprobar';
    return 'No ofrecido por esta ECU';
  };
  const shouldShow = (...pids: string[]) => pids.some((pid) => (
    typeof values[pid] === 'number'
    || capabilityMap.get(pid)?.supported_verified
  ));

  const accelerator = pickValue('VAG_ACCELERATOR_POSITION', 'ACCELERATOR_POS_D', 'ACCELERATOR_POS_E', 'RELATIVE_ACCEL_POS');
  const oilTemperature = pickValue('VAG_OIL_TEMP', 'OIL_TEMP');
  const ambientTemperature = pickValue('VAG_AMBIENT_TEMP', 'AMBIANT_AIR_TEMP');
  const engineCodeNormalized = String(engineCode || '').toUpperCase();
  const bkpWithoutFactoryDpf = engineCodeNormalized === 'BKP';
  const calculatedMaf = typeof values.VAG_AIR_MASS_ACTUAL === 'number' && typeof values.RPM === 'number'
    ? values.VAG_AIR_MASS_ACTUAL * values.RPM / 30000
    : undefined;
  const maf = pickValue('MAF') ?? calculatedMaf;
  const manifoldPressure = pickValue('INTAKE_PRESSURE', 'VAG_BOOST_PRESSURE_ACTUAL');
  const exhaustTemperature = pickValue('VAG_EXHAUST_TEMP_1', 'VAG_EXHAUST_TEMP_2', 'CATALYST_TEMP_B1S1', 'CATALYST_TEMP_B2S1', 'CATALYST_TEMP_B1S2', 'CATALYST_TEMP_B2S2');
  const barometricPressure = pickValue('VAG_BAROMETRIC_PRESSURE', 'BAROMETRIC_PRESSURE');
  const egrCommand = pickValue('VAG_EGR_COMMAND', 'COMMANDED_EGR');
  const egrActual = pickValue('VAG_EGR_ACTUAL');
  const egrUsesAirMass = capabilityMap.get('VAG_EGR_COMMAND')?.unit?.toLowerCase().includes('mg/') || false;
  const egrUnit = egrUsesAirMass ? 'MG/STR' : '%';
  const egrMax = egrUsesAirMass ? 1500 : 100;
  const egrError = typeof egrCommand === 'number' && typeof egrActual === 'number'
    ? egrActual - egrCommand
    : pickValue('EGR_ERROR');
  const fuelPressureKpa = pickValue('FUEL_RAIL_PRESSURE_DIRECT', 'FUEL_RAIL_PRESSURE_ABS', 'FUEL_PRESSURE');
  const vagFuelPressureBar = pickValue('VAG_RAIL_PRESSURE_ACTUAL');
  const fuelPressureBar = typeof vagFuelPressureBar === 'number'
    ? vagFuelPressureBar
    : typeof fuelPressureKpa === 'number' ? fuelPressureKpa / 100 : undefined;
  const hasRailPressure = typeof vagFuelPressureBar === 'number'
    || typeof pickValue('FUEL_RAIL_PRESSURE_DIRECT', 'FUEL_RAIL_PRESSURE_ABS') === 'number';
  const moduleVoltage = pickValue('VAG_ECU_VOLTAGE', 'CONTROL_MODULE_VOLTAGE');
  const fuelRate = pickValue('VAG_FUEL_RATE', 'FUEL_RATE');
  const instantConsumption = typeof fuelRate === 'number' && typeof values.SPEED === 'number' && values.SPEED >= 5
    ? fuelRate / values.SPEED * 100
    : undefined;
  const pumpDuseCodes = ['BKP', 'BMP', 'BMN', 'BMR', 'BUY', 'BUZ'];
  const isPumpDuse = Boolean(
    pumpDuseCodes.includes(String(engineCode || '').toUpperCase())
    || capabilityMap.get('VAG_INJECTION_QUANTITY')?.supported_verified
    || capabilityMap.get('VAG_INJECTOR_DEVIATION_1')?.supported_verified
  ) && !hasRailPressure;
  const injectorStatuses = [1, 2, 3, 4]
    .map((cylinder) => values[`VAG_INJECTOR_STATUS_${cylinder}`])
    .filter((value) => typeof value === 'number' && Number.isFinite(value)) as number[];
  const injectorFaultStatuses = injectorStatuses.filter((value) => (Math.trunc(value) & (16 | 32 | 64 | 128)) !== 0);
  const injectorStatusLabel = injectorStatuses.length === 4
    ? injectorFaultStatuses.length === 0
      ? injectorStatuses.every((value) => value === 0)
        ? 'Sin fallos BIP detectados por la ECU'
        : `Sin fallos BIP // estado operativo ${injectorStatuses.join(' / ')}`
      : `Revisar estados BIP: ${injectorStatuses.join(' / ')}`
    : statusFor(undefined, 'VAG_INJECTOR_STATUS_1', 'VAG_INJECTOR_STATUS_2', 'VAG_INJECTOR_STATUS_3', 'VAG_INJECTOR_STATUS_4');

  const dpfPids = [
    'VAG_DPF_SOOT_CALCULATED', 'VAG_DPF_SOOT_MEASURED', 'VAG_DPF_SOOT_PERCENT',
    'VAG_DPF_ASH_MASS', 'VAG_DPF_DIFFERENTIAL_PRESSURE',
    'VAG_DPF_DISTANCE_SINCE_REGEN', 'VAG_DPF_TIME_SINCE_REGEN', 'VAG_DPF_REGEN_STATUS'
  ];
  const showDpfCategory = visibility !== 'diagnostic' || (!bkpWithoutFactoryDpf && dpfPids.some((pid) => shouldShow(pid)));

  const allMetricCapabilities = useMemo(() => {
    const byPid = new Map<string, PIDCapability>();
    capabilities.forEach((item) => item?.pid_name && byPid.set(item.pid_name, item));
    Object.keys(values).forEach((pid_name) => {
      if (!byPid.has(pid_name)) byPid.set(pid_name, { pid_name, supported_verified: true });
    });
    return Array.from(byPid.values());
  }, [capabilities, values]);
  const dynamicMetrics = visibility === 'diagnostic'
    ? []
    : allMetricCapabilities.filter((item) => {
        if (categoryForCapability(item) !== category) return false;
        const value = values[item.pid_name];
        const hasData = typeof value === 'number' && Number.isFinite(value);
        if (visibility === 'data') return hasData;
        if (visibility === 'missing') return !hasData;
        return true;
      });
  const categoryColors: Record<Category, string> = {
    motor: '#ff5a1f', temp: '#ffca28', intake: '#00dcff', fuel: '#ff2e9f', dpf: '#ff8a35', elec: '#c7ff35'
  };

  const categories = [
    { id: 'motor' as const, label: 'Motor / Marcha', icon: Car, color: '#ff5a1f' },
    { id: 'temp' as const, label: 'Temperaturas', icon: Thermometer, color: '#ffca28' },
    { id: 'intake' as const, label: 'Admisión / Aire', icon: Wind, color: '#00dcff' },
    { id: 'fuel' as const, label: 'Combustible / Mezcla', icon: Fuel, color: '#ff2e9f' },
    ...(showDpfCategory ? [{ id: 'dpf' as const, label: 'Escape / DPF', icon: Factory, color: '#ff8a35' }] : []),
    { id: 'elec' as const, label: 'Sistema eléctrico', icon: Zap, color: '#c7ff35' }
  ];

  return (
    <section aria-label="Instrumentación de telemetría">
      <div style={{ display: 'flex', gap: '0.45rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
        {([
          { id: 'data', label: 'Solo con datos', icon: Eye },
          { id: 'all', label: 'Todas las métricas', icon: Layers3 },
          { id: 'missing', label: 'Sin datos visibles', icon: EyeOff },
          { id: 'diagnostic', label: 'Vista de diagnóstico', icon: LayoutDashboard }
        ] as Array<{ id: VisibilityMode; label: string; icon: typeof Eye }>).map((item) => {
          const Icon = item.icon;
          return <button key={item.id} type="button" className={`sensor-tab${visibility === item.id ? ' active' : ''}`} onClick={() => setVisibility(item.id)}>
            <Icon size={14} /> {item.label}
          </button>;
        })}
      </div>
      <div className="sensor-tabs">
        <span className="section-kicker">Cuadro de instrumentos</span>
        {categories.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              className={`sensor-tab${category === item.id ? ' active' : ''}`}
              style={{ '--tab-color': item.color } as React.CSSProperties}
              onClick={() => setCategory(item.id)}
            >
              <Icon size={14} />
              {item.label}
            </button>
          );
        })}
      </div>

      <div className={`telemetry-grid${category === 'motor' ? ' telemetry-grid--motor' : ''}`}>
        {visibility === 'diagnostic' && category === 'motor' && <>
          <Gauge label="Revoluciones del motor" value={values.RPM} unit="RPM" max={9000} color="#ff5a1f" variant="hero" />
          <Gauge label="Velocidad del vehículo" value={values.SPEED} unit="KM/H" max={340} color="#c7ff35" variant="hero" />
          {shouldShow('VAG_CAMSHAFT_SPEED') && <Gauge label="Velocidad del árbol de levas" value={values.VAG_CAMSHAFT_SPEED} unit="RPM" max={4500} color="#00dcff" statusText={statusFor(values.VAG_CAMSHAFT_SPEED, 'VAG_CAMSHAFT_SPEED')} />}
          {shouldShow('VAG_ENGINE_TORQUE') && <Gauge label="Par calculado del motor" value={values.VAG_ENGINE_TORQUE} unit="NM" min={-100} max={450} color="#ff2e9f" statusText={statusFor(values.VAG_ENGINE_TORQUE, 'VAG_ENGINE_TORQUE')} />}
          {shouldShow('VAG_DRIVER_TORQUE_REQUEST') && <Gauge label="Par solicitado por el conductor" value={values.VAG_DRIVER_TORQUE_REQUEST} unit="NM" min={-100} max={450} color="#ffca28" statusText={statusFor(values.VAG_DRIVER_TORQUE_REQUEST, 'VAG_DRIVER_TORQUE_REQUEST')} />}
          {shouldShow('ENGINE_LOAD') && <Gauge label="Carga del motor" value={values.ENGINE_LOAD} unit="%" max={100} color="#ff2e9f" statusText={statusFor(values.ENGINE_LOAD, 'ENGINE_LOAD')} />}
          <Gauge label="Pedal del acelerador" value={accelerator} unit="%" max={100} color="#ffca28" statusText={statusFor(accelerator, 'VAG_ACCELERATOR_POSITION', 'ACCELERATOR_POS_D', 'ACCELERATOR_POS_E', 'RELATIVE_ACCEL_POS')} />
          {shouldShow('THROTTLE_POS') && <Gauge label="Mariposa de admisión" value={values.THROTTLE_POS} unit="%" max={100} color="#00dcff" statusText={statusFor(values.THROTTLE_POS, 'THROTTLE_POS')} />}
          {shouldShow('RUN_TIME') && <Gauge label="Tiempo de funcionamiento" value={values.RUN_TIME} unit="S" max={3600} color="#8c8c94" statusText={statusFor(values.RUN_TIME, 'RUN_TIME')} />}
        </>}

        {visibility === 'diagnostic' && category === 'temp' && <>
          <Gauge label="Refrigerante (ECT)" value={values.COOLANT_TEMP} unit="°C" max={120} color="#ffca28" />
          {shouldShow('VAG_RADIATOR_OUTLET_TEMP') && <Gauge label="Refrigerante a la salida del radiador" value={values.VAG_RADIATOR_OUTLET_TEMP} unit="°C" max={120} color="#c7ff35" statusText={statusFor(values.VAG_RADIATOR_OUTLET_TEMP, 'VAG_RADIATOR_OUTLET_TEMP')} />}
          {shouldShow('VAG_COOLING_FAN_COMMAND') && <Gauge label="Mando del ventilador del radiador" value={values.VAG_COOLING_FAN_COMMAND} unit="%" max={100} color="#ff2e9f" statusText={statusFor(values.VAG_COOLING_FAN_COMMAND, 'VAG_COOLING_FAN_COMMAND')} />}
          <Gauge label="Aire de admisión (IAT)" value={values.INTAKE_TEMP} unit="°C" max={80} color="#00dcff" />
          <Gauge label="Aceite del motor" value={oilTemperature} unit="°C" max={140} color="#ff5a1f" statusText={statusFor(oilTemperature, 'VAG_OIL_TEMP', 'OIL_TEMP')} />
          <Gauge label="Temperatura ambiente" value={ambientTemperature} unit="°C" min={-30} max={60} color="#c7ff35" statusText={statusFor(ambientTemperature, 'VAG_AMBIENT_TEMP', 'AMBIANT_AIR_TEMP')} />
          {shouldShow('VAG_EXHAUST_TEMP_1', 'VAG_EXHAUST_TEMP_2', 'CATALYST_TEMP_B1S1', 'CATALYST_TEMP_B2S1', 'CATALYST_TEMP_B1S2', 'CATALYST_TEMP_B2S2') && <Gauge label="Gases de escape" value={exhaustTemperature} unit="°C" max={900} color="#ff334f" statusText={statusFor(exhaustTemperature, 'VAG_EXHAUST_TEMP_1', 'VAG_EXHAUST_TEMP_2', 'CATALYST_TEMP_B1S1', 'CATALYST_TEMP_B2S1', 'CATALYST_TEMP_B1S2', 'CATALYST_TEMP_B2S2')} />}
        </>}

        {visibility === 'diagnostic' && category === 'intake' && <>
          <Gauge label="Caudal de aire (MAF)" value={maf} unit="G/S" max={200} color="#00dcff" statusText={typeof values.MAF === 'number' ? 'Dato real de la ECU' : typeof calculatedMaf === 'number' ? 'Calculado desde mg/str y RPM (motor 4 cilindros)' : statusFor(undefined, 'MAF', 'VAG_AIR_MASS_ACTUAL')} />
          <Gauge label="Masa de aire por ciclo" value={values.VAG_AIR_MASS_ACTUAL} unit="MG/STR" max={1600} color="#00dcff" statusText={statusFor(values.VAG_AIR_MASS_ACTUAL, 'VAG_AIR_MASS_ACTUAL')} />
          <Gauge label="Presión del colector (MAP)" value={manifoldPressure} unit="KPA" max={300} color="#ff5a1f" statusText={typeof values.INTAKE_PRESSURE === 'number' ? 'Dato OBD genérico' : typeof values.VAG_BOOST_PRESSURE_ACTUAL === 'number' ? 'Presión absoluta real del colector, medida por la ECU' : statusFor(undefined, 'INTAKE_PRESSURE', 'VAG_BOOST_PRESSURE_ACTUAL')} />
          <Gauge label="Presión barométrica" value={barometricPressure} unit="KPA" max={110} color="#c7ff35" statusText={statusFor(barometricPressure, 'VAG_BAROMETRIC_PRESSURE', 'BAROMETRIC_PRESSURE')} />
          <Gauge label="Turbo solicitado" value={values.VAG_BOOST_PRESSURE_REQUESTED} unit="KPA" max={300} color="#c7ff35" statusText={statusFor(values.VAG_BOOST_PRESSURE_REQUESTED, 'VAG_BOOST_PRESSURE_REQUESTED')} />
          <Gauge label="Turbo real" value={pickValue('VAG_BOOST_PRESSURE_ACTUAL', 'INTAKE_PRESSURE')} unit="KPA" max={300} color="#ff5a1f" statusText={statusFor(pickValue('VAG_BOOST_PRESSURE_ACTUAL', 'INTAKE_PRESSURE'), 'VAG_BOOST_PRESSURE_ACTUAL', 'INTAKE_PRESSURE')} />
          <Gauge label={egrUsesAirMass ? 'Masa de aire objetivo EGR' : 'EGR ordenada'} value={egrCommand} unit={egrUnit} max={egrMax} color="#ff2e9f" statusText={statusFor(egrCommand, 'VAG_EGR_COMMAND', 'COMMANDED_EGR')} />
          <Gauge label={egrUsesAirMass ? 'Masa de aire real EGR' : 'EGR real'} value={egrActual} unit={egrUnit} max={egrMax} color="#00dcff" statusText={statusFor(egrActual, 'VAG_EGR_ACTUAL')} />
          <Gauge label="Diferencia EGR" value={egrError} unit={egrUnit} min={-egrMax} max={egrMax} color="#ffca28" statusText={statusFor(egrError, 'VAG_EGR_ACTUAL', 'EGR_ERROR')} />
          <Gauge label="Mando de la EGR" value={values.VAG_EGR_DUTY_CYCLE} unit="%" min={0} max={100} color="#ffca28" statusText={statusFor(values.VAG_EGR_DUTY_CYCLE, 'VAG_EGR_DUTY_CYCLE')} />
        </>}

        {visibility === 'diagnostic' && category === 'fuel' && <>
          {!isPumpDuse && <Gauge label="Presión del rail real" value={fuelPressureBar} unit="BAR" max={hasRailPressure ? 2000 : 10} color="#00dcff" statusText={statusFor(fuelPressureBar, 'VAG_RAIL_PRESSURE_ACTUAL', 'FUEL_RAIL_PRESSURE_DIRECT', 'FUEL_RAIL_PRESSURE_ABS', 'FUEL_PRESSURE')} />}
          {!isPumpDuse && <Gauge label="Presión del rail solicitada" value={values.VAG_RAIL_PRESSURE_REQUESTED} unit="BAR" max={2000} color="#c7ff35" statusText={statusFor(values.VAG_RAIL_PRESSURE_REQUESTED, 'VAG_RAIL_PRESSURE_REQUESTED')} />}
          {isPumpDuse && <div className="lcd-card"><span>Sistema de inyección</span><strong>Inyector-bomba // sin rail common-rail</strong></div>}
          <Gauge label="Cantidad de inyección" value={values.VAG_INJECTION_QUANTITY} unit="MG/STR" max={100} color="#00dcff" statusText={statusFor(values.VAG_INJECTION_QUANTITY, 'VAG_INJECTION_QUANTITY')} />
          <Gauge label="Duración de inyección" value={pickValue('VAG_INJECTION_DURATION', 'VAG_INJECTION_DURATION_2')} unit="°CA" min={-5} max={40} color="#00dcff" statusText={statusFor(pickValue('VAG_INJECTION_DURATION', 'VAG_INJECTION_DURATION_2'), 'VAG_INJECTION_DURATION', 'VAG_INJECTION_DURATION_2')} />
          <Gauge label="Caudal de combustible" value={fuelRate} unit="L/H" max={40} color="#ff5a1f" statusText={statusFor(fuelRate, 'VAG_FUEL_RATE', 'FUEL_RATE')} />
          <Gauge label="Consumo instantáneo calculado" value={instantConsumption} unit="L/100KM" max={30} color="#ff5a1f" statusText={typeof instantConsumption === 'number' ? 'Calculado con caudal y velocidad de la ECU' : 'Disponible circulando por encima de 5 km/h'} />
          {tripMetrics?.available && <Gauge label="Consumo medio del trayecto" value={tripMetrics.average_l_per_100km} unit="L/100KM" max={30} color="#c7ff35" statusText={`${tripMetrics.reason || 'Promedio integrado del trayecto'}${typeof tripMetrics.distance_km === 'number' ? ` · ${tripMetrics.distance_km.toFixed(2)} km analizados` : ''}`} />}
          <Gauge label="Avance de inyección" value={pickValue('VAG_INJECTION_TIMING', 'FUEL_INJECT_TIMING')} unit="°" min={-20} max={40} color="#ffca28" statusText={statusFor(pickValue('VAG_INJECTION_TIMING', 'FUEL_INJECT_TIMING'), 'VAG_INJECTION_TIMING', 'FUEL_INJECT_TIMING')} />
          {isPumpDuse && <Gauge label="Torsión de distribución" value={values.VAG_TORSION_VALUE} unit="°CA" min={-6} max={6} color="#ffca28" statusText={statusFor(values.VAG_TORSION_VALUE, 'VAG_TORSION_VALUE')} />}
          {isPumpDuse && <Gauge label="Temperatura del combustible" value={values.VAG_FUEL_TEMP} unit="°C" min={-20} max={120} color="#c7ff35" statusText={statusFor(values.VAG_FUEL_TEMP, 'VAG_FUEL_TEMP')} />}
          {!isPumpDuse && <Gauge label="Relación equivalente ordenada" value={values.COMMANDED_EQUIV_RATIO} unit="λ" min={0.7} max={2} color="#c7ff35" statusText={statusFor(values.COMMANDED_EQUIV_RATIO, 'COMMANDED_EQUIV_RATIO')} />}
          {powertrainType !== 'diesel' && <Gauge label="Corrección corta (STFT)" value={values.SHORT_FUEL_TRIM_1} unit="%" min={-25} max={25} color="#ff2e9f" statusText={statusFor(values.SHORT_FUEL_TRIM_1, 'SHORT_FUEL_TRIM_1')} />}
          {powertrainType !== 'diesel' && <Gauge label="Corrección larga (LTFT)" value={values.LONG_FUEL_TRIM_1} unit="%" min={-25} max={25} color="#ffca28" statusText={statusFor(values.LONG_FUEL_TRIM_1, 'LONG_FUEL_TRIM_1')} />}
          {!isPumpDuse && <div className="lcd-card"><span>Estado del control de mezcla</span><strong>{typeof values.FUEL_STATUS === 'number' ? (FUEL_STATUS_LABELS[values.FUEL_STATUS] || `Estado ${values.FUEL_STATUS}`) : statusFor(undefined, 'FUEL_STATUS')}</strong></div>}
          {isPumpDuse && <div className="lcd-card"><span>Estado eléctrico / BIP de inyectores</span><strong>{injectorStatusLabel}</strong></div>}
          {powertrainType === 'diesel' && [1, 2, 3, 4].map((cylinder) => <Gauge key={cylinder} label={`Corrección del inyector ${cylinder}`} value={values[`VAG_INJECTOR_DEVIATION_${cylinder}`]} unit="MG/STR" min={-4} max={4} color="#ff2e9f" statusText={statusFor(values[`VAG_INJECTOR_DEVIATION_${cylinder}`], `VAG_INJECTOR_DEVIATION_${cylinder}`)} />)}
          {isPumpDuse && [1, 2, 3, 4].map((cylinder) => <Gauge key={`switch-${cylinder}`} label={`Desviación de conmutación ${cylinder}`} value={values[`VAG_INJECTOR_SWITCH_TIME_${cylinder}`]} unit="MS" min={0} max={0.5} color="#ff8a1f" statusText={statusFor(values[`VAG_INJECTOR_SWITCH_TIME_${cylinder}`], `VAG_INJECTOR_SWITCH_TIME_${cylinder}`)} />)}
        </>}

        {visibility === 'diagnostic' && category === 'dpf' && showDpfCategory && <>
          <Gauge label="Hollín calculado" value={values.VAG_DPF_SOOT_CALCULATED} unit="G" max={50} color="#ff8a35" statusText={statusFor(values.VAG_DPF_SOOT_CALCULATED, 'VAG_DPF_SOOT_CALCULATED')} />
          <Gauge label="Hollín medido" value={values.VAG_DPF_SOOT_MEASURED} unit="G" max={50} color="#ffca28" statusText={statusFor(values.VAG_DPF_SOOT_MEASURED, 'VAG_DPF_SOOT_MEASURED')} />
          <Gauge label="Carga de hollín" value={values.VAG_DPF_SOOT_PERCENT} unit="%" max={100} color="#ff8a35" statusText={statusFor(values.VAG_DPF_SOOT_PERCENT, 'VAG_DPF_SOOT_PERCENT')} />
          <Gauge label="Masa de ceniza" value={values.VAG_DPF_ASH_MASS} unit="G" max={100} color="#ffca28" statusText={statusFor(values.VAG_DPF_ASH_MASS, 'VAG_DPF_ASH_MASS')} />
          <Gauge label="Presión diferencial" value={values.VAG_DPF_DIFFERENTIAL_PRESSURE} unit="MBAR" max={300} color="#00dcff" statusText={statusFor(values.VAG_DPF_DIFFERENTIAL_PRESSURE, 'VAG_DPF_DIFFERENTIAL_PRESSURE')} />
          <Gauge label="Desde última regeneración" value={values.VAG_DPF_DISTANCE_SINCE_REGEN} unit="KM" max={1000} color="#c7ff35" statusText={statusFor(values.VAG_DPF_DISTANCE_SINCE_REGEN, 'VAG_DPF_DISTANCE_SINCE_REGEN')} />
          <Gauge label="Tiempo desde regeneración" value={values.VAG_DPF_TIME_SINCE_REGEN} unit="S" max={100000} color="#8c8c94" statusText={statusFor(values.VAG_DPF_TIME_SINCE_REGEN, 'VAG_DPF_TIME_SINCE_REGEN')} />
          <div className="lcd-card"><span>Estado de regeneración</span><strong>{typeof values.VAG_DPF_REGEN_STATUS === 'number' ? ((values.VAG_DPF_REGEN_STATUS & 3) ? 'Regeneración activa' : 'Regeneración inactiva') : statusFor(undefined, 'VAG_DPF_REGEN_STATUS')}</strong></div>
        </>}

        {visibility === 'diagnostic' && category === 'elec' && <>
          <Gauge label="Módulo de control" value={moduleVoltage} unit="V" min={10} max={16} color="#c7ff35" statusText={statusFor(moduleVoltage, 'VAG_ECU_VOLTAGE', 'CONTROL_MODULE_VOLTAGE')} />
          {shouldShow('VAG_ALTERNATOR_LOAD') && <Gauge label="Carga del alternador" value={values.VAG_ALTERNATOR_LOAD} unit="%" max={100} color="#ffca28" statusText={statusFor(values.VAG_ALTERNATOR_LOAD, 'VAG_ALTERNATOR_LOAD')} />}
          {shouldShow('ELM_VOLTAGE') && <Gauge label="Alimentación del adaptador OBD" value={values.ELM_VOLTAGE} unit="V" min={10} max={16} color="#00dcff" statusText={statusFor(values.ELM_VOLTAGE, 'ELM_VOLTAGE')} />}
        </>}

        {visibility !== 'diagnostic' && dynamicMetrics.map((item) => {
          const value = values[item.pid_name];
          const range = gaugeRange(item.pid_name, item.unit || '');
          return <Gauge
            key={item.pid_name}
            label={item.label || telemetryLabel(item.pid_name)}
            value={value}
            unit={(item.unit || '—').toUpperCase()}
            min={range.min}
            max={range.max}
            color={categoryColors[category]}
            statusText={statusFor(value, item.pid_name)}
          />;
        })}
        {visibility !== 'diagnostic' && dynamicMetrics.length === 0 && (
          <div className="lcd-card">
            <span>{visibility === 'data' ? 'Métricas con datos' : visibility === 'missing' ? 'Métricas sin datos visibles' : 'Métricas catalogadas'}</span>
            <strong>No hay métricas en esta categoría para el filtro seleccionado</strong>
          </div>
        )}
      </div>
    </section>
  );
};
