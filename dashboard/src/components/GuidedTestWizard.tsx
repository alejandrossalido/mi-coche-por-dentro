'use client';

import React from 'react';
import {
  BatteryCharging,
  CheckCircle2,
  ClipboardCheck,
  Fuel,
  Gauge,
  Play,
  ShieldCheck,
  Thermometer,
  Wind
} from 'lucide-react';
import { useI18n } from '@/lib/i18n';

export interface TestStep {
  at_sec: number;
  title: string;
  instruction: string;
}

export interface CaptureProfile {
  id: string;
  name: string;
  description: string;
  recommended_duration_sec: number;
  pids: string[];
  steps?: TestStep[];
}

interface GuidedTestWizardProps {
  profiles: CaptureProfile[];
  selectedProfileId: string;
  onSelectProfile: (profileId: string) => void;
  onStartTest: (profileId: string) => void;
  isRecording: boolean;
  elapsedSec: number;
  loading?: boolean;
}

const PROFILE_ICONS: Record<string, React.ElementType> = {
  COMPLETE_DIAGNOSTIC: ClipboardCheck,
  BATTERY_CHARGING: BatteryCharging,
  COOLING_SYSTEM: Thermometer,
  IDLE_STABILITY: Gauge,
  INTAKE_TURBO: Wind,
  FUEL_MIXTURE: Fuel,
  EMISSIONS_ITV: ShieldCheck
};

const FEATURED_IDS = [
  'COMPLETE_DIAGNOSTIC',
  'BATTERY_CHARGING',
  'COOLING_SYSTEM',
  'IDLE_STABILITY',
  'INTAKE_TURBO',
  'FUEL_MIXTURE',
  'EMISSIONS_ITV'
];

export const GuidedTestWizard: React.FC<GuidedTestWizardProps> = ({
  profiles,
  selectedProfileId,
  onSelectProfile,
  onStartTest,
  isRecording,
  elapsedSec,
  loading = false
}) => {
  const { t } = useI18n();
  const visibleProfiles = FEATURED_IDS
    .map((id) => profiles.find((profile) => profile.id === id))
    .filter(Boolean) as CaptureProfile[];
  const selected = profiles.find((profile) => profile.id === selectedProfileId) || visibleProfiles[0];
  const steps = selected?.steps || [];
  const activeStepIndex = Math.max(
    0,
    steps.reduce((current, step, index) => (elapsedSec >= step.at_sec ? index : current), 0)
  );
  const activeStep = steps[activeStepIndex];
  const duration = selected?.recommended_duration_sec || 1;
  const progress = Math.min(100, (elapsedSec / duration) * 100);

  return (
    <section className="race-panel guided-test">
      <div className="race-panel__header">
        <h3 className="race-panel__title">
          <ClipboardCheck size={18} color="#c7ff35" />
          Pruebas guiadas determinantes
        </h3>
        <span className="section-kicker">{isRecording ? 'Protocolo activo' : 'Selecciona objetivo'}</span>
      </div>

      <div className="test-profile-grid">
        {visibleProfiles.map((profile) => {
          const Icon = PROFILE_ICONS[profile.id] || ClipboardCheck;
          const active = selectedProfileId === profile.id;
          return (
            <button
              type="button"
              key={profile.id}
              className={`test-profile${active ? ' active' : ''}`}
              onClick={() => onSelectProfile(profile.id)}
              disabled={isRecording}
            >
              <Icon size={18} />
              <strong>{t(profile.name)}</strong>
              <span>{t(`${Math.round(profile.recommended_duration_sec / 60)} min · ${profile.pids.length} señales objetivo`)}</span>
            </button>
          );
        })}
      </div>

      {selected && (
        <div className="test-protocol">
          <div>
            <span className="control-label">Objetivo seleccionado</span>
            <h4>{t(selected.name)}</h4>
            <p>{t(selected.description)}</p>
          </div>
          {!isRecording ? (
            <button
              className="race-button race-button--start"
              onClick={() => onStartTest(selected.id)}
              disabled={loading}
            >
              <Play size={16} fill="currentColor" />
              Validar OBD e iniciar
            </button>
          ) : (
            <div className="test-progress-block">
              <div className="test-progress-meta">
                <span>{Math.round(elapsedSec)} s / {duration} s</span>
                <strong>{t(activeStep?.title || 'Capturando datos')}</strong>
              </div>
              <div className="test-progress"><span style={{ width: `${progress}%` }} /></div>
              <p>{t(activeStep?.instruction || 'Mantén una conducción segura y estable.')}</p>
            </div>
          )}
        </div>
      )}

      <div className="safety-strip">
        <CheckCircle2 size={16} />
        El conductor no debe manipular la pantalla. Usa un acompañante y respeta siempre la vía y los límites legales.
      </div>
    </section>
  );
};
