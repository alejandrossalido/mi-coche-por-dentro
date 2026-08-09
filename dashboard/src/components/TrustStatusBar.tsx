import React from 'react';
import { CheckCircle2, CircleDot, DatabaseZap, HardDriveDownload, Radio, ShieldCheck } from 'lucide-react';

interface TrustStatusBarProps {
  isRecording: boolean;
  adapterConnected: boolean;
  captureMetrics?: any;
  dataSources?: string[];
  coverageLabel: string;
  activeSessionTitle?: string;
}

export const TrustStatusBar: React.FC<TrustStatusBarProps> = ({
  isRecording,
  adapterConnected,
  captureMetrics,
  dataSources = [],
  coverageLabel,
  activeSessionTitle
}) => {
  const simulated = dataSources.includes('simulated');
  const sourceLabel = simulated
    ? 'Datos simulados'
    : dataSources.includes('measured')
      ? 'Datos medidos'
      : isRecording
        ? 'Esperando primera lectura'
        : 'Sin captura seleccionada';
  const successRate = captureMetrics
    ? Math.round((captureMetrics.valid_ratio || 0) * 100)
    : undefined;
  const requestedSignals = captureMetrics?.requested_signal_count ?? captureMetrics?.pids_requested?.length ?? 0;
  const capturedSignals = captureMetrics?.captured_signal_count ?? 0;

  return (
    <section className={`trust-bar${simulated ? ' trust-bar--warning' : ''}`} aria-label="Trazabilidad de los datos">
      <div className="trust-bar__title">
        <ShieldCheck size={16} />
        <span>Confianza de los datos</span>
      </div>
      <div className="trust-item">
        <DatabaseZap size={15} />
        <div><span>Origen</span><strong>{sourceLabel}</strong></div>
      </div>
      <div className="trust-item">
        {isRecording ? <Radio size={15} /> : <CircleDot size={15} />}
        <div><span>Captura</span><strong>{isRecording ? 'Registrando ahora' : adapterConnected ? 'Preparada' : 'En espera'}</strong></div>
      </div>
      <div className="trust-item">
        <CheckCircle2 size={15} />
        <div>
          <span>Calidad en directo</span>
          <strong>{successRate === undefined ? 'Pendiente' : `${successRate}% · ${capturedSignals}/${requestedSignals} señales guardadas`}</strong>
        </div>
      </div>
      <div className="trust-item trust-item--wide">
        <ShieldCheck size={15} />
        <div><span>Cobertura</span><strong>{coverageLabel}</strong></div>
      </div>
      <div className="trust-item trust-item--wide">
        <HardDriveDownload size={15} />
        <div>
          <span>Conservación</span>
          <strong>{isRecording ? 'Autoguardado activo' : activeSessionTitle || 'Sin sesión activa'}</strong>
        </div>
      </div>
    </section>
  );
};
