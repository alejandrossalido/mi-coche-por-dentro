import React from 'react';
import { ShieldCheck, AlertOctagon, CheckCircle, Clock } from 'lucide-react';

interface ReadinessPanelProps {
  milStatus: boolean;
  dtcCount: number;
  monitors: Array<{ name: string; status: 'PASSED' | 'INCOMPLETE' | 'UNSUPPORTED' }>;
}

export const EmissionsReadinessPanel: React.FC<ReadinessPanelProps> = ({
  milStatus,
  dtcCount,
  monitors
}) => {
  return (
    <div style={{
      backgroundColor: '#1e293b',
      borderRadius: '12px',
      padding: '1.5rem',
      border: '1px solid #334155',
      marginBottom: '1.5rem'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <ShieldCheck size={24} color="#10b981" />
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
              Estado OBD de emisiones antes de la ITV
            </h3>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Comprobación local de monitores del sistema de diagnóstico</span>
          </div>
        </div>

        <div style={{
          backgroundColor: milStatus || dtcCount > 0 ? '#ef4444' : '#10b981',
          color: '#ffffff',
          padding: '0.4rem 0.8rem',
          borderRadius: '6px',
          fontWeight: 800,
          fontSize: '0.85rem'
        }}>
          {milStatus || dtcCount > 0 ? '❌ ATENCIÓN: MIL O DTCs ACTIVOS' : '✅ SIN IMPEDIMENTOS OBD EVIDENTES'}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.25rem' }}>
        <div style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px' }}>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Testigo MIL (Luz Avería Cuadro)</span>
          <h4 style={{ color: milStatus ? '#ef4444' : '#10b981', fontSize: '1.2rem', marginTop: '0.2rem' }}>
            {milStatus ? 'ENCENDIDO' : 'APAGADO'}
          </h4>
        </div>
        <div style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px' }}>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Códigos DTC de Emisiones</span>
          <h4 style={{ color: dtcCount > 0 ? '#ef4444' : '#10b981', fontSize: '1.2rem', marginTop: '0.2rem' }}>
            {dtcCount} Avería(s)
          </h4>
        </div>
        <div style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px' }}>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Monitores Completados</span>
          <h4 style={{ color: '#38bdf8', fontSize: '1.2rem', marginTop: '0.2rem' }}>
            {monitors.filter(m => m.status === 'PASSED').length} / {monitors.length}
          </h4>
        </div>
      </div>

      <div style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px', borderLeft: '4px solid #f59e0b', fontSize: '0.85rem', color: '#cbd5e1' }}>
        <p style={{ margin: 0 }}>
          <strong>Aviso Legal Obligatorio:</strong> El estado OBD de emisiones refleja únicamente la información digital leída de la ECU. Esta comprobación <em>no garantiza superar la ITV</em>, ya que la inspección oficial incluye comprobaciones físicas de opacidad/gases, estado mecánico del escape e inspección visual.
        </p>
      </div>
    </div>
  );
};
