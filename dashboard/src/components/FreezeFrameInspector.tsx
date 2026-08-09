import React from 'react';
import { Camera, AlertOctagon } from 'lucide-react';

interface FreezeFrameParam {
  parameter: string;
  value: number;
  unit: string;
}

interface FreezeFrameProps {
  dtcCode?: string;
  freezeFrameParams?: FreezeFrameParam[];
}

export const FreezeFrameInspector: React.FC<FreezeFrameProps> = ({
  dtcCode = 'P0171',
  freezeFrameParams = []
}) => {
  return (
    <div style={{
      backgroundColor: '#1e293b',
      borderRadius: '12px',
      padding: '1.25rem',
      border: '1px solid #f43f5e',
      marginBottom: '1.5rem'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <Camera size={20} color="#f43f5e" />
        <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
          Fotograma congelado de la avería ({dtcCode})
        </h3>
      </div>
      <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1rem' }}>
        Valores capturados por la ECU en el instante en que se registró la avería.
      </p>

      {freezeFrameParams.length === 0 ? (
        <div style={{ backgroundColor: '#0f172a', padding: '0.8rem', borderRadius: '6px', color: '#fbbf24', fontSize: '0.82rem' }}>
          La ECU no ha proporcionado un fotograma congelado verificable para este código. No se muestran valores de ejemplo.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
          {freezeFrameParams.map((p, idx) => (
            <div key={idx} style={{ backgroundColor: '#0f172a', padding: '0.6rem 0.8rem', borderRadius: '6px' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block' }}>{p.parameter}</span>
              <span style={{ fontSize: '1rem', fontWeight: 800, color: '#f43f5e' }}>
                {p.value} <span style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>{p.unit}</span>
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
