'use client';

import React, { useState } from 'react';
import {
  AlertOctagon,
  AlertTriangle,
  BatteryCharging,
  CheckCircle2,
  CircleHelp,
  Clock3,
  Droplets,
  Gauge,
  ShieldCheck,
  Thermometer,
  Wind
} from 'lucide-react';
import type { ExperienceMode } from '@/lib/experience';

interface DiagnosticSummaryPanelProps {
  analysis?: any;
  values: Record<string, any>;
  isRecording: boolean;
  captureMetrics?: any;
  captureError?: any;
  experienceMode?: ExperienceMode;
}

const SYSTEM_ICONS: Record<string, React.ElementType> = {
  engine: Gauge,
  cooling: Thermometer,
  intake: Wind,
  fuel: Droplets,
  electrical: BatteryCharging,
  emissions: ShieldCheck
};

const STATUS_LABELS: Record<string, string> = {
  green: 'Correcto',
  amber: 'Revisar',
  red: 'Crítico',
  unknown: 'Sin datos'
};

export const DiagnosticSummaryPanel: React.FC<DiagnosticSummaryPanelProps> = ({
  analysis,
  values,
  isRecording,
  captureMetrics,
  captureError,
  experienceMode = 'guided'
}) => {
  const [resultLevel, setResultLevel] = useState<'summary' | 'explanation' | 'technical'>(
    experienceMode === 'professional' ? 'technical' : 'summary'
  );
  const liveAlerts = [];
  if (typeof values.COOLANT_TEMP === 'number' && values.COOLANT_TEMP >= 103) {
    liveAlerts.push({
      severity: values.COOLANT_TEMP >= 110 ? 'critical' : 'warning',
      message: `Refrigerante elevado: ${values.COOLANT_TEMP.toFixed(1)} °C`
    });
  }
  if (typeof values.CONTROL_MODULE_VOLTAGE === 'number' && values.CONTROL_MODULE_VOLTAGE < 11.8) {
    liveAlerts.push({ severity: 'warning', message: `Tensión baja: ${values.CONTROL_MODULE_VOLTAGE.toFixed(2)} V` });
  }
  const dataStale = Boolean(captureMetrics?.data_stale);
  const alerts = analysis?.alerts || liveAlerts;
  const conclusion = analysis?.conclusion;
  const fuelDiagnosis = analysis?.fuel_diagnosis;
  const tripMetrics = captureMetrics?.trip_metrics || analysis?.trip_metrics;

  return (
    <section className="diagnostic-summary">
      {captureError && (
        <div className="capture-stop-alert">
          <AlertOctagon size={22} />
          <div>
            <strong>Captura detenida automáticamente</strong>
            <span>{captureError.message}</span>
          </div>
        </div>
      )}

      {isRecording && (
        <div className={`live-safety-banner${liveAlerts.length || dataStale ? ' warning' : ''}`}>
          {liveAlerts.length || dataStale ? <AlertTriangle size={20} /> : <CheckCircle2 size={20} />}
          <div>
            <strong>{dataStale ? 'La captura sigue abierta, pero la ECU ha dejado de responder' : liveAlerts.length ? 'Alerta activa durante la marcha' : 'Monitorización activa sin alertas críticas'}</strong>
            <span>
              {dataStale
                ? `Último dato válido hace ${captureMetrics.last_valid_age_sec?.toFixed?.(1) || captureMetrics.last_valid_age_sec} s · revisa el contacto o finaliza la prueba`
                : captureMetrics
                ? `${captureMetrics.valid_sample_count} lecturas válidas · ${captureMetrics.captured_signal_count || 0}/${captureMetrics.requested_signal_count || captureMetrics.pids_requested?.length || 0} señales guardadas · ${Math.round((captureMetrics.valid_ratio || 0) * 100)}% de éxito`
                : 'Validando el flujo de datos de la ECU…'}
            </span>
          </div>
        </div>
      )}

      {analysis && !isRecording && (
        <div className="result-levels">
          <div>
            <span>Profundidad del resultado</span>
            <strong>Empieza por la conclusión y abre solo el detalle que necesites.</strong>
          </div>
          <div role="group" aria-label="Profundidad del resultado">
            <button type="button" className={resultLevel === 'summary' ? 'active' : ''} onClick={() => setResultLevel('summary')}>
              Resumen
            </button>
            <button type="button" className={resultLevel === 'explanation' ? 'active' : ''} onClick={() => setResultLevel('explanation')}>
              Explicación
            </button>
            <button type="button" className={resultLevel === 'technical' ? 'active' : ''} onClick={() => setResultLevel('technical')}>
              Datos técnicos
            </button>
          </div>
        </div>
      )}

      {conclusion && (
        <div className={`conclusion-card conclusion-card--${conclusion.verdict}`}>
          <span className="control-label">Conclusión automática basada en evidencia</span>
          <h3>{conclusion.title}</h3>
          <p>{conclusion.summary}</p>
          <ol>
            {conclusion.next_steps?.map((step: string, index: number) => <li key={index}>{step}</li>)}
          </ol>
        </div>
      )}

      {tripMetrics?.available && (
        <div className="trip-consumption-card">
          <div>
            <span className="control-label">Consumo medio del trayecto</span>
            <strong>{Number(tripMetrics.average_l_per_100km).toFixed(1)} L/100 km</strong>
          </div>
          <p>{tripMetrics.reason} · {Number(tripMetrics.distance_km || 0).toFixed(2)} km analizados.</p>
        </div>
      )}

      {fuelDiagnosis?.applicable && (
        <div className={`fuel-diagnosis-card fuel-diagnosis-card--${fuelDiagnosis.status}`}>
          <div className="fuel-diagnosis-card__header">
            <div>
              <span className="control-label">Diagnóstico específico de consumo diésel</span>
              <h3>{fuelDiagnosis.title}</h3>
            </div>
            <strong>
              {fuelDiagnosis.coverage?.captured || 0}/{fuelDiagnosis.coverage?.total || 0} señales
            </strong>
          </div>
          <p>{fuelDiagnosis.summary}</p>
          {resultLevel !== 'summary' && fuelDiagnosis.metrics?.length > 0 && (
            <div className="fuel-metric-grid">
              {fuelDiagnosis.metrics.map((metric: any) => (
                <article key={metric.id} className={`fuel-metric fuel-metric--${metric.status}`}>
                  <span>{metric.label}</span>
                  <strong>{metric.value} {metric.unit}</strong>
                  <small>{metric.interpretation}</small>
                </article>
              ))}
            </div>
          )}
          {fuelDiagnosis.priorities?.length > 0 && (
            <ol>
              {fuelDiagnosis.priorities.map((priority: string, index: number) => <li key={index}>{priority}</li>)}
            </ol>
          )}
        </div>
      )}

      {analysis?.health?.length > 0 && resultLevel !== 'summary' && (
        <div className="health-grid">
          {analysis.health.map((system: any) => {
            const Icon = SYSTEM_ICONS[system.id] || CircleHelp;
            return (
              <article key={system.id} className={`health-card health-card--${system.status}`}>
                <div className="health-card__status">
                  <Icon size={18} />
                  <span>{STATUS_LABELS[system.status]}</span>
                </div>
                <strong>{system.label}</strong>
                <p>{system.reason}</p>
                <small>{system.signals?.length ? system.signals.join(' · ') : 'Cobertura insuficiente'}</small>
              </article>
            );
          })}
        </div>
      )}

      {resultLevel === 'technical' && analysis && (
        <div className="technical-evidence-strip">
          <div><span>Calidad global</span><strong>{Math.round(analysis.quality?.overall_score || 0)}%</strong></div>
          <div><span>Lecturas válidas</span><strong>{analysis.quality?.valid_samples ?? analysis.quality?.total_samples ?? captureMetrics?.valid_sample_count ?? '—'}</strong></div>
          <div><span>Sistemas evaluados</span><strong>{analysis.health?.length || 0}</strong></div>
          <div><span>Alertas detectadas</span><strong>{alerts.length}</strong></div>
        </div>
      )}

      {alerts.length > 0 && resultLevel !== 'summary' && (
        <div className="alert-timeline race-panel">
          <div className="race-panel__header">
            <h3 className="race-panel__title">
              <Clock3 size={17} color="#ffca28" />
              Cronología de anomalías y alertas
            </h3>
            <span className="section-kicker">{alerts.length} eventos</span>
          </div>
          {alerts.map((alert: any, index: number) => (
            <div className={`timeline-row timeline-row--${alert.severity}`} key={alert.id || index}>
              <span className="timeline-time">
                {typeof alert.timestamp_sec === 'number' ? `${alert.timestamp_sec.toFixed(1)} s` : 'Sesión'}
              </span>
              <div>
                <strong>{alert.message}</strong>
                {alert.recommendation && <p>{alert.recommendation}</p>}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
