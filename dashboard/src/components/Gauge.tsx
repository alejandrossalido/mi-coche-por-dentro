import React from 'react';

interface GaugeProps {
  label: string;
  value?: number;
  unit: string;
  min?: number;
  max?: number;
  color?: string;
  variant?: 'standard' | 'hero';
  statusText?: string;
}

export const Gauge: React.FC<GaugeProps> = ({
  label,
  value,
  unit,
  min = 0,
  max = 100,
  color = '#ff5a1f',
  variant = 'standard',
  statusText
}) => {
  const hasValue = typeof value === 'number' && Number.isFinite(value);
  const numericValue: number = hasValue ? (value as number) : min;
  const percentage = Math.min(100, Math.max(0, ((numericValue - min) / (max - min)) * 100));
  const decimals = Math.abs(numericValue) >= 100 ? 0 : 1;
  const style = {
    '--gauge-color': color,
    '--gauge-progress': `${percentage}%`,
    '--gauge-sweep': `${percentage * 0.75}%`
  } as React.CSSProperties;

  return (
    <article className={`gauge-card${variant === 'hero' ? ' gauge-card--hero' : ''}`} style={style}>
      <span className="gauge-label">{label}</span>
      {statusText && <span className="gauge-status">{statusText}</span>}

      <div className="gauge-dial">
        <div className="gauge-readout">
          <span className="gauge-value">
            {hasValue ? numericValue.toFixed(decimals) : '--'}
          </span>
          <span className="gauge-unit">{unit}</span>
        </div>
      </div>

      <div className="gauge-scale">
        <span>{min}</span>
        <span>{Math.round((min + max) / 2)}</span>
        <span>{max}</span>
      </div>
    </article>
  );
};
