import React, { useState, useEffect } from 'react';
import { Wrench, Download, Database, Usb, CheckCircle2, AlertCircle, RefreshCw, ListChecks } from 'lucide-react';

interface RepairAction {
  id: string;
  performed_at: string;
  description: string;
  notes?: string;
}

interface GaragePanelProps {
  vehicleId: string;
  vehicleName: string;
}

export const GaragePanel: React.FC<GaragePanelProps> = ({ vehicleId, vehicleName }) => {
  const [repairs, setRepairs] = useState<RepairAction[]>([]);
  const [description, setDescription] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [baseline, setBaseline] = useState<any>(null);
  const [compatibility, setCompatibility] = useState<any>(null);
  const [manufacturerData, setManufacturerData] = useState<any>(null);
  const [inventoryRunning, setInventoryRunning] = useState(false);
  const [inventoryError, setInventoryError] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('Todas');

  const fetchRepairs = async () => {
    if (!vehicleId) return;
    try {
      const [repairsResponse, baselineResponse, compatibilityResponse, manufacturerResponse] = await Promise.all([
        fetch(`/api/vehicles/${vehicleId}/repairs`),
        fetch(`/api/vehicles/${vehicleId}/baseline`),
        fetch('/api/adapter/compatibility'),
        fetch(`/api/vehicles/${vehicleId}/manufacturer-probe`, { cache: 'no-store' })
      ]);
      if (repairsResponse.ok) setRepairs(await repairsResponse.json());
      if (baselineResponse.ok) setBaseline(await baselineResponse.json());
      if (compatibilityResponse.ok) setCompatibility(await compatibilityResponse.json());
      if (manufacturerResponse.ok) setManufacturerData(await manufacturerResponse.json());
    } catch (e) {
      console.error(e);
    }
  };

  const runFullInventory = async () => {
    if (!vehicleId || inventoryRunning) return;
    setInventoryRunning(true);
    setInventoryError('');
    try {
      const response = await fetch(`/api/vehicles/${vehicleId}/manufacturer-probe`, { method: 'POST' });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || 'No se pudo completar el inventario de la ECU.');
      setManufacturerData({
        vehicle_id: vehicleId,
        applicable: true,
        last_probe: payload,
        capabilities: payload.live_signals || []
      });
    } catch (error) {
      setInventoryError(error instanceof Error ? error.message : 'No se pudo completar el inventario.');
    } finally {
      setInventoryRunning(false);
    }
  };

  const capabilities = manufacturerData?.capabilities || manufacturerData?.last_probe?.live_signals || [];
  const summary = manufacturerData?.last_probe || {};
  const categories = ['Todas', ...Array.from(new Set(capabilities.map((item: any) => item.category).filter(Boolean))) as string[]];
  const visibleCapabilities = capabilities
    .filter((item: any) => categoryFilter === 'Todas' || item.category === categoryFilter)
    .sort((a: any, b: any) => {
      const fuelA = a.category === 'Combustible, mezcla y emisiones' ? 0 : 1;
      const fuelB = b.category === 'Combustible, mezcla y emisiones' ? 0 : 1;
      return fuelA - fuelB || Number(b.supported_verified) - Number(a.supported_verified) || Number(a.group_number || 999) - Number(b.group_number || 999);
    });

  useEffect(() => {
    fetchRepairs();
  }, [vehicleId]);

  const handleAddRepair = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim() || !vehicleId) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/vehicles/${vehicleId}/repairs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description, notes })
      });
      if (res.ok) {
        setDescription('');
        setNotes('');
        fetchRepairs();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="race-panel">
      <div className="race-panel__header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Wrench size={20} color="#ffca28" />
          <div>
            <h3 className="race-panel__title">
              Expediente Técnico y Registro de Reparaciones
            </h3>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{vehicleName}</span>
          </div>
        </div>

        {vehicleId && (
          <a
            href={`/api/vehicles/${vehicleId}/export`}
            download
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              backgroundColor: '#10b981',
              color: '#0f172a',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontWeight: 800,
              textDecoration: 'none',
              fontSize: '0.85rem'
            }}
          >
            <Download size={16} /> Exportar Copia ZIP
          </a>
        )}
      </div>

      <div className="garage-insight-grid">
        <article className="garage-insight-card">
          <div><Database size={18} /><strong>Referencia histórica del vehículo</strong></div>
          {baseline?.available ? (
            <>
              <span className="garage-status garage-status--ready">
                <CheckCircle2 size={14} /> Referencia disponible
              </span>
              <p>
                {baseline.qualifying_session_count} sesiones anteriores válidas y
                {' '}{Object.keys(baseline.signals || {}).length} señales comparables.
              </p>
            </>
          ) : (
            <>
              <span className="garage-status garage-status--learning">
                <AlertCircle size={14} /> Aprendiendo
              </span>
              <p>{baseline?.message || 'Aún no hay suficientes sesiones verificables.'}</p>
            </>
          )}
          <small>Solo usa capturas medidas, calidad ≥ 75% y sin alertas.</small>
        </article>

        <article className="garage-insight-card">
          <div><Usb size={18} /><strong>vLinker FS y cobertura de la aplicación</strong></div>
          <span className={`garage-status ${compatibility?.connected ? 'garage-status--ready' : 'garage-status--learning'}`}>
            {compatibility?.connected ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
            {compatibility?.connected ? 'Adaptador conectado' : 'Pendiente de conectar'}
          </span>
          <p>
            OBD-II genérico, DTC, freeze frame y Modo 06 real preparados.
            Los PIDs OEM propietarios requieren paquetes verificados específicos.
          </p>
          <small>{compatibility?.message}</small>
        </article>
      </div>

      {manufacturerData?.applicable && (
        <section style={{ backgroundColor: '#0b1220', border: '1px solid #334155', borderRadius: '8px', padding: '1rem', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', alignItems: 'flex-start', flexWrap: 'wrap' }}>
            <div>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0, color: '#f8fafc' }}>
                <ListChecks size={18} color="#22d3ee" /> Inventario completo de la ECU Volkswagen
              </h4>
              <p style={{ color: '#cbd5e1', margin: '0.5rem 0 0', maxWidth: '780px' }}>
                Comprueba uno por uno los bloques documentados y conserva la respuesta bruta. Una métrica solo figura como confirmada si este coche la ha devuelto realmente.
              </p>
            </div>
            <button
              type="button"
              onClick={runFullInventory}
              disabled={inventoryRunning || !compatibility?.connected}
              style={{ background: inventoryRunning ? '#334155' : '#0891b2', color: '#f8fafc', border: 0, borderRadius: '6px', padding: '0.65rem 0.9rem', fontWeight: 800, cursor: inventoryRunning || !compatibility?.connected ? 'not-allowed' : 'pointer' }}
            >
              <RefreshCw size={15} style={{ marginRight: '0.4rem', verticalAlign: 'text-bottom' }} />
              {inventoryRunning ? 'Leyendo todos los bloques…' : 'Repetir inventario completo'}
            </button>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', margin: '1rem 0' }}>
            <span className="garage-status garage-status--ready">{summary.verified_live_signal_count || 0} métricas confirmadas</span>
            <span className="garage-status garage-status--learning">{summary.responding_group_count || 0} / {summary.documented_group_count || summary.tested_group_count || 69} bloques responden</span>
            <span className="garage-status garage-status--learning">Cobertura real: {summary.coverage_percent ?? 0}%</span>
          </div>
          <p style={{ color: '#94a3b8', fontSize: '0.82rem' }}>
            “No disponible” significa que la ECU no devolvió ese campo o que todavía no se ha comprobado; no se sustituye por un valor calculado o simulado.
          </p>
          {inventoryError && <p style={{ color: '#fb7185', fontWeight: 700 }}>{inventoryError}</p>}

          {capabilities.length > 0 && (
            <details>
              <summary style={{ cursor: 'pointer', color: '#22d3ee', fontWeight: 800 }}>Ver las {capabilities.length} métricas catalogadas</summary>
              <div style={{ marginTop: '0.8rem' }}>
                <select value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)} style={{ background: '#111827', color: '#f8fafc', border: '1px solid #475569', borderRadius: '6px', padding: '0.45rem' }}>
                  {categories.map((category) => <option key={category} value={category}>{category}</option>)}
                </select>
                <div style={{ maxHeight: '430px', overflow: 'auto', marginTop: '0.75rem', borderTop: '1px solid #334155' }}>
                  {visibleCapabilities.map((item: any) => (
                    <div key={item.pid_name} style={{ display: 'grid', gridTemplateColumns: '90px minmax(220px, 1fr) 155px 120px', gap: '0.75rem', alignItems: 'center', padding: '0.55rem 0.25rem', borderBottom: '1px solid #1e293b', fontSize: '0.82rem' }}>
                      <code style={{ color: '#94a3b8' }}>{item.pid || '—'}</code>
                      <span style={{ color: '#e2e8f0' }}>{item.label || item.pid_name}</span>
                      <span style={{ color: '#94a3b8' }}>{item.category || 'Sin clasificar'}</span>
                      <strong style={{ color: item.supported_verified ? '#a3e635' : item.status === 'not_tested' ? '#fbbf24' : '#94a3b8' }}>
                        {item.supported_verified ? `Confirmada${item.sample_value !== null && item.sample_value !== undefined ? ` · ${item.sample_value} ${item.unit || ''}` : ''}` : item.status === 'not_tested' ? 'Pendiente' : 'No disponible'}
                      </strong>
                    </div>
                  ))}
                </div>
              </div>
            </details>
          )}
        </section>
      )}

      <form onSubmit={handleAddRepair} style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
        <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
          + Registrar Nueva Reparación / Mantenimiento
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '0.75rem', alignItems: 'center' }}>
          <input
            type="text"
            placeholder="Descripción (ej. Cambio de Bujías y Limpieza de MAF)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            style={{ backgroundColor: '#1e293b', color: '#f8fafc', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #334155' }}
          />
          <input
            type="text"
            placeholder="Notas (ej. Bujías NGK Iridium de 0.8mm)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            style={{ backgroundColor: '#1e293b', color: '#f8fafc', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #334155' }}
          />
          <button
            type="submit"
            disabled={loading || !description.trim()}
            style={{
              backgroundColor: '#f59e0b',
              color: '#0f172a',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontWeight: 800,
              cursor: loading || !description.trim() ? 'not-allowed' : 'pointer'
            }}
          >
            Guardar Reparación
          </button>
        </div>
      </form>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {repairs.length === 0 ? (
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>No hay intervenciones registradas en el historial de este vehículo.</p>
        ) : (
          repairs.map((r) => (
            <div key={r.id} style={{ backgroundColor: '#0f172a', padding: '0.75rem 1rem', borderRadius: '8px', borderLeft: '4px solid #f59e0b' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.2rem' }}>
                <strong style={{ fontSize: '0.95rem', color: '#f8fafc' }}>{r.description}</strong>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{r.performed_at}</span>
              </div>
              {r.notes && <p style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '0.25rem' }}>{r.notes}</p>}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
