'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { LineChart } from 'lucide-react';
import { telemetryLabel } from '@/lib/telemetryLabels';
import { getActiveLanguage } from '@/lib/i18n';

interface Sample {
  timestamp_monotonic: number;
  pid: string;
  value: number;
  unit?: string;
}

interface Marker {
  timestamp_offset_ms: number;
  event_type: string;
  note?: string;
}

interface TelemetryChartProps {
  samples: Sample[];
  markers?: Marker[];
  professional?: boolean;
}

const COLORS = ['#ff5a1f', '#c7ff35', '#00dcff', '#ff2e9f'];
const PRIORITY = [
  'RPM', 'SPEED', 'VAG_ACCELERATOR_POSITION', 'ENGINE_LOAD',
  'VAG_INJECTION_QUANTITY', 'VAG_FUEL_RATE', 'VAG_BOOST_PRESSURE_ACTUAL',
  'INTAKE_PRESSURE', 'MAF', 'VAG_AIR_MASS_ACTUAL', 'COOLANT_TEMP'
];
const GUIDED_SIGNALS = new Set([
  ...PRIORITY,
  'VAG_BOOST_PRESSURE_REQUESTED', 'VAG_EGR_COMMAND', 'VAG_EGR_ACTUAL',
  'VAG_EGR_DUTY_CYCLE', 'INTAKE_TEMP', 'VAG_OIL_TEMP', 'VAG_FUEL_TEMP',
  'VAG_ECU_VOLTAGE', 'VAG_TORSION_VALUE', 'VAG_INJECTION_TIMING',
  'VAG_INJECTION_DURATION', 'VAG_INJECTION_DURATION_2',
  'VAG_INJECTOR_DEVIATION_1', 'VAG_INJECTOR_DEVIATION_2',
  'VAG_INJECTOR_DEVIATION_3', 'VAG_INJECTOR_DEVIATION_4'
]);
const WIDTH = 1000;
const HEIGHT = 360;
const LEFT = 66;
const RIGHT = 22;
const TOP = 18;
const BOTTOM = 34;

const numberText = (value: number) => value.toLocaleString(
  { es: 'es-ES', en: 'en-GB', it: 'it-IT', de: 'de-DE' }[getActiveLanguage()],
  { maximumFractionDigits: 2 }
);

