import React from 'react';
import { Activity, AlertTriangle, Disc, Flame, Flag, Volume2, Zap } from 'lucide-react';

interface EventMarkerBarProps {
  onMarkEvent: (type: string, note?: string) => void;
  disabled?: boolean;
}

export const EventMarkerBar: React.FC<EventMarkerBarProps> = ({ onMarkEvent, disabled = false }) => {
  const eventTypes = [
    { id: 'jerk', label: 'Tirón', icon: Zap, color: '#ffca28' },
    { id: 'power_loss', label: 'Pérdida potencia', icon: AlertTriangle, color: '#ff334f' },
    { id: 'vibration', label: 'Vibración', icon: Activity, color: '#ff2e9f' },
    { id: 'smoke', label: 'Humo', icon: Flame, color: '#8c8c94' },
    { id: 'idle_rough', label: 'Ralentí irregular', icon: Disc, color: '#00dcff' },
    { id: 'noise', label: 'Ruido / anomalía', icon: Volume2, color: '#c7ff35' }
  ];

  return (
    <section className="race-panel">
      <div className="race-panel__header">
        <h3 className="race-panel__title">
          <Flag size={16} color="#ff5a1f" />
          Marcador de incidencias // registro rápido
        </h3>
        <span className="section-kicker">{disabled ? 'Captura inactiva' : 'Captura activa'}</span>
      </div>

      <div className="event-grid">
        {eventTypes.map((event) => {
          const Icon = event.icon;
          return (
            <button
              key={event.id}
              onClick={() => onMarkEvent(event.id, event.label)}
              disabled={disabled}
              className="event-button"
              style={{ '--event-color': event.color } as React.CSSProperties}
            >
              <Icon size={15} color={event.color} />
              {event.label}
            </button>
          );
        })}
      </div>
    </section>
  );
};
