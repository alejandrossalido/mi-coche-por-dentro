import React, { useState, useEffect } from 'react';
import { Activity, AlertCircle } from 'lucide-react';

interface Monitor {
  mid: string;
  tid: string;
  name: string;
  value: number;
  min: number;
  max: number;
  unit: string;
  passed: boolean;
  description: string;
}

interface Mode06PanelProps {
  vehicleId: string;
}

export const Mode06Panel: React.FC<Mode06PanelProps> = ({ vehicleId }) => {
  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const fetchMonitors = async () => {
    if (!vehicleId) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/vehicles/${vehicleId}/mode06`);
      if (res.ok) {
        const json = await res.json();
        setMonitors(json.monitors || []);
        setMessage(json.message || '');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMonitors();
  }, [vehicleId]);

  return (
    <div className="race-panel">
      <div className="race-panel__header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Activity size={20} color="#c7ff35" />
          <h3 className="race-panel__title">
            Diagnóstico a bordo en Modo 06
          </h3>
        </div>
        <button
          onClick={fetchMonitors}
          disabled={loading || !vehicleId}
          className="race-button race-button--connect"
        >
          {loading ? 'Leyendo Modo 06…' : 'Actualizar monitores'}
        </button>
      </div>

      {message && monitors.length === 0 && (
        <div className="empty-evidence">
          <AlertCircle size={22} />
          <div><strong>Sin lectura verificable</strong><p>{message}</p></div>
        </div>
      )}
      {message && monitors.length > 0 && (
        <p style={{ color: '#94a3b8', marginBottom: '1rem' }}>{message}</p>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
        {monitors.map((m, i) => (
          <div key={`${m.mid}-${m.tid}-${i}`} style={{
            backgroundColor: '#0f172a',
            borderRadius: '8px',
            padding: '1rem',
            borderLeft: `4px solid ${m.passed ? '#10b981' : '#f43f5e'}`
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#f8fafc' }}>
                MID {m.mid} · TID {m.tid} · {m.name}
              </span>
              <span style={{ fontSize: '0.75rem', color: m.passed ? '#10b981' : '#f43f5e', fontWeight: 700 }}>
                {m.passed ? 'CORRECTO' : 'FUERA DE LÍMITES'}
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.5rem' }}>{m.description}</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#cbd5e1', fontWeight: 600 }}>
              <span>Valor: {m.value} {m.unit}</span>
              <span>Límites: [{m.min} - {m.max}]</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
