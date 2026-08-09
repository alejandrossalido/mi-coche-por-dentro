'use client';

import React, { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle2, RefreshCw, ShieldCheck } from 'lucide-react';
import { monitorLabel } from '@/lib/telemetryLabels';

interface ImReadinessPanelProps {
  vehicleId: string;
}

export const ImReadinessPanel: React.FC<ImReadinessPanelProps> = ({ vehicleId }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    if (!vehicleId) return;
    setLoading(true);
    try {
      const response = await fetch(`/api/vehicles/${vehicleId}/readiness`);
      const payload = await response.json();
      setData(response.ok ? payload : { available: false, message: payload.detail || 'No se pudo leer la ECU.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [vehicleId]);

  return (
    <section className="race-panel">
      <div className="race-panel__header">
        <h3 className="race-panel__title">
          <ShieldCheck size={19} color="#c7ff35" />
          Preparación real de monitores OBD para la ITV
        </h3>
        <button className="race-button" onClick={load} disabled={loading || !vehicleId}>
          <RefreshCw size={15} />
          Leer ECU
        </button>
      </div>

      {!data?.available ? (
        <div className="empty-evidence">
          <AlertCircle size={22} />
          <div>
            <strong>Sin lectura verificable</strong>
            <p>{data?.message || 'Conecta el vehículo para consultar los monitores reales.'}</p>
          </div>
        </div>
      ) : (
        <>
          <div className="readiness-summary">
            <div><span>MIL</span><strong className={data.mil ? 'bad' : 'good'}>{data.mil ? 'ENCENDIDA' : 'APAGADA'}</strong></div>
            <div><span>DTC declarados</span><strong>{data.dtc_count}</strong></div>
            <div><span>Monitores completos</span><strong>{data.monitors.filter((monitor: any) => monitor.complete).length} / {data.monitors.length}</strong></div>
          </div>
          <div className="readiness-grid">
            {data.monitors.map((monitor: any, index: number) => (
              <article key={`${monitor.name}-${index}`} className={monitor.complete ? 'ready' : 'incomplete'}>
                {monitor.complete ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                <span>{monitorLabel(monitor.name)}</span>
                <strong>{!monitor.available ? 'NO DISPONIBLE' : monitor.complete ? 'COMPLETO' : 'INCOMPLETO'}</strong>
              </article>
            ))}
          </div>
        </>
      )}
      <p className="legal-note">Esta lectura OBD no sustituye la inspección física ni garantiza superar la ITV.</p>
    </section>
  );
};
