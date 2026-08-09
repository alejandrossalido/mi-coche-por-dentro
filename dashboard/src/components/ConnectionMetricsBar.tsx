import React from 'react';
import { Activity, Clock3, Cpu, Radio, ShieldCheck, Zap } from 'lucide-react';

interface ConnectionMetricsProps {
  adapterState: string;
  port?: string;
  protocol?: string;
  latencyMs?: number;
  sampleRateHz?: number;
  successRatePct?: number;
  ecuVoltage?: number;
}

export const ConnectionMetricsBar: React.FC<ConnectionMetricsProps> = ({
  adapterState,
  port = 'Sin puerto verificado',
  protocol = 'Protocolo pendiente',
  latencyMs,
  sampleRateHz,
  successRatePct,
  ecuVoltage
}) => {
  const isConnected = adapterState === 'VEHICLE_CONNECTED' || adapterState === 'CAPTURING';
  const metrics = [
    { label: 'PUERTO OBD', value: port, icon: Radio, color: isConnected ? '#c7ff35' : '#ffca28', wide: true },
    { label: 'PROTOCOLO DE LA ECU', value: protocol, icon: Cpu, color: '#00dcff', wide: true },
    { label: 'LATENCIA DEL BUS', value: latencyMs ? `${latencyMs} ms` : '--', icon: Clock3, color: '#ff2e9f' },
    { label: 'FRECUENCIA DE MUESTREO', value: sampleRateHz ? `${sampleRateHz} Hz` : '--', icon: Activity, color: '#c7ff35' },
    { label: 'LECTURAS CORRECTAS', value: typeof successRatePct === 'number' ? `${successRatePct}%` : '--', icon: ShieldCheck, color: '#c7ff35' },
    { label: 'TENSIÓN OBD / ECU', value: ecuVoltage ? `${ecuVoltage} V` : '--', icon: Zap, color: '#ff8a1f' }
  ];

  return (
    <section className="metrics-rack" aria-label="Estado del enlace OBD">
      <div className="metrics-rack__label">
        <span>MONITOR DEL BUS</span>
        <small>DATOS EN DIRECTO</small>
      </div>
      <div className="metrics-rack__grid">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <div className={`metric-cell${metric.wide ? ' metric-cell--wide' : ''}`} key={metric.label}>
              <Icon size={15} style={{ color: metric.color }} />
              <div>
                <small>{metric.label}</small>
                <strong style={{ color: metric.color }}>{metric.value}</strong>
              </div>
            </div>
          );
        })}
      </div>

      <style jsx>{`
        .metrics-rack {
          display: grid;
          grid-template-columns: 105px 1fr;
          margin-bottom: .8rem;
          border: 1px solid #35353b;
          background: #09090b;
          box-shadow: inset 0 1px #222, 0 7px 20px rgba(0,0,0,.28);
        }
        .metrics-rack__label {
          display: grid;
          place-content: center;
          padding: .75rem;
          color: #0a0a0a;
          background: linear-gradient(135deg, #ff8a1f, #e23c00);
          clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
          font: 900 .68rem "Lucida Console", monospace;
          letter-spacing: .04em;
        }
        .metrics-rack__label small {
          margin-top: .18rem;
          color: rgba(0,0,0,.62);
          font-size: .48rem;
        }
        .metrics-rack__grid {
          display: grid;
          grid-template-columns: 1.1fr 1.65fr repeat(4, minmax(105px, .75fr));
        }
        .metric-cell {
          min-width: 0;
          display: flex;
          align-items: center;
          gap: .45rem;
          padding: .63rem .72rem;
          border-left: 1px solid #28282d;
          background: linear-gradient(180deg, #131317, #09090b);
        }
        .metric-cell small {
          display: block;
          margin-bottom: .18rem;
          color: #5f5f66;
          font: 700 .48rem "Lucida Console", monospace;
          letter-spacing: .08em;
        }
        .metric-cell strong {
          display: block;
          overflow: hidden;
          font: 700 .61rem "Lucida Console", monospace;
          text-overflow: ellipsis;
          text-shadow: 0 0 8px currentColor;
          white-space: nowrap;
        }
        @media (max-width: 1150px) {
          .metrics-rack { grid-template-columns: 1fr; }
          .metrics-rack__label { display: none; }
          .metrics-rack__grid { grid-template-columns: repeat(3, 1fr); }
        }
        @media (max-width: 700px) {
          .metrics-rack__grid { grid-template-columns: repeat(2, 1fr); }
          .metric-cell { min-height: 57px; }
        }
      `}</style>
    </section>
  );
};
