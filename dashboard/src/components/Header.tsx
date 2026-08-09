import React from 'react';
import { Car, Radio, Signal, Timer, Wifi } from 'lucide-react';
import { LanguageSelector } from '@/components/LanguageSelector';
import { useI18n } from '@/lib/i18n';

interface HeaderProps {
  adapterState: string;
  vehicleName?: string;
  isRecording: boolean;
  elapsedSec?: number;
}

export const Header: React.FC<HeaderProps> = ({ adapterState, vehicleName, isRecording, elapsedSec = 0 }) => {
  const { t } = useI18n();
  const connected = adapterState === 'VEHICLE_CONNECTED' || adapterState === 'CAPTURING';
  const stateLabel = t(isRecording ? 'GRABANDO EN DIRECTO' : connected ? 'ECU CONECTADA' : 'EN ESPERA');
  const stateColor = isRecording ? '#ff334f' : connected ? '#c7ff35' : '#ffca28';
  const hours = Math.floor(elapsedSec / 3600).toString().padStart(2, '0');
  const minutes = Math.floor((elapsedSec % 3600) / 60).toString().padStart(2, '0');
  const seconds = Math.floor(elapsedSec % 60).toString().padStart(2, '0');

  return (
    <header className="race-header">
      <div className="race-header__stripe" />

      <div className="race-brand">
        <div className="race-brand__badge" aria-hidden="true">
          <span>M</span>
          <small>OBD</small>
        </div>
        <div>
          <div className="race-brand__eyebrow">{t('SISTEMA DE INFORMACIÓN DEL VEHÍCULO // 02')}</div>
          <h1>{t('MI COCHE')} <span>{t('POR DENTRO')}</span></h1>
          <p>{t('TELEMETRÍA · DIAGNÓSTICO · LABORATORIO DE RENDIMIENTO')}</p>
        </div>
      </div>

      <div className="race-header__center" aria-hidden="true">
        <div className="shift-light">
          {[0, 1, 2, 3, 4, 5, 6, 7].map((light) => (
            <i key={light} className={light < 3 ? 'green' : light < 6 ? 'orange' : 'red'} />
          ))}
        </div>
        <div className="race-header__clock">
          <Timer size={13} />
          <span>{t('SESIÓN')} {hours}:{minutes}:{seconds}</span>
        </div>
      </div>

      <div className="race-status">
        <div className="race-status__vehicle">
          <Car size={17} />
          <div>
            <small>{t('PERFIL DEL VEHÍCULO')}</small>
            <strong>{vehicleName ? t(vehicleName) : t('NINGÚN VEHÍCULO SELECCIONADO')}</strong>
          </div>
        </div>
        <div className="race-status__network" style={{ '--state-color': stateColor } as React.CSSProperties}>
          {isRecording ? <Radio size={17} /> : connected ? <Signal size={17} /> : <Wifi size={17} />}
          <div>
            <small>{t('ESTADO DE CONEXIÓN OBD')}</small>
            <strong>{stateLabel}</strong>
          </div>
        </div>
        <LanguageSelector />
      </div>

      <style jsx>{`
        .race-header {
          position: relative;
          min-height: 92px;
          display: grid;
          grid-template-columns: minmax(320px, 1.1fr) auto minmax(320px, 1fr);
          align-items: center;
          gap: 1.5rem;
          padding: 0.85rem max(1.25rem, calc((100vw - 1680px) / 2));
          border-bottom: 1px solid #3b3b41;
          background:
            linear-gradient(90deg, rgba(255,90,31,.12), transparent 20%, transparent 80%, rgba(0,220,255,.06)),
            linear-gradient(180deg, #1b1b1f, #08080a);
          box-shadow: 0 10px 28px rgba(0,0,0,.4), inset 0 -1px #000;
        }
        .race-header__stripe {
          position: absolute;
          left: 0;
          right: 0;
          bottom: -4px;
          height: 3px;
          background: linear-gradient(90deg, #ff5a1f 0 11%, #f5f0e8 11% 12%, transparent 12% 82%, #00dcff 82% 88%, #ff2e9f 88%);
          box-shadow: 0 0 10px rgba(255,90,31,.25);
        }
        .race-brand {
          display: flex;
          align-items: center;
          gap: .85rem;
          min-width: 0;
        }
        .race-brand__badge {
          width: 54px;
          height: 54px;
          flex: 0 0 auto;
          display: grid;
          place-content: center;
          border: 2px solid #b9b8b2;
          border-radius: 50%;
          background: radial-gradient(circle, #26262b, #08080a 68%);
          box-shadow: inset 0 0 0 3px #111, 0 0 0 1px #000, 0 0 18px rgba(255,90,31,.12);
          transform: skew(-5deg);
          text-align: center;
        }
        .race-brand__badge span {
          color: #ff5a1f;
          font-size: 1.1rem;
          font-weight: 900;
          line-height: .9;
        }
        .race-brand__badge small {
          color: #d8d5ce;
          font: 700 .45rem "Lucida Console", monospace;
          letter-spacing: .08em;
        }
        .race-brand__eyebrow {
          margin-bottom: .22rem;
          color: #77777e;
          font: 700 .55rem "Lucida Console", monospace;
          letter-spacing: .15em;
        }
        .race-brand h1 {
          font-size: clamp(1.25rem, 2vw, 1.75rem);
          font-style: italic;
          font-weight: 900;
          letter-spacing: -.045em;
          line-height: 1;
        }
        .race-brand h1 span { color: #ff5a1f; }
        .race-brand p {
          margin-top: .28rem;
          color: #a5a29b;
          font: 700 .57rem "Lucida Console", monospace;
          letter-spacing: .09em;
        }
        .race-header__center {
          display: grid;
          justify-items: center;
          gap: .42rem;
        }
        .shift-light {
          display: flex;
          gap: 5px;
          padding: 6px 9px;
          border: 1px solid #333339;
          background: #070708;
          box-shadow: inset 0 1px 5px #000;
        }
        .shift-light i {
          width: 10px;
          height: 6px;
          border-radius: 1px;
          opacity: .62;
        }
        .shift-light .green { background: #c7ff35; box-shadow: 0 0 6px #c7ff35; }
        .shift-light .orange { background: #ff8a1f; box-shadow: 0 0 6px #ff8a1f; }
        .shift-light .red { background: #ff334f; box-shadow: 0 0 6px #ff334f; }
        .race-header__clock {
          display: flex;
          align-items: center;
          gap: .35rem;
          color: #8d8d93;
          font: 700 .55rem "Lucida Console", monospace;
          letter-spacing: .08em;
        }
        .race-status {
          display: flex;
          justify-content: flex-end;
          gap: .5rem;
          min-width: 0;
        }
        .race-status__vehicle,
        .race-status__network {
          min-width: 0;
          display: flex;
          align-items: center;
          gap: .55rem;
          padding: .55rem .7rem;
          border: 1px solid #36363c;
          background: linear-gradient(#17171b, #0b0b0d);
          box-shadow: inset 0 1px rgba(255,255,255,.05);
        }
        .race-status__vehicle svg { color: #a5a29b; }
        .race-status__network {
          color: var(--state-color);
          border-color: color-mix(in srgb, var(--state-color) 55%, #333);
        }
        .race-status small {
          display: block;
          margin-bottom: .16rem;
          color: #696970;
          font: 700 .47rem "Lucida Console", monospace;
          letter-spacing: .11em;
        }
        .race-status strong {
          display: block;
          max-width: 190px;
          overflow: hidden;
          color: inherit;
          font: 700 .63rem "Lucida Console", monospace;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        @media (max-width: 1100px) {
          .race-header { grid-template-columns: 1fr auto; }
          .race-header__center { display: none; }
        }
        @media (max-width: 720px) {
          .race-header { grid-template-columns: 1fr; padding: .8rem 1rem; }
          .race-status { justify-content: stretch; }
          .race-status > div { flex: 1; }
        }
      `}</style>
    </header>
  );
};
