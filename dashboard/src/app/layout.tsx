import './globals.css';
import React from 'react';
import { LanguageProvider } from '@/lib/i18n';

export const metadata = {
  title: 'Mi Coche por Dentro — Telemetría OBD-II',
  description: 'Cuadro de instrumentación local para telemetría OBD-II, diagnóstico determinista y análisis asistido.'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <LanguageProvider>
          <main>{children}</main>
        </LanguageProvider>
      </body>
    </html>
  );
}
