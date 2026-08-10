'use client';

import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  Bot,
  CheckCircle2,
  ExternalLink,
  FileText,
  History,
  Play,
  Plus,
  PlugZap,
  Scale,
  ScanLine,
  ShieldCheck,
  Square,
  TriangleAlert,
  Wrench,
  type LucideIcon
} from 'lucide-react';
import { AddVehicleDialog, type CreatedVehicle } from '@/components/AddVehicleDialog';
import { AiAssistantPanel } from '@/components/AiAssistantPanel';
import { ConnectionMetricsBar } from '@/components/ConnectionMetricsBar';
import { DiagnosticSummaryPanel } from '@/components/DiagnosticSummaryPanel';
import { DtcPanel } from '@/components/DtcPanel';
import { EventMarkerBar } from '@/components/EventMarkerBar';
import { ExperienceModeSwitch } from '@/components/ExperienceModeSwitch';
import { FreezeFrameInspector } from '@/components/FreezeFrameInspector';
import { GaragePanel } from '@/components/GaragePanel';
import { GuidedTestWizard, type CaptureProfile } from '@/components/GuidedTestWizard';
import { Header } from '@/components/Header';
import { ImReadinessPanel } from '@/components/ImReadinessPanel';
import { Mode06Panel } from '@/components/Mode06Panel';
import { OnboardingDialog } from '@/components/OnboardingDialog';
import { SessionComparator } from '@/components/SessionComparator';
import { SessionsLibrary } from '@/components/SessionsLibrary';
import { SymptomGuide, type GuidedSessionContext } from '@/components/SymptomGuide';
import { TelemetryChart } from '@/components/TelemetryChart';
import { TelemetryGaugesGrid } from '@/components/TelemetryGaugesGrid';
import { TrustStatusBar } from '@/components/TrustStatusBar';
import type { ExperienceMode, SessionRecord } from '@/lib/experience';
import { useI18n } from '@/lib/i18n';

interface Vehicle {
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
  powertrain_type?: 'gasoline' | 'diesel' | 'hybrid' | 'phev' | 'bev';
  market?: string;
}

interface AdapterPort {
  port: string;
  description: string;
  hwid: string;
  is_obdlink: boolean;
  priority?: number;
  excluded?: boolean;
}

type TabId = 'live' | 'sessions' | 'ai' | 'compare' | 'garage' | 'mode06' | 'im';

const sameSnapshot = (current: any, next: any) => (
  JSON.stringify(current ?? null) === JSON.stringify(next ?? null)
);

const downsampleTelemetry = (rows: any[], maxPerSignal = 700) => {
  const groups = new Map<string, any[]>();
  rows.forEach((row) => {
    if (typeof row?.value !== 'number' || !Number.isFinite(row.value)) return;
    const group = groups.get(row.pid) || [];
    group.push(row);
    groups.set(row.pid, group);
  });
  const output: any[] = [];
  groups.forEach((group) => {
    const step = Math.max(1, Math.ceil(group.length / maxPerSignal));
    for (let index = 0; index < group.length; index += step) output.push(group[index]);
    if (group.length && output[output.length - 1] !== group[group.length - 1]) output.push(group[group.length - 1]);
  });
  return output.sort((a, b) => a.timestamp_monotonic - b.timestamp_monotonic);
};

