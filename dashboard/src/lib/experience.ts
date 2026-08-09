export type ExperienceMode = 'guided' | 'professional';

export interface SessionRecord {
  id: string;
  vehicle_id: string;
  profile_id?: string;
  title?: string;
  symptom?: string;
  started_at: string;
  ended_at?: string;
  odometer_km?: number;
  engine_condition?: 'cold' | 'warm' | 'hot';
  notes?: string;
  capture_quality_score?: number;
  status: 'recording' | 'completed' | 'interrupted' | 'error';
  sample_count?: number;
  signal_count?: number;
  duration_sec?: number;
  data_sources?: string[];
  alert_count?: number;
  result_label?: string;
}

import { getActiveLanguage } from './i18n';

const locales = { es: 'es-ES', en: 'en-GB', it: 'it-IT', de: 'de-DE' } as const;

export const formatSessionDate = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(locales[getActiveLanguage()], {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

export const formatDuration = (seconds?: number) => {
  const total = Math.max(0, Math.round(seconds || 0));
  const minutes = Math.floor(total / 60);
  const remainder = total % 60;
  return minutes ? `${minutes} min ${remainder.toString().padStart(2, '0')} s` : `${remainder} s`;
};
