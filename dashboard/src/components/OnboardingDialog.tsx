'use client';

import React, { useEffect, useState } from 'react';
import { Activity, Bot, Cable, ChevronRight, Languages, ShieldCheck, X } from 'lucide-react';
import type { ExperienceMode } from '@/lib/experience';
import { LanguageSelector } from '@/components/LanguageSelector';
import { useI18n } from '@/lib/i18n';

interface OnboardingDialogProps {
  open: boolean;
  onClose: () => void;
  onChooseMode: (mode: ExperienceMode) => void;
}

const STEPS = [
  {
    icon: Cable,
    eyebrow: 'Paso 1',
    title: 'Conecta el coche cuando quieras medir',
    text: 'La aplicación no registra nada antes de iniciar una prueba. Primero comprueba el adaptador y la ECU.'
  },
  {
    icon: Activity,
    eyebrow: 'Paso 2',
    title: 'Sigue una prueba reproducible',
    text: 'El modo guiado recomienda el protocolo y te dice qué hacer. Los datos se guardan automáticamente durante la captura.'
  },
  {
    icon: Bot,
    eyebrow: 'Paso 3',
    title: 'Analiza una sesión concreta',
    text: 'El asistente explica la sesión que selecciones. No mezcla carreras anteriores ni inventa mediciones ausentes.'
  }
];

export const OnboardingDialog: React.FC<OnboardingDialogProps> = ({
  open,
  onClose,
  onChooseMode
}) => {
  const [step, setStep] = useState(0);
  const { t } = useI18n();

  useEffect(() => {
    if (open) setStep(0);
  }, [open]);

  if (!open) return null;
  const isLanguageStep = step === 0;
  const current = isLanguageStep ? null : STEPS[step - 1];
  const Icon = isLanguageStep ? Languages : current!.icon;

  return (
    <div className="welcome-backdrop" role="presentation">
      <section className="welcome-dialog" role="dialog" aria-modal="true" aria-labelledby="welcome-title">
        <button className="welcome-close" type="button" onClick={onClose} aria-label="Cerrar bienvenida">
          <X size={18} />
        </button>
        <div className="welcome-visual" aria-hidden="true">
          <div className="welcome-orbit"><ShieldCheck size={42} /></div>
          <span>{t('DIAGNÓSTICO OBD-II LOCAL')}</span>
        </div>
        <div className="welcome-copy">
          <span className="welcome-eyebrow">
            {isLanguageStep ? t('Selecciona tu idioma') : t(`Paso ${step + 1} de 4`)}
          </span>
          <Icon size={26} />
          <h2 id="welcome-title">{isLanguageStep ? 'Select your language / Selecciona tu idioma' : t(current!.title)}</h2>
          <p>{isLanguageStep ? t('Puedes cambiarlo en cualquier momento') : t(current!.text)}</p>
          {isLanguageStep && <LanguageSelector expanded />}
          <div className="welcome-progress" aria-label={t(`Paso ${step + 1} de 4`)}>
            {[0, 1, 2, 3].map((index) => <i key={index} className={index <= step ? 'active' : ''} />)}
          </div>
          {step < STEPS.length ? (
            <button className="welcome-primary" type="button" onClick={() => setStep((value) => value + 1)}>
              {t('Continuar')}
              <ChevronRight size={17} />
            </button>
          ) : (
            <div className="welcome-mode-actions">
              <button
                className="welcome-primary"
                type="button"
                onClick={() => {
                  onChooseMode('guided');
                  onClose();
                }}
              >
                {t('Empezar en modo guiado')}
              </button>
              <button
                className="welcome-secondary"
                type="button"
                onClick={() => {
                  onChooseMode('professional');
                  onClose();
                }}
              >
                {t('Prefiero el modo profesional')}
              </button>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};
