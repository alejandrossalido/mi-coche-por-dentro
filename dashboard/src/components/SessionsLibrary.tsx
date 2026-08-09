'use client';

import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  Bot,
  CalendarDays,
  CheckCircle2,
  FileText,
  Gauge,
  Pencil,
  RefreshCw,
  Save,
  Scale,
  Search,
  X
} from 'lucide-react';
import {
  formatDuration,
  formatSessionDate,
  type ExperienceMode,
  type SessionRecord
} from '@/lib/experience';
import { useI18n } from '@/lib/i18n';

interface VehicleOption {
  id: string;
  display_name: string;
}

interface SessionsLibraryProps {
  sessions: SessionRecord[];
  vehicles: VehicleOption[];
  selectedVehicleId: string;
  mode: ExperienceMode;
  loading?: boolean;
  onRefresh: () => void;
  onAnalyze: (sessionId: string) => void;
  onCompare: (sessionId: string) => void;
  onUpdated: (session: SessionRecord) => void;
}

const statusLabel: Record<string, string> = {
  completed: 'Finalizada',
  recording: 'Grabando',
  interrupted: 'Interrumpida',
  error: 'Con error'
};

export const SessionsLibrary: React.FC<SessionsLibraryProps> = ({
  sessions,
  vehicles,
  selectedVehicleId,
  mode,
  loading = false,
  onRefresh,
  onAnalyze,
  onCompare,
  onUpdated
}) => {
  const { language, locale } = useI18n();
  const [query, setQuery] = useState('');
  const [scope, setScope] = useState(selectedVehicleId);
  const [editingId, setEditingId] = useState('');
  const [editTitle, setEditTitle] = useState('');
  const [editOdometer, setEditOdometer] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setScope(selectedVehicleId);
  }, [selectedVehicleId]);

  const filtered = useMemo(() => sessions.filter((session) => {
    const vehicle = vehicles.find((item) => item.id === session.vehicle_id);
    const haystack = `${session.title || ''} ${session.notes || ''} ${session.symptom || ''} ${vehicle?.display_name || ''}`.toLowerCase();
    return (!scope || session.vehicle_id === scope) && (!query || haystack.includes(query.toLowerCase()));
  }), [query, scope, sessions, vehicles]);

  const beginEdit = (session: SessionRecord) => {
    setEditingId(session.id);
    setEditTitle(session.title || session.notes || 'Sesión de diagnóstico');
    setEditOdometer(session.odometer_km?.toString() || '');
  };

  const saveEdit = async (session: SessionRecord) => {
    setSaving(true);
    try {
      const response = await fetch(`/api/sessions/${session.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: editTitle,
          odometer_km: editOdometer ? Number(editOdometer) : null
        })
      });
      if (response.ok) {
        onUpdated({ ...session, ...(await response.json()) });
        setEditingId('');
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="session-library">
      <div className="library-heading">
        <div>
          <span className="section-kicker">Historial verificable</span>
          <h2>Biblioteca de sesiones</h2>
          <p>Encuentra, nombra, analiza y compara cada prueba sin perder su contexto.</p>
        </div>
        <button type="button" className="race-button" onClick={onRefresh} disabled={loading}>
          <RefreshCw size={15} className={loading ? 'spin' : ''} />
          Actualizar
        </button>
      </div>

      <div className="library-filters">
        <label className="library-search">
          <Search size={16} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Buscar por nombre, síntoma o vehículo…"
          />
        </label>
        <select value={scope} onChange={(event) => setScope(event.target.value)}>
          <option value="">Todos los vehículos</option>
          {vehicles.map((vehicle) => (
            <option key={vehicle.id} value={vehicle.id}>{vehicle.display_name}</option>
          ))}
        </select>
        <span>{filtered.length} sesiones</span>
      </div>

      {!filtered.length && (
        <div className="library-empty">
          <CalendarDays size={30} />
          <strong>Aún no hay sesiones en esta vista</strong>
          <p>Inicia una prueba guiada y aparecerá aquí al finalizar.</p>
        </div>
      )}

      <div className={`session-list session-list--${mode}`}>
        {filtered.map((session) => {
          const vehicle = vehicles.find((item) => item.id === session.vehicle_id);
          const simulated = session.data_sources?.includes('simulated');
          const measured = session.data_sources?.includes('measured');
          const goodQuality = (session.capture_quality_score || 0) >= 75;
          const editing = editingId === session.id;
          return (
            <article className={`session-card session-card--${session.status}`} key={session.id}>
              <div className="session-card__identity">
                <div className="session-card__status">
                  {session.status === 'completed' ? <CheckCircle2 size={15} /> : <AlertTriangle size={15} />}
                  {statusLabel[session.status] || session.status}
                </div>
                {editing ? (
                  <div className="session-edit">
                    <input value={editTitle} onChange={(event) => setEditTitle(event.target.value)} maxLength={100} />
                    <input
                      value={editOdometer}
                      onChange={(event) => setEditOdometer(event.target.value.replace(/[^\d]/g, ''))}
                      placeholder="Kilómetros"
                      inputMode="numeric"
                    />
                    <button type="button" onClick={() => saveEdit(session)} disabled={saving} aria-label="Guardar cambios"><Save size={15} /></button>
                    <button type="button" onClick={() => setEditingId('')} aria-label="Cancelar edición"><X size={15} /></button>
                  </div>
                ) : (
                  <>
                    <h3>{session.title || session.notes || 'Sesión de diagnóstico'}</h3>
                    <p>{vehicle?.display_name || 'Vehículo'} · {formatSessionDate(session.started_at)}</p>
                    {session.symptom && <blockquote>“{session.symptom}”</blockquote>}
                  </>
                )}
              </div>

              <div className="session-card__metrics">
                <span><strong>{formatDuration(session.duration_sec)}</strong>Duración</span>
                <span><strong>{session.sample_count || 0}</strong>Lecturas válidas</span>
                <span><strong>{session.signal_count || 0}</strong>Señales</span>
                <span><strong>{Math.round(session.capture_quality_score || 0)}%</strong>Calidad</span>
                <span className={session.alert_count ? 'warning' : ''}><strong>{session.alert_count || 0}</strong>Alertas</span>
              </div>

              <div className="session-card__result">
                <span className={`source-pill${simulated ? ' simulated' : ''}`}>
                  {simulated ? 'Simulados' : measured ? 'Medidos' : 'Sin datos'}
                </span>
                <strong>{session.result_label || (goodQuality ? 'Datos fiables' : 'Calidad limitada')}</strong>
                {session.odometer_km ? <small>{session.odometer_km.toLocaleString(locale)} km</small> : <small>Km no indicados</small>}
              </div>

              <div className="session-card__actions">
                <button type="button" onClick={() => onAnalyze(session.id)} disabled={session.status === 'recording'}>
                  <Bot size={15} /> Analizar
                </button>
                <button type="button" onClick={() => onCompare(session.id)} disabled={session.status !== 'completed'}>
                  <Scale size={15} /> Comparar
                </button>
                <a href={`/api/sessions/${session.id}/report?lang=${language}`} target="_blank" rel="noreferrer">
                  <FileText size={15} /> Informe
                </a>
                <button type="button" onClick={() => beginEdit(session)}>
                  <Pencil size={15} /> Renombrar
                </button>
              </div>
              {mode === 'professional' && (
                <div className="session-card__technical">
                  <Gauge size={14} />
                  <span>Protocolo: {session.profile_id || 'Histórico sin identificar'}</span>
                  <span>Motor: {session.engine_condition === 'cold' ? 'frío' : session.engine_condition === 'hot' ? 'muy caliente' : 'caliente'}</span>
                  <code>{session.id.slice(0, 8)}</code>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
};