export default function DashboardPage() {
  const { language, t } = useI18n();
  const [activeTab, setActiveTab] = useState<TabId>('live');
  const [experienceMode, setExperienceMode] = useState<ExperienceMode>('guided');
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [adapterStatus, setAdapterStatus] = useState<any>({ state: 'ADAPTER_NOT_FOUND', is_connected: false });
  const [adapterPorts, setAdapterPorts] = useState<AdapterPort[]>([]);
  const [selectedAdapterPort, setSelectedAdapterPort] = useState('');
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState('');
  const [showAddVehicle, setShowAddVehicle] = useState(false);
  const [vehicleSpec, setVehicleSpec] = useState<any>(null);
  const [sessions, setSessions] = useState<SessionRecord[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [comparisonBaseId, setComparisonBaseId] = useState('');
  const [profiles, setProfiles] = useState<CaptureProfile[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState('COMPLETE_DIAGNOSTIC');
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [captureMetrics, setCaptureMetrics] = useState<any>(null);
  const [captureError, setCaptureError] = useState<any>(null);
  const [preflight, setPreflight] = useState<any>(null);
  const [manufacturerProbe, setManufacturerProbe] = useState<any>(null);
  const [manufacturerCapabilities, setManufacturerCapabilities] = useState<any[]>([]);
  const [metricCatalogCapabilities, setMetricCatalogCapabilities] = useState<any[]>([]);
  const [uiMessage, setUiMessage] = useState('');
  const [samples, setSamples] = useState<any[]>([]);
  const [telemetryValues, setTelemetryValues] = useState<Record<string, any>>({});
  const [dtcs, setDtcs] = useState<any[]>([]);
  const [markers, setMarkers] = useState<any[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const refreshSessionLibrary = async () => {
    setSessionsLoading(true);
    try {
      const response = await fetch('/api/sessions/library', { cache: 'no-store' });
      if (response.ok) setSessions(await response.json());
    } finally {
      setSessionsLoading(false);
    }
  };

  const refreshStatus = async () => {
    try {
      const response = await fetch('/api/status', { cache: 'no-store' });
      if (!response.ok) return;
      const data = await response.json();
      setAdapterStatus((current: any) => sameSnapshot(current, data.adapter) ? current : data.adapter);
      setIsRecording(data.is_recording);
      setCaptureMetrics((current: any) => sameSnapshot(current, data.capture_metrics) ? current : data.capture_metrics);
      if (data.active_session_id) setActiveSessionId(data.active_session_id);
      if (data.capture_error) {
        setCaptureError((current: any) => sameSnapshot(current, data.capture_error) ? current : data.capture_error);
        setUiMessage(data.capture_error.message);
        if (data.capture_error.session_id) setActiveSessionId(data.capture_error.session_id);
      }
    } catch {
      setUiMessage('No se puede comunicar con el backend local.');
    }
  };

  const loadAdapterPorts = async () => {
    const response = await fetch('/api/adapter/ports', { cache: 'no-store' });
    if (!response.ok) return [] as AdapterPort[];
    const data = await response.json();
    const ports: AdapterPort[] = data.ports || [];
    setAdapterPorts(ports);
    return ports;
  };

  useEffect(() => {
    const savedMode = window.localStorage.getItem('micoche-experience-mode');
    if (savedMode === 'guided' || savedMode === 'professional') setExperienceMode(savedMode);
    if (!window.localStorage.getItem('micoche-onboarding-completed')) setShowOnboarding(true);
    const loadInitial = async () => {
      await refreshStatus();
      const [vehicleResponse, sessionResponse, profileResponse, portResponse] = await Promise.all([
        fetch('/api/vehicles'),
        fetch('/api/sessions/library'),
        fetch('/api/profiles'),
        loadAdapterPorts()
      ]);
      const recommendedPort = portResponse.find((port) => port.is_obdlink && !port.excluded);
      if (recommendedPort) setSelectedAdapterPort(recommendedPort.port);
      if (vehicleResponse.ok) {
        const list = await vehicleResponse.json();
        setVehicles(list);
        if (list.length) setSelectedVehicleId(list[0].id);
      }
      if (profileResponse.ok) setProfiles(await profileResponse.json());
      if (sessionResponse.ok) {
        const list = await sessionResponse.json();
        setSessions(list);
      }
    };
    loadInitial();
  }, []);

  useEffect(() => {
    if (showAddVehicle) return;
    const timer = setInterval(refreshStatus, 1000);
    return () => clearInterval(timer);
  }, [showAddVehicle]);

  useEffect(() => {
    window.localStorage.setItem('micoche-experience-mode', experienceMode);
    if (experienceMode === 'guided' && (activeTab === 'mode06' || activeTab === 'im')) {
      setActiveTab('live');
    }
  }, [experienceMode]);

  useEffect(() => {
    if (!isRecording) refreshSessionLibrary();
  }, [isRecording]);

  useEffect(() => {
    if (!isRecording) return;
    const warnBeforeClose = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', warnBeforeClose);
    return () => window.removeEventListener('beforeunload', warnBeforeClose);
  }, [isRecording]);

  useEffect(() => {
    if (!selectedVehicleId) {
      setVehicleSpec(null);
      setManufacturerProbe(null);
      setManufacturerCapabilities([]);
    }
    const controller = new AbortController();
    if (selectedVehicleId) {
      setVehicleSpec(null);
      fetch(`/api/vehicles/${selectedVehicleId}/spec`, { signal: controller.signal })
        .then(async (response) => {
          if (response.ok) setVehicleSpec(await response.json());
        })
        .catch(() => undefined);
      fetch(`/api/vehicles/${selectedVehicleId}/manufacturer-probe`, { signal: controller.signal, cache: 'no-store' })
        .then(async (response) => {
          if (response.ok) {
            const payload = await response.json();
            setManufacturerProbe(payload.last_probe || null);
            setManufacturerCapabilities(payload.capabilities || payload.last_probe?.live_signals || []);
          }
        })
        .catch(() => undefined);
    }
    const catalogUrl = selectedVehicleId
      ? `/api/vehicles/${selectedVehicleId}/metric-catalog`
      : '/api/metric-catalog';
    fetch(catalogUrl, { signal: controller.signal, cache: 'no-store' })
      .then(async (response) => {
        if (response.ok) {
          const payload = await response.json();
          setMetricCatalogCapabilities(payload.metrics || []);
        }
      })
      .catch(() => undefined);
    return () => controller.abort();
  }, [selectedVehicleId]);

  useEffect(() => {
    if (!selectedVehicleId || isRecording) return;
    const controller = new AbortController();
    let cancelled = false;
    const latest = sessions.find(
      (session) => session.vehicle_id === selectedVehicleId && session.status !== 'recording'
    );
    setActiveSessionId(latest?.id || null);
    setAnalysis(null);
    setSamples([]);
    setMarkers([]);
    setTelemetryValues({});
    if (!latest) {
      return () => controller.abort();
    }
    Promise.all([
      fetch(`/api/sessions/${latest.id}/analysis`, { signal: controller.signal, cache: 'no-store' }),
      fetch(`/api/sessions/${latest.id}/signals`, { signal: controller.signal, cache: 'no-store' }),
      fetch(`/api/sessions/${latest.id}/markers`, { signal: controller.signal, cache: 'no-store' })
    ]).then(async ([analysisResponse, signalsResponse, markersResponse]) => {
      const analysisPayload = analysisResponse.ok ? await analysisResponse.json() : null;
      const signalsPayload = signalsResponse.ok ? await signalsResponse.json() : null;
      const markersPayload = markersResponse.ok ? await markersResponse.json() : null;
      if (cancelled) return;
      if (analysisPayload) setAnalysis(analysisPayload);
      if (signalsResponse.ok) {
        const signalRows = signalsPayload?.samples || [];
        setSamples(downsampleTelemetry(signalRows));
        const latestValues: Record<string, number> = {};
        const latestTimes: Record<string, number> = {};
        signalRows.forEach((sample: any) => {
          if (typeof sample?.value !== 'number' || !Number.isFinite(sample.value)) return;
          const timestamp = Number(sample.timestamp_monotonic || 0);
          if (latestTimes[sample.pid] === undefined || timestamp >= latestTimes[sample.pid]) {
            latestTimes[sample.pid] = timestamp;
            latestValues[sample.pid] = sample.value;
          }
        });
        setTelemetryValues(latestValues);
      }
      if (markersPayload) setMarkers(markersPayload);
    }).catch(() => undefined);
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [selectedVehicleId, sessions, isRecording]);

  useEffect(() => {
    if (!isRecording) return;
    const loadLive = async () => {
      const response = await fetch('/api/live/snapshot', { cache: 'no-store' });
      if (!response.ok) return;
      const data = await response.json();
      setSamples(data.samples || []);
      setCaptureMetrics({
        ...(data.capture_metrics || {}),
        last_valid_age_sec: data.last_valid_age_sec,
        data_stale: data.data_stale,
        trip_metrics: data.trip_metrics
      });
      const values: Record<string, number> = {};
      Object.entries(data.latest || {}).forEach(([pid, sample]: [string, any]) => {
        if (typeof sample.value === 'number') values[pid] = sample.value;
      });
      setTelemetryValues(values);
      if (data.capture_error) setCaptureError(data.capture_error);
    };
    loadLive();
    const timer = setInterval(loadLive, 400);
    return () => clearInterval(timer);
  }, [isRecording, activeSessionId]);

  const handleConnectAdapter = async () => {
    setLoading(true);
    setUiMessage('Buscando adaptador y ECU…');
    try {
      const currentPorts = await loadAdapterPorts();
      const selectedPortInfo = currentPorts.find((port) => port.port === selectedAdapterPort);
      const recommendedPort = currentPorts.find((port) => port.is_obdlink && !port.excluded);
      const portToUse = (
        selectedPortInfo && !selectedPortInfo.excluded
          ? selectedPortInfo.port
          : recommendedPort?.port || ''
      );
      setSelectedAdapterPort(portToUse);
      const response = await fetch('/api/adapter/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ com_port: portToUse || null })
      });
      const data = await response.json();
      setAdapterStatus(data.status);
      if (!data.success) {
        setUiMessage(data.message || 'No se encontró una ECU operativa. Revisa contacto y puerto.');
      } else {
        const selectedVehicle = vehicles.find((vehicle) => vehicle.id === selectedVehicleId);
        const isVag = ['volkswagen', 'vw', 'audi', 'seat', 'skoda', 'škoda'].includes(String(selectedVehicle?.make || '').toLowerCase());
        if (isVag && selectedVehicleId) {
          setUiMessage('ECU detectada. Identificando la centralita Volkswagen con lecturas seguras…');
          const probeResponse = await fetch(`/api/vehicles/${selectedVehicleId}/manufacturer-probe`, { method: 'POST' });
          const probeData = await probeResponse.json();
          if (probeResponse.ok) {
            setManufacturerProbe(probeData);
            setManufacturerCapabilities(probeData.live_signals || []);
            const protocol = String(probeData.protocol || '').includes('KWP2000') ? 'KWP2000/TP2.0' : 'UDS';
            setUiMessage(probeData.probe_error
              ? `Centralita ${protocol} detectada, pero no se pudo abrir el canal ampliado: ${probeData.probe_error}`
              : probeData.vehicle_configuration_warning
                ? `${probeData.verified_live_signal_count} señales verificadas. ${probeData.vehicle_configuration_warning}`
                : probeData.identified
                  ? `Centralita Volkswagen identificada por ${protocol}. ${probeData.verified_live_signal_count} señales propietarias verificadas.`
                  : `OBD genérico conectado; identificación Volkswagen ${protocol} pendiente.`);
          } else {
            setUiMessage(probeData.detail || 'Adaptador conectado; no se pudo completar la identificación Volkswagen.');
          }
        } else {
          setUiMessage('Adaptador conectado y ECU detectada.');
        }
        if (selectedVehicleId) {
          const catalogResponse = await fetch(`/api/vehicles/${selectedVehicleId}/metric-catalog`, { cache: 'no-store' });
          if (catalogResponse.ok) {
            const catalogPayload = await catalogResponse.json();
            setMetricCatalogCapabilities(catalogPayload.metrics || []);
          }
        }
      }
    } catch {
      setUiMessage('No se pudo conectar con el adaptador.');
    } finally {
      setLoading(false);
    }
  };

  const handleScanDtc = async () => {
    if (!selectedVehicleId) return;
    setLoading(true);
    try {
      const response = await fetch(`/api/dtc/scan?vehicle_id=${selectedVehicleId}`);
      const data = await response.json();
      if (response.ok) {
        setDtcs(data.dtcs || []);
        setUiMessage(data.dtcs?.length ? `${data.dtcs.length} códigos leídos de la ECU.` : 'La ECU no informa de códigos DTC.');
      } else {
        setUiMessage(data.detail || 'No se pudo leer los DTC.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleStartSession = async (
    profileId = selectedProfileId,
    context?: GuidedSessionContext
  ) => {
    if (!selectedVehicleId) return;
    setLoading(true);
    setPreflight(null);
    setCaptureError(null);
    setAnalysis(null);
    setUiMessage('Validando conexión y señales compatibles…');
    try {
      const preflightResponse = await fetch(`/api/diagnostics/preflight?vehicle_id=${selectedVehicleId}`);
      const preflightData = await preflightResponse.json();
      setPreflight(preflightData);
      if (!preflightResponse.ok || !preflightData.ready) {
        setUiMessage(preflightData.message || preflightData.detail || 'La prevalidación no se ha superado.');
        return;
      }
      const profile = profiles.find((item) => item.id === profileId);
      const response = await fetch('/api/sessions/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vehicle_id: selectedVehicleId,
          profile_id: profileId,
          engine_condition: context?.engineCondition || 'warm',
          notes: profile?.name || 'Diagnóstico OBD-II guiado',
          title: context?.title || profile?.name || 'Diagnóstico OBD-II guiado',
          symptom: context?.symptom || '',
          odometer_km: context?.odometerKm
        })
      });
      const data = await response.json();
      if (!response.ok) {
        setUiMessage(data.detail || 'No se pudo iniciar la captura.');
        return;
      }
      setSelectedProfileId(profileId);
      setActiveSessionId(data.id);
      setIsRecording(true);
      setSamples([]);
      setTelemetryValues({});
      setMarkers([]);
      setSessions((current) => [data, ...current]);
      setUiMessage('Captura validada e iniciada. Sigue las instrucciones del protocolo.');
    } catch {
      setUiMessage('Error durante la prevalidación del diagnóstico.');
    } finally {
      setLoading(false);
    }
  };

  const handleStopSession = async () => {
    if (!activeSessionId) return;
    setLoading(true);
    try {
      const response = await fetch(`/api/sessions/${activeSessionId}/stop`, { method: 'POST' });
      const data = await response.json();
      if (!response.ok) {
        setUiMessage(data.detail || 'No se pudo detener la sesión.');
        return;
      }
      setIsRecording(false);
      const analysisResponse = await fetch(`/api/sessions/${activeSessionId}/analysis`);
      if (analysisResponse.ok) setAnalysis(await analysisResponse.json());
      const captured = data.capture_summary?.captured_signal_count ?? data.captured_signal_count ?? 0;
      const requested = data.capture_summary?.requested_signal_count ?? data.requested_signal_count ?? 0;
      setUiMessage(`Prueba finalizada y analizada. Se guardaron datos de ${captured}/${requested} señales solicitadas.`);
      await refreshSessionLibrary();
    } finally {
      setLoading(false);
    }
  };

  const handleMarkEvent = async (type: string, note?: string) => {
    if (!activeSessionId) return;
    const lastSample = samples[samples.length - 1];
    const offsetMs = lastSample ? Math.round(lastSample.timestamp_monotonic * 1000) : 0;
    const response = await fetch(`/api/sessions/${activeSessionId}/markers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ timestamp_offset_ms: offsetMs, event_type: type, note: note || type })
    });
    if (response.ok) {
      const marker = await response.json();
      setMarkers((current) => [...current, marker]);
    }
  };

  const handleVehicleCreated = (vehicle: CreatedVehicle) => {
    setVehicles((current) => [vehicle, ...current]);
    setSelectedVehicleId(vehicle.id);
    setUiMessage(`${vehicle.display_name} se ha añadido al garaje.`);
  };

  const currentVehicle = vehicles.find((vehicle) => vehicle.id === selectedVehicleId);
  const gaugeCapabilities = useMemo(() => {
    const combined = [...metricCatalogCapabilities, ...manufacturerCapabilities, ...(preflight?.supported_pids || [])];
    const byPid = new Map<string, any>();
    combined.forEach((item) => {
      if (!item?.pid_name) return;
      const previous = byPid.get(item.pid_name);
      if (!previous) {
        byPid.set(item.pid_name, item);
      } else if (item.supported_verified || !previous.supported_verified) {
        byPid.set(item.pid_name, {
          ...previous,
          ...item,
          importance: Math.max(Number(previous.importance || 0), Number(item.importance || 0))
        });
      }
    });
    return Array.from(byPid.values());
  }, [metricCatalogCapabilities, manufacturerCapabilities, preflight]);
  const currentVehicleSessions = sessions.filter(
    (session) => session.vehicle_id === selectedVehicleId && session.status !== 'recording'
  );
  const activeSession = sessions.find((session) => session.id === activeSessionId);
  const liveDataSources = useMemo(
    () => Array.from(new Set(samples.map((sample) => sample.data_source).filter(Boolean))),
    [samples]
  );
  const coverage = (() => {
    switch (vehicleSpec?.confidence_tier) {
      case 'OEM_CONFIRMED':
        return { className: 'oem', label: 'Ficha específica confirmada' };
      case 'VEHICLE_BASELINE':
        return { className: 'baseline', label: 'Línea base aprendida' };
      case 'USER_DEFINED':
        return { className: 'custom', label: 'Límites personalizados' };
      case 'ENGINE_IDENTIFICATION_REQUIRED':
        return { className: 'pending', label: 'Motor pendiente de identificar' };
      case 'GENERIC_ENGINEERING_RANGE':
        return { className: 'generic', label: 'Cobertura OBD genérica' };
      default:
        return { className: 'loading', label: 'Comprobando cobertura…' };
    }
  })();
  const navItems: Array<{ id: TabId; label: string; icon: LucideIcon }> = [
    { id: 'live', label: 'Diagnóstico', icon: Activity },
    { id: 'sessions', label: 'Sesiones', icon: History },
    { id: 'ai', label: 'Asistente de diagnóstico', icon: Bot },
    { id: 'compare', label: 'Antes / Después', icon: Scale },
    { id: 'garage', label: 'Garaje', icon: Wrench },
    { id: 'im', label: 'ITV / Monitores', icon: ShieldCheck },
    { id: 'mode06', label: 'Modo 06', icon: ScanLine }
  ];
  const visibleNavItems = experienceMode === 'professional'
    ? navItems
    : navItems.filter((item) => !['mode06', 'im'].includes(item.id));

  return (
    <div className="dashboard-shell">
      <Header
        adapterState={adapterStatus.state}
        vehicleName={currentVehicle ? `${currentVehicle.make} ${currentVehicle.model}` : undefined}
        isRecording={isRecording}
        elapsedSec={captureMetrics?.elapsed_sec || 0}
      />

      <div className="dashboard-content">
        <ExperienceModeSwitch
          mode={experienceMode}
          onChange={setExperienceMode}
          onOpenHelp={() => setShowOnboarding(true)}
        />
        <TrustStatusBar
          isRecording={isRecording}
          adapterConnected={Boolean(adapterStatus.is_connected)}
          captureMetrics={captureMetrics}
          dataSources={isRecording ? liveDataSources : activeSession?.data_sources}
          coverageLabel={coverage.label}
          activeSessionTitle={activeSession?.title || activeSession?.notes}
        />
        <ConnectionMetricsBar
          adapterState={adapterStatus.state}
          port={adapterStatus.port || 'Sin puerto verificado'}
          protocol={adapterStatus.protocol || 'Protocolo pendiente'}
          latencyMs={adapterStatus.latency_ms || 0}
          sampleRateHz={
            captureMetrics?.elapsed_sec > 0
              ? Math.round((captureMetrics.valid_sample_count / captureMetrics.elapsed_sec) * 10) / 10
              : undefined
          }
          successRatePct={
            captureMetrics ? Math.round((captureMetrics.valid_ratio || 0) * 1000) / 10 : undefined
          }
          ecuVoltage={telemetryValues.CONTROL_MODULE_VOLTAGE ?? telemetryValues.ELM_VOLTAGE}
        />

        <section className="control-console" aria-label="Controles de sesión">
          <div className="control-group">
            <div className="control-field">
              <label className="control-label" htmlFor="vehicle-profile">Vehículo del garaje</label>
              <div className="vehicle-selector-row">
                <select
                  id="vehicle-profile"
                  className="race-select"
                  value={selectedVehicleId}
                  onChange={(event) => setSelectedVehicleId(event.target.value)}
                  disabled={isRecording}
                >
                  {vehicles.map((vehicle) => (
                    <option key={vehicle.id} value={vehicle.id}>
                      {vehicle.display_name} // {vehicle.make} {vehicle.model}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  className="race-button race-button--add"
                  onClick={() => setShowAddVehicle(true)}
                  disabled={isRecording}
                >
                  <Plus size={17} />
                  Añadir vehículo
                </button>
              </div>
              {selectedVehicleId && (
                <span className={`vehicle-coverage vehicle-coverage--${coverage.className}`}>
                  <span aria-hidden="true" />
                  {t(coverage.label)}
                </span>
              )}
            </div>
            <div className="control-field">
              <label className="control-label" htmlFor="adapter-port">Puerto del adaptador</label>
              <select
                id="adapter-port"
                className="race-select"
                value={selectedAdapterPort}
                onChange={(event) => setSelectedAdapterPort(event.target.value)}
                disabled={loading || isRecording || adapterStatus.is_connected}
              >
                {!adapterPorts.length && <option value="">Ningún adaptador USB detectado</option>}
                {adapterPorts.map((port) => (
                  <option key={port.port} value={port.port} disabled={port.excluded}>
                    {port.port} · {port.description}
                    {port.is_obdlink && !port.excluded ? ` · ${t('recomendado')}` : ''}
                    {port.excluded ? ` · ${t('no es OBD')}` : ''}
                  </option>
                ))}
              </select>
            </div>
            <button onClick={handleConnectAdapter} disabled={loading || isRecording} className="race-button race-button--connect">
              <PlugZap size={17} />
              Conectar OBD
            </button>
          </div>

          <div className="control-group">
            {activeSessionId && (
              <a href={`/api/sessions/${activeSessionId}/report?lang=${language}`} target="_blank" rel="noreferrer" className="race-button report-link">
                <FileText size={16} />
                Informe
                <ExternalLink size={13} />
              </a>
            )}
            {!isRecording ? (
              <button onClick={() => handleStartSession('COMPLETE_DIAGNOSTIC')} disabled={!selectedVehicleId || loading} className="race-button race-button--start">
                <Play size={17} fill="currentColor" />
                Diagnóstico completo
              </button>
            ) : (
              <button onClick={handleStopSession} className="race-button race-button--stop">
                <Square size={17} fill="currentColor" />
                Finalizar y analizar
              </button>
            )}
          </div>
        </section>

        {(uiMessage || preflight) && (
          <div className={`operation-banner${preflight && !preflight.ready ? ' error' : ''}`}>
            {preflight && !preflight.ready ? <TriangleAlert size={18} /> : <CheckCircle2 size={18} />}
            <div>
              <strong>{uiMessage}</strong>
              {preflight?.checks && (
                <span>{preflight.checks.map((check: any) => `${check.ok ? '✓' : '×'} ${check.label}`).join('  ·  ')}</span>
              )}
              {manufacturerProbe && (
                <span>
                  Volkswagen {String(manufacturerProbe.protocol || '').includes('KWP2000') ? 'KWP2000/TP2.0' : 'UDS'}: {manufacturerProbe.identified ? 'centralita identificada' : 'identificación pendiente'}
                  {' · '}{manufacturerProbe.verified_live_signal_count || 0} señales propietarias verificadas
                  {manufacturerProbe.tested_group_count ? ` · ${manufacturerProbe.responding_group_count || 0}/${manufacturerProbe.documented_group_count || manufacturerProbe.tested_group_count} bloques responden` : ''}
                  {manufacturerProbe.coverage_percent !== undefined ? ` · ${manufacturerProbe.coverage_percent}% de cobertura real` : ''}
                  {manufacturerProbe.mapping_required_count ? ` · ${manufacturerProbe.mapping_required_count} pendientes` : ''}
                  {' · '}solo lectura
                </span>
              )}
            </div>
          </div>
        )}

        <nav className="race-nav" aria-label="Módulos principales">
          {visibleNavItems.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.id} className={`nav-button${activeTab === item.id ? ' active' : ''}`} onClick={() => setActiveTab(item.id)}>
                <Icon size={16} />
                {item.label}
              </button>
            );
          })}
        </nav>

        {activeTab === 'live' && (
          <>
            {experienceMode === 'guided' && !isRecording && (
              <SymptomGuide
                profiles={profiles}
                loading={loading}
                disabled={!selectedVehicleId}
                onStart={handleStartSession}
              />
            )}
            {(experienceMode === 'professional' || isRecording) && (
              <GuidedTestWizard
                profiles={profiles}
                selectedProfileId={selectedProfileId}
                onSelectProfile={setSelectedProfileId}
                onStartTest={handleStartSession}
                isRecording={isRecording}
                elapsedSec={captureMetrics?.elapsed_sec || 0}
                loading={loading}
              />
            )}
            <DiagnosticSummaryPanel
              analysis={analysis}
              values={telemetryValues}
              isRecording={isRecording}
              captureMetrics={captureMetrics}
              captureError={captureError}
              experienceMode={experienceMode}
            />
            <TelemetryGaugesGrid
              values={telemetryValues}
              capabilities={gaugeCapabilities}
              isConnected={Boolean(adapterStatus?.is_connected)}
              powertrainType={currentVehicle?.powertrain_type}
              engineCode={currentVehicle?.engine_code}
              tripMetrics={captureMetrics?.trip_metrics || analysis?.trip_metrics}
            />
            <EventMarkerBar onMarkEvent={handleMarkEvent} disabled={!isRecording} />
            <DtcPanel dtcs={dtcs} onScanDtc={handleScanDtc} loading={loading} />
            {dtcs.length > 0 && (
              <FreezeFrameInspector
                dtcCode={dtcs[0].code}
                freezeFrameParams={dtcs[0].freeze_frame || []}
              />
            )}
            <TelemetryChart samples={samples} markers={markers} professional={experienceMode === 'professional'} />
          </>
        )}

        {activeTab === 'sessions' && (
          <SessionsLibrary
            sessions={sessions}
            vehicles={vehicles}
            selectedVehicleId={selectedVehicleId}
            mode={experienceMode}
            loading={sessionsLoading}
            onRefresh={refreshSessionLibrary}
            onAnalyze={(sessionId) => {
              setActiveSessionId(sessionId);
              setActiveTab('ai');
            }}
            onCompare={(sessionId) => {
              setComparisonBaseId(sessionId);
              setActiveTab('compare');
            }}
            onUpdated={(updated) => {
              setSessions((current) => current.map((session) => session.id === updated.id ? updated : session));
            }}
          />
        )}

        {activeTab === 'ai' && (
          <AiAssistantPanel
            sessionId={activeSessionId || undefined}
            sessions={currentVehicleSessions}
            onSelectSession={setActiveSessionId}
            isRecording={isRecording}
            onStartTest={handleStartSession}
            onOpenEvidence={() => {
              setActiveTab('live');
              setTimeout(() => document.querySelector('.telemetry-grid')?.scrollIntoView({ behavior: 'smooth' }), 50);
            }}
          />
        )}
        {activeTab === 'compare' && (
          <SessionComparator sessions={currentVehicleSessions} initialBaseSessionId={comparisonBaseId} />
        )}
        {activeTab === 'garage' && (
          <GaragePanel
            vehicleId={selectedVehicleId}
            vehicleName={currentVehicle ? `${currentVehicle.display_name} (${currentVehicle.make} ${currentVehicle.model})` : 'Vehículo'}
          />
        )}
        {activeTab === 'im' && <ImReadinessPanel vehicleId={selectedVehicleId} />}
        {activeTab === 'mode06' && <Mode06Panel vehicleId={selectedVehicleId} />}
      </div>
      <AddVehicleDialog
        open={showAddVehicle}
        onClose={() => setShowAddVehicle(false)}
        onCreated={handleVehicleCreated}
      />
      <OnboardingDialog
        open={showOnboarding}
        onChooseMode={setExperienceMode}
        onClose={() => {
          window.localStorage.setItem('micoche-onboarding-completed', '1');
          setShowOnboarding(false);
        }}
      />
    </div>
  );
}
