'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Car, ShieldCheck, X } from 'lucide-react';

export interface CreatedVehicle {
  id: string;
  display_name: string;
  make: string;
  model: string;
  year: number;
  generation?: string;
  variant?: string;
  engine?: string;
  engine_code?: string;
  fuel_type?: string;
  powertrain_type: 'gasoline' | 'diesel' | 'hybrid' | 'phev' | 'bev';
  market?: string;
}

interface AddVehicleDialogProps {
  open: boolean;
  onClose: () => void;
  onCreated: (vehicle: CreatedVehicle) => void;
}

const INITIAL_FORM = {
  display_name: '',
  make: '',
  model: '',
  year: String(new Date().getFullYear()),
  powertrain_type: 'gasoline',
  engine: '',
  generation: '',
  variant: '',
  engine_code: '',
  market: 'EU'
};

const POWERTRAINS = [
  { value: 'gasoline', label: 'Gasolina' },
  { value: 'diesel', label: 'Diésel' },
  { value: 'hybrid', label: 'Híbrido' },
  { value: 'phev', label: 'Híbrido enchufable' },
  { value: 'bev', label: 'Eléctrico' }
];

export const AddVehicleDialog: React.FC<AddVehicleDialogProps> = ({
  open,
  onClose,
  onCreated
}) => {
  const [form, setForm] = useState(INITIAL_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const makeInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    setError('');
    const focusTimer = window.setTimeout(() => makeInputRef.current?.focus(), 50);
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !saving) onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      window.clearTimeout(focusTimer);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [open, onClose, saving]);

  if (!open) return null;

  const update = (field: keyof typeof form, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      const response = await fetch('/api/vehicles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, year: Number(form.year) })
      });
      const data = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item: any) => item.msg).join(' · ')
          : data.detail;
        throw new Error(detail || 'No se pudo guardar el vehículo.');
      }
      onCreated(data);
      setForm(INITIAL_FORM);
      onClose();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'No se pudo guardar el vehículo.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className="vehicle-dialog-backdrop"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !saving) onClose();
      }}
    >
      <section
        className="vehicle-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="add-vehicle-title"
      >
        <header className="vehicle-dialog__header">
          <div className="vehicle-dialog__icon"><Car size={24} /></div>
          <div>
            <span className="vehicle-dialog__eyebrow">Alta rápida · Perfil ampliable</span>
            <h2 id="add-vehicle-title">Añadir vehículo al garaje</h2>
            <p>Podrás diagnosticarlo desde ahora y completar sus datos técnicos más adelante.</p>
          </div>
          <button
            type="button"
            className="vehicle-dialog__close"
            onClick={onClose}
            disabled={saving}
            aria-label="Cerrar formulario"
          >
            <X size={20} />
          </button>
        </header>

        <form className="vehicle-form" onSubmit={handleSubmit}>
          <div className="vehicle-form__grid">
            <label className="vehicle-form__field">
              <span>Marca *</span>
              <input
                ref={makeInputRef}
                value={form.make}
                onChange={(event) => update('make', event.target.value)}
                placeholder="Hyundai"
                maxLength={60}
                required
              />
            </label>
            <label className="vehicle-form__field">
              <span>Modelo *</span>
              <input
                value={form.model}
                onChange={(event) => update('model', event.target.value)}
                placeholder="Kona"
                maxLength={80}
                required
              />
            </label>
            <label className="vehicle-form__field">
              <span>Año *</span>
              <input
                type="number"
                value={form.year}
                onChange={(event) => update('year', event.target.value)}
                min="1886"
                max={new Date().getFullYear() + 1}
                required
              />
            </label>
            <label className="vehicle-form__field">
              <span>Propulsión *</span>
              <select
                value={form.powertrain_type}
                onChange={(event) => update('powertrain_type', event.target.value)}
              >
                {POWERTRAINS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </label>
            <label className="vehicle-form__field vehicle-form__field--wide">
              <span>Versión o motor</span>
              <input
                value={form.engine}
                onChange={(event) => update('engine', event.target.value)}
                placeholder="Ej. 1.6 GDi Hybrid 141 CV"
                maxLength={100}
              />
              <small>Muy recomendable para distinguir motorizaciones del mismo año.</small>
            </label>
            <label className="vehicle-form__field vehicle-form__field--wide">
              <span>Apodo</span>
              <input
                value={form.display_name}
                onChange={(event) => update('display_name', event.target.value)}
                placeholder="Opcional · Ej. Mi coche diario"
                maxLength={100}
              />
            </label>
          </div>

          <details className="vehicle-form__advanced">
            <summary>Datos técnicos opcionales</summary>
            <p>Si no los conoces, déjalos vacíos. La cobertura genérica seguirá disponible.</p>
            <div className="vehicle-form__grid">
              <label className="vehicle-form__field">
                <span>Generación</span>
                <input
                  value={form.generation}
                  onChange={(event) => update('generation', event.target.value)}
                  placeholder="Ej. OS facelift"
                  maxLength={60}
                />
              </label>
              <label className="vehicle-form__field">
                <span>Acabado / variante</span>
                <input
                  value={form.variant}
                  onChange={(event) => update('variant', event.target.value)}
                  placeholder="Ej. Tecno"
                  maxLength={100}
                />
              </label>
              <label className="vehicle-form__field">
                <span>Código de motor</span>
                <input
                  value={form.engine_code}
                  onChange={(event) => update('engine_code', event.target.value.toUpperCase())}
                  placeholder="Si figura en la documentación"
                  maxLength={50}
                />
              </label>
              <label className="vehicle-form__field">
                <span>Mercado</span>
                <select
                  value={form.market}
                  onChange={(event) => update('market', event.target.value)}
                >
                  <option value="EU">Europa</option>
                  <option value="US">Estados Unidos</option>
                  <option value="LATAM">Latinoamérica</option>
                  <option value="OTHER">Otro</option>
                </select>
              </label>
            </div>
          </details>

          <div className="vehicle-form__privacy">
            <ShieldCheck size={17} />
            <span>No hace falta introducir matrícula ni VIN para crear el vehículo.</span>
          </div>

          {error && <div className="vehicle-form__error" role="alert">{error}</div>}

          <footer className="vehicle-form__actions">
            <button type="button" className="race-button" onClick={onClose} disabled={saving}>
              Cancelar
            </button>
            <button
              type="submit"
              className="race-button race-button--start"
              disabled={saving || !form.make.trim() || !form.model.trim() || !form.year}
            >
              {saving ? 'Guardando…' : 'Añadir al garaje'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  );
};