export const TelemetryChart: React.FC<TelemetryChartProps> = ({ samples, markers = [], professional = false }) => {
  const validSamples = useMemo(
    () => samples.filter((sample) => Number.isFinite(sample.timestamp_monotonic) && Number.isFinite(sample.value)),
    [samples]
  );
  const pids = useMemo(() => {
    const found = Array.from(new Set(validSamples.map((sample) => sample.pid)))
      .filter((pid) => professional || GUIDED_SIGNALS.has(pid));
    return found.sort((a, b) => {
      const ai = PRIORITY.indexOf(a);
      const bi = PRIORITY.indexOf(b);
      return (ai < 0 ? 999 : ai) - (bi < 0 ? 999 : bi) || telemetryLabel(a).localeCompare(telemetryLabel(b));
    });
  }, [validSamples, professional]);
  const [selected, setSelected] = useState<string[]>([]);

  useEffect(() => {
    setSelected((current) => {
      const retained = current.filter((pid) => pids.includes(pid)).slice(0, 4);
      return retained.length ? retained : pids.slice(0, Math.min(3, pids.length));
    });
  }, [pids]);

  const toggleSignal = (pid: string) => {
    setSelected((current) => {
      if (current.includes(pid)) return current.length > 1 ? current.filter((item) => item !== pid) : current;
      return current.length >= 4 ? [...current.slice(1), pid] : [...current, pid];
    });
  };

  const timeMin = validSamples.length ? Math.min(...validSamples.map((sample) => sample.timestamp_monotonic)) : 0;
  const timeMax = validSamples.length ? Math.max(...validSamples.map((sample) => sample.timestamp_monotonic)) : 0;
  const duration = Math.max(0.001, timeMax - timeMin);
  const plotWidth = WIDTH - LEFT - RIGHT;
  const plotHeight = HEIGHT - TOP - BOTTOM;
  const laneHeight = plotHeight / Math.max(1, selected.length);
  const xFor = (seconds: number) => LEFT + ((seconds - timeMin) / duration) * plotWidth;

  const series = selected.map((pid, index) => {
    const allRows = validSamples.filter((sample) => sample.pid === pid).sort((a, b) => a.timestamp_monotonic - b.timestamp_monotonic);
    const step = Math.max(1, Math.ceil(allRows.length / 600));
    const rows = allRows.filter((_, rowIndex) => rowIndex % step === 0 || rowIndex === allRows.length - 1);
    const values = rows.map((sample) => sample.value);
    const minimum = values.length ? Math.min(...values) : 0;
    const maximum = values.length ? Math.max(...values) : 0;
    const range = Math.max(0.0001, maximum - minimum);
    const laneTop = TOP + laneHeight * index + 12;
    const laneBottom = TOP + laneHeight * (index + 1) - 12;
    const points = rows.map((sample) => {
      const normalized = (sample.value - minimum) / range;
      return `${xFor(sample.timestamp_monotonic).toFixed(2)},${(laneBottom - normalized * (laneBottom - laneTop)).toFixed(2)}`;
    }).join(' ');
    return { pid, rows, minimum, maximum, unit: rows[0]?.unit || '', points, laneTop, laneBottom, color: COLORS[index] };
  });

  const visibleMarkers = markers
    .map((marker) => ({ ...marker, seconds: marker.timestamp_offset_ms / 1000 }))
    .filter((marker) => marker.seconds >= timeMin && marker.seconds <= timeMax);

  return (
    <section className="race-panel">
      <div className="race-panel__header">
        <h3 className="race-panel__title">
          <LineChart size={17} color="#00dcff" />
          Registrador multicanal // señales sincronizadas
        </h3>
        <span className="section-kicker">
          {validSamples.length} lecturas{timeMax > timeMin ? ` · ${timeMin.toFixed(1)}–${timeMax.toFixed(1)} s` : ''}
        </span>
      </div>
      {validSamples.length === 0 ? (
        <div className="chart-placeholder">Esperando el inicio de la captura // Bus de datos en reposo</div>
      ) : (
        <>
          <div className="chart-signal-picker" aria-label="Canales visibles">
            {pids.map((pid) => {
              const active = selected.includes(pid);
              const color = active ? COLORS[selected.indexOf(pid)] : '#66666e';
              return (
                <button key={pid} type="button" onClick={() => toggleSignal(pid)} className={active ? 'active' : ''} style={{ borderColor: color, color }}>
                  {telemetryLabel(pid)}
                </button>
              );
            })}
          </div>
          <div className="telemetry-svg-wrap">
            <svg role="img" aria-label="Evolución temporal de las señales seleccionadas" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} preserveAspectRatio="none">
              <rect x={LEFT} y={TOP} width={plotWidth} height={plotHeight} fill="#08080b" stroke="#303038" />
              {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
                const x = LEFT + plotWidth * ratio;
                return <line key={ratio} x1={x} x2={x} y1={TOP} y2={HEIGHT - BOTTOM} stroke="#202027" strokeDasharray="4 4" />;
              })}
              {series.map((item, index) => (
                <g key={item.pid}>
                  {index > 0 && <line x1={LEFT} x2={WIDTH - RIGHT} y1={TOP + laneHeight * index} y2={TOP + laneHeight * index} stroke="#292930" />}
                  <text x={LEFT - 8} y={item.laneTop + 3} textAnchor="end" fill={item.color} className="axis-value">{numberText(item.maximum)}</text>
                  <text x={LEFT - 8} y={item.laneBottom + 3} textAnchor="end" fill={item.color} className="axis-value">{numberText(item.minimum)}</text>
                  <text x={LEFT + 8} y={item.laneTop + 3} fill={item.color} className="series-name">{telemetryLabel(item.pid)} {item.unit ? `/ ${item.unit}` : ''}</text>
                  <polyline points={item.points} fill="none" stroke={item.color} strokeWidth="2.2" vectorEffect="non-scaling-stroke" />
                </g>
              ))}
              {visibleMarkers.map((marker, index) => {
                const x = xFor(marker.seconds);
                return (
                  <g key={`${marker.event_type}-${index}`}>
                    <line x1={x} x2={x} y1={TOP} y2={HEIGHT - BOTTOM} stroke="#ffca28" strokeWidth="1.5" strokeDasharray="5 4" />
                    <text x={Math.min(x + 5, WIDTH - 150)} y={TOP + 13} fill="#ffca28" className="marker-label">{marker.note || marker.event_type}</text>
                  </g>
                );
              })}
              {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
                <text key={ratio} x={LEFT + plotWidth * ratio} y={HEIGHT - 11} textAnchor="middle" fill="#777780" className="time-label">
                  {(timeMin + duration * ratio).toFixed(1)} s
                </text>
              ))}
            </svg>
          </div>
          <p className="chart-help">Selecciona hasta 4 canales · cada canal conserva su propia escala y comparte el mismo eje temporal</p>
        </>
      )}
      <style jsx>{`
        .chart-signal-picker { display:flex; flex-wrap:wrap; gap:7px; padding:12px 20px 0; }
        .chart-signal-picker button { background:#0a0a0d; border:1px solid #3a3a42; color:#777780; padding:6px 9px; font:700 10px/1.2 monospace; text-transform:uppercase; cursor:pointer; }
        .chart-signal-picker button.active { background:rgba(255,255,255,.045); box-shadow:0 0 10px color-mix(in srgb, currentColor 30%, transparent); }
        .telemetry-svg-wrap { height:390px; margin:8px 14px 0; overflow:hidden; }
        svg { width:100%; height:100%; display:block; }
        .axis-value, .series-name, .marker-label, .time-label { font-family:monospace; }
        .axis-value { font-size:9px; }
        .series-name { font-size:10px; font-weight:700; text-transform:uppercase; }
        .marker-label { font-size:9px; }
        .time-label { font-size:9px; }
        .chart-help { margin:-2px 20px 14px; color:#777780; font:10px/1.4 monospace; text-transform:uppercase; }
      `}</style>
    </section>
  );
};
