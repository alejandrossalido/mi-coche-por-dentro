'use client';

import React from 'react';
import { Languages } from 'lucide-react';
import { APP_LANGUAGES, AppLanguage, useI18n } from '@/lib/i18n';

interface LanguageSelectorProps {
  expanded?: boolean;
  className?: string;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({ expanded = false, className = '' }) => {
  const { language, setLanguage, t } = useI18n();

  if (expanded) {
    return (
      <div className={`language-picker language-picker--expanded ${className}`} role="group" aria-label={t('Seleccionar idioma')}>
        {APP_LANGUAGES.map((item) => (
          <button
            type="button"
            key={item.id}
            className={language === item.id ? 'active' : ''}
            onClick={() => setLanguage(item.id)}
            lang={item.id}
            aria-pressed={language === item.id}
          >
            <strong>{item.short}</strong>
            <span>{item.nativeName}</span>
          </button>
        ))}
      </div>
    );
  }

  return (
    <label className={`language-select ${className}`} title={t('Seleccionar idioma')}>
      <Languages size={16} aria-hidden="true" />
      <span className="sr-only">{t('Idioma')}</span>
      <select
        value={language}
        onChange={(event) => setLanguage(event.target.value as AppLanguage)}
        aria-label={t('Seleccionar idioma')}
      >
        {APP_LANGUAGES.map((item) => (
          <option key={item.id} value={item.id} lang={item.id}>{item.short} · {item.nativeName}</option>
        ))}
      </select>
    </label>
  );
};
