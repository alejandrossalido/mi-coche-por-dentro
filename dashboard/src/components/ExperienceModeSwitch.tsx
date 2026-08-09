import React from 'react';
import { GraduationCap, SlidersHorizontal } from 'lucide-react';
import type { ExperienceMode } from '@/lib/experience';

interface ExperienceModeSwitchProps {
  mode: ExperienceMode;
  onChange: (mode: ExperienceMode) => void;
  onOpenHelp: () => void;
}

export const ExperienceModeSwitch: React.FC<ExperienceModeSwitchProps> = ({
  mode,
  onChange,
  onOpenHelp
}) => (
  <div className="experience-toolbar">
    <div>
      <span>Forma de trabajo</span>
      <strong>{mode === 'guided' ? 'La aplicación te acompaña paso a paso' : 'Todos los controles y datos técnicos visibles'}</strong>
    </div>
    <div className="experience-switch" role="group" aria-label="Forma de trabajo">
      <button
        type="button"
        className={mode === 'guided' ? 'active' : ''}
        onClick={() => onChange('guided')}
        aria-pressed={mode === 'guided'}
      >
        <GraduationCap size={15} />
        Modo guiado
      </button>
      <button
        type="button"
        className={mode === 'professional' ? 'active' : ''}
        onClick={() => onChange('professional')}
        aria-pressed={mode === 'professional'}
      >
        <SlidersHorizontal size={15} />
        Modo profesional
      </button>
    </div>
    <button type="button" className="experience-help" onClick={onOpenHelp}>
      ¿Cómo funciona?
    </button>
  </div>
);
