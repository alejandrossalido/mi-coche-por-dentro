import React from 'react';
import { CheckCircle2, ShieldAlert } from 'lucide-react';
import { dtcDescriptionLabel, dtcStatusLabel } from '@/lib/telemetryLabels';

interface Dtc {
  code: string;
  status: string;
  description: string;
}

interface DtcPanelProps {
  dtcs: Dtc[];
  onScanDtc: () => void;
  loading?: boolean;
}

export const DtcPanel: React.FC<DtcPanelProps> = ({ dtcs, onScanDtc, loading = false }) => {
  return (
    <section className="race-panel">
      <div className="race-panel__header">
        <h3 className="race-panel__title">
          <ShieldAlert size={17} color="#ffca28" />
          Memoria de averías de la ECU // códigos DTC
        </h3>
        <button onClick={onScanDtc} disabled={loading} className="race-button race-button--connect">
          {loading ? 'Leyendo el bus…' : 'Buscar averías'}
        </button>
      </div>

      {dtcs.length === 0 ? (
        <div className="system-ok">
          <CheckCircle2 size={17} />
          <span>NO HAY AVERÍAS GUARDADAS NI PENDIENTES // SISTEMA SIN DTC</span>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '.55rem' }}>
          {dtcs.map((dtc, index) => (
            <div className="dtc-row" key={`${dtc.code}-${index}`}>
              <div>
                <strong style={{ color: '#ff334f', fontFamily: 'var(--mono-font)', marginRight: '.7rem' }}>
                  {dtc.code}
                </strong>
                <span style={{ color: '#d5d2cb', fontSize: '.78rem' }}>{dtcDescriptionLabel(dtc.code, dtc.description)}</span>
              </div>
              <span style={{ color: '#99979a', fontFamily: 'var(--mono-font)', fontSize: '.62rem' }}>
                {dtcStatusLabel(dtc.status).toUpperCase()}
              </span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
