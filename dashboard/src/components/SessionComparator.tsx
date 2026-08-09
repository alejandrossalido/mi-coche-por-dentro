'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, CheckCircle2, Scale, Sparkles } from 'lucide-react';
import { formatSessionDate, type SessionRecord } from '@/lib/experience';
import { telemetryLabel } from '@/lib/telemetryLabels';

interface SessionComparatorProps {
  sessions: SessionRecord[];
  initialBaseSessionId?: string;
}

export const SessionComparator: React.FC<SessionComparatorProps> = ({
  sessions,
  initialBaseSessionId
}) => {
  const [sessionA, setSessionA] = useState('');
  const [sessionB, setSessionB] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (initialBaseSessionId) setSessionA(initialBaseSessionId);
  }, [initialBaseSessionId]);

  useEffect(() => {
    if (!sessionA && sessions[1]) setSessionA(sessions[1].id);
    if (!sessionB && sessions[0]) setSessionB(sessions[0].id);
  }, [sessionA, sessionB, sessions]);

  const previewWarnings = useMemo(() => {
    const a = sessions.find((session) => session.id === sessionA);
    const b = sessions.find((session) => session.id === sessionB);
    if (!a || !b) return [];
    const warnings: string[] = [];
    if (a.profile_id && b.profile_id && a.profile_id !== b.profile_id) warnings.push('Protocolos distintos');
    if (a.engine_condition !== b.engine_condition) warnings.push('Condición del motor distinta');
    if (Math.min(a.capture_quality_score || 0, b.capture_quality_score || 0) < 60) warnings.push('Calidad limitada');
    return warnings;
  }, [sessionA, sessionB, sessions]);

  const handleCompare = async () => {
    if (!sessionA || !sessionB) return;
    if (sessionA === sessionB) {
      setError('Selecciona dos sesiones diferentes.');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await fetch('/api/sessions/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id_a: sessionA,
          session_id_b: sessionB,
          label_a: 'Antes',
          label_b: 'Después'
        })
      });
      const data = await response.json();
      if (!response.ok) setError(data.detail || 'No se pudieron comparar las sesiones.');
      else if (data.error) setError(data.error);
      else setResult(data);
    } catch {
      setError('No se pudo comunicar con el analizador local.');
    } finally {
      setLoading(false);
    }
  };

  const comparedSignals = result?.signals_compared
    ? Object.entries(result.signals_compared) as Array<[string, any]>
    : [];

  return (
    <section className="comparison-workspace">
      <div className="library-heading">
        <div>
          <span className="section-kicker">Prueba reproducible</span>
          <h2>Comparación antes / después</h2>
          <p>La aplicación comprueba primero si ambas capturas se pueden comparar con rigor.</p>
        </div>
      </div>

      <div className="comparison-picker">
        <label>
          <span>Referencia · Antes</span>
          <select value={sessionA} onChange={(event) => setSessionA(event.target.value)}>
            <option value="">Seleccionar sesión…</option>
            {sessions.map((session) => (
              <option key={session.id} value={session.id}>
                {formatSessionDate(session.started_at)} · {session.title || session.notes || session.id.slice(0, 8)}
              </option>
            ))}
          </select>
        </label>
        <div className="comparison-arrow" aria-hidden="true">→</div>
        <label>
          <span>Resultado · Después</span>
          <select value={sessionB} onChange={(event) => setSessionB(event.target.value)}>
            <option value="">Seleccionar sesión…</option>
            {sessions.map((session) => (
              <option key={session.id} value={session.id}>
                {formatSessionDate(session.started_at)} · {session.title || session.notes || session.id.slice(0, 8)}
              </option>
            ))}
          </select>
        </label>
        <button className="race-button race-button--start" type="button" onClick={handleCompare} disabled={!sessionA || !sessionB || loading}>
          <Scale size={16} />
          {loading ? 'Comprobando…' : 'Comparar con rigor'}
        </button>
      </div>

      {previewWarnings.length > 0 && !result && (
        <div className="comparison-preview-warning">
          <AlertTriangle size={17} />
          <span>Antes de calcular: {previewWarnings.join(' · ')}. El informe cuantificará su impacto.</span>
        </div>
      )}
      {error && <div className="operation-banner error"><AlertTriangle size={17} /><strong>{error}</strong></div>}

      {result?.comparability && (
        <article className={`comparability-card comparability-card--${result.comparability.level}`}>
          <div className="comparability-score">
            <strong>{result.comparability.score}</strong>
            <span>/ 100</span>
          </div>
          <div>
            <span>Comparabilidad {result.comparability.level}</span>
            <h3>{result.comparability.message}</h3>
            {result.comparability.warnings.length > 0 ? (
              <ul>{result.comparability.warnings.map((warning: string) => <li key={warning}>{warning}</li>)}</ul>
            ) : (
              <p><CheckCircle2 size={14} /> Mismo protocolo, condición y origen de datos.</p>
            )}
          </div>
        </article>
      )}

      {result?.conclusion && (
        <article className={`comparison-hero comparison-hero--${result.conclusion.verdict}`}>
          <Sparkles size={20} />
          <div>
            <span>Conclusión calculada</span>
            <h3>{result.conclusion.summary}</h3>
          </div>
          <div className="comparison-totals">
            <strong>{result.conclusion.improved_signals}</strong><span>más estables</span>
            <strong>{result.conclusion.worsened_signals}</strong><span>más variables</span>
          </div>
        </article>
      )}

      {comparedSignals.length > 0 && (
        <div className="comparison-signal-grid">
          {comparedSignals.map(([pid, info]) => {
            const extent = Math.max(Math.abs(info.session_a.mean || 0), Math.abs(info.session_b.mean || 0), 1);
            return (
              <article key={pid} className={info.stability_improved ? 'improved' : 'worsened'}>
                <header>
                  <div><span>{pid}</span><strong>{telemetryLabel(pid)}</strong></div>
                  <em>{info.stability_improved ? 'Más estable' : 'Más variable'}</em>
                </header>
                <div className="signal-comparison-bars">
                  <div><span>Antes</span><i><b style={{ width: `${Math.min(100, Math.abs(info.session_a.mean || 0) / extent * 100)}%` }} /></i><strong>{info.session_a.mean}</strong></div>
                  <div><span>Después</span><i><b style={{ width: `${Math.min(100, Math.abs(info.session_b.mean || 0) / extent * 100)}%` }} /></i><strong>{info.session_b.mean}</strong></div>
                </div>
                <footer>
                  <span>Δ {info.delta_mean > 0 ? '+' : ''}{info.delta_mean}</span>
                  <span>{info.pct_change_mean > 0 ? '+' : ''}{info.pct_change_mean}% de media</span>
                  <span>{Math.abs(info.pct_change_std)}% de variabilidad</span>
                </footer>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
};
