'use client';

import React, { useMemo, useState } from 'react';
import {
  BatteryWarning,
  CloudCog,
  Gauge,
  Play,
  RotateCcw,
  Search,
  ThermometerSun,
  Wind
} from 'lucide-react';
import type { CaptureProfile } from '@/components/GuidedTestWizard';
import { useI18n } from '@/lib/i18n';

export interface GuidedSessionContext {
  symptom: string;
  title: string;
  engineCondition: 'cold' | 'warm' | 'hot';
  odometerKm?: number;
}

interface SymptomGuideProps {
  profiles: CaptureProfile[];
  loading?: boolean;
  disabled?: boolean;
  onStart: (profileId: string, context: GuidedSessionContext) => void;
}

const SYMPTOMS = [
  { id: 'start', label: 'Le cuesta arrancar', icon: RotateCcw, profile: 'COLD_START' },
  { id: 'idle', label: 'Ralentí inestable o vibración', icon: Gauge, profile: 'IDLE_STABILITY' },
  { id: 'power', label: 'Falta de potencia', icon: Wind, profile: 'INTAKE_TURBO' },
  { id: 'temperature', label: 'Temperatura o refrigeración', icon: ThermometerSun, profile: 'COOLING_SYSTEM' },
  { id: 'battery', label: 'Batería o carga eléctrica', icon: BatteryWarning, profile: 'BATTERY_CHARGING' },
  { id: 'emissions', label: 'Humo, consumo o emisiones', icon: CloudCog, profile: 'FUEL_MIXTURE' }
];

export const SymptomGuide: React.FC<SymptomGuideProps> = ({
  profiles,
  loading = false,
  disabled = false,
  onStart
}) => {
  const { t } = useI18n();
  const [selectedId, setSelectedId] = useState('power');
  const [detail, setDetail] = useState('');
  const [engineCondition, setEngineCondition] = useState<'cold' | 'warm' | 'hot'>('warm');
  const [odometer, setOdometer] = useState('');
  const selectedSymptom = SYMPTOMS.find((item) => item.id === selectedId) || SYMPTOMS[0];
  const recommended = useMemo(
    () => profiles.find((profile) => profile.id === selectedSymptom.profile)
      || profiles.find((profile) => profile.id === 'COMPLETE_DIAGNOSTIC'),
    [profiles, selectedSymptom]
  );

  return (
    <section className="symptom-guide">
      <div className="symptom-guide__intro">
        <span className="section-kicker">Inicio rápido</span>
        <h2>¿Qué notas en el coche?</h2>
        <p>Elige el síntoma y prepararemos la prueba que mejor puede confirmarlo con datos.</p>
      </div>
      <div className="symptom-grid">
        {SYMPTOMS.map((symptom) => {
          const Icon = symptom.icon;
          return (
            <button
              type="button"
              key={symptom.id}
              className={selectedId === symptom.id ? 'active' : ''}
              onClick={() => setSelectedId(symptom.id)}
              disabled={disabled}
            >
              <Icon size={18} />
              <span>{t(symptom.label)}</span>
            </button>
          );
        })}
      </div>
      <div className="symptom-plan">
        <div className="symptom-fields">
          <label>
            <span>Describe cuándo ocurre (opcional)</span>
            <textarea
              value={detail}
              onChange={(event) => setDetail(event.target.value)}
              placeholder="Ej.: al adelantar en cuarta, entre 2.000 y 2.500 rpm…"
              rows={2}
              maxLength={500}
              disabled={disabled}
            />
          </label>
          <div>
            <label>
              <span>Estado del motor</span>
              <select
                value={engineCondition}
                onChange={(event) => setEngineCondition(event.target.value as 'cold' | 'warm' | 'hot')}
                disabled={disabled}
              >
                <option value="cold">Frío, antes de arrancar</option>
                <option value="warm">A temperatura normal</option>
                <option value="hot">Muy caliente</option>
              </select>
            </label>
            <label>
              <span>Kilometraje (opcional)</span>
              <input
                inputMode="numeric"
                value={odometer}
                onChange={(event) => setOdometer(event.target.value.replace(/[^\d]/g, ''))}
                placeholder="145000"
                disabled={disabled}
              />
            </label>
          </div>
        </div>
        <article className="recommended-plan">
          <div>
            <Search size={17} />
            <span>Prueba recomendada</span>
          </div>
          <h3>{t(recommended?.name || 'Diagnóstico completo guiado')}</h3>
          <p>{t(recommended?.description || 'Comprobaremos las señales disponibles de forma ordenada.')}</p>
          <small>
            {recommended
              ? t(`${Math.round(recommended.recommended_duration_sec / 60)} min previstos · ${recommended.pids.length} señales solicitadas`)
              : t('Preparando perfiles disponibles…')}
          </small>
          <button
            type="button"
            className="race-button race-button--start"
            disabled={!recommended || loading || disabled}
            onClick={() => recommended && onStart(recommended.id, {
              symptom: `${t(selectedSymptom.label)}${detail ? `: ${detail}` : ''}`,
              title: t(selectedSymptom.label),
              engineCondition,
              odometerKm: odometer ? Number(odometer) : undefined
            })}
          >
            <Play size={16} fill="currentColor" />
            Validar conexión e iniciar esta prueba
          </button>
        </article>
      </div>
    </section>
  );
};
