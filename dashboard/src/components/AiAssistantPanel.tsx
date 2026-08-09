'use client';

import React, { FormEvent, useEffect, useMemo, useState } from 'react';
import {
  AlertOctagon,
  Bot,
  Car,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  Database,
  Gauge,
  MessageSquareText,
  Mic,
  Send,
  ShieldAlert,
  Sparkles,
  Trash2,
  TriangleAlert,
  Wrench
} from 'lucide-react';
import { telemetryLabel } from '@/lib/telemetryLabels';
import { useI18n } from '@/lib/i18n';

interface AiAssistantPanelProps {
  sessionId?: string;
  sessions?: Array<{ id: string; started_at: string; title?: string; symptom?: string; notes?: string; status: string }>;
  onSelectSession?: (sessionId: string) => void;
  isRecording?: boolean;
  onStartTest?: (profileId: string) => void;
  onOpenEvidence?: (pid?: string) => void;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text?: string;
  data?: any;
  createdAt: string;
}

const QUICK_QUESTIONS = [
  '¿Qué está mal en esta sesión?',
  '¿Puedo seguir circulando?',
  'El coche da tirones al acelerar',
  '¿Qué debería revisar primero?',
  'Prepara un resumen para el taller'
];

const MODE_LABELS: Record<string, string> = {
  simple: 'Conductor',
  technical: 'Técnico',
  workshop: 'Taller'
};

export const AiAssistantPanel: React.FC<AiAssistantPanelProps> = ({
  sessionId,
  sessions = [],
  onSelectSession,
  isRecording = false,
  onStartTest,
  onOpenEvidence
}) => {
  const { language, locale, speechLocale, t } = useI18n();
  const [context, setContext] = useState<any>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState('');
  const [mode, setMode] = useState('simple');
  const [engine, setEngine] = useState<'local' | 'generative'>('local');
  const [aiStatus, setAiStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [historyReady, setHistoryReady] = useState(false);

  const storageKey = sessionId ? `micoche-ai-chat:${sessionId}` : '';

  useEffect(() => {
    fetch('/api/ai/status')
      .then((response) => response.json())
      .then(setAiStatus)
      .catch(() => setAiStatus(null));
  }, []);

  useEffect(() => {
    setContext(null);
    setHistoryReady(false);
    if (!sessionId) {
      setMessages([]);
      return;
    }
    const saved = window.localStorage.getItem(storageKey);
    try {
      setMessages(saved ? JSON.parse(saved) : []);
    } catch {
      setMessages([]);
    }
    setHistoryReady(true);
    if (isRecording) return;
    fetch(`/api/sessions/${sessionId}/assistant-context`)
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'No se pudo cargar la sesión.');
        setContext(data);
      })
      .catch((cause) => setError(cause.message));
  }, [sessionId, storageKey, isRecording]);

  useEffect(() => {
    if (historyReady && storageKey) {
      window.localStorage.setItem(storageKey, JSON.stringify(messages.slice(-30)));
    }
  }, [messages, historyReady, storageKey]);

  const lastAssistantData = useMemo(
    () => [...messages].reverse().find((message) => message.role === 'assistant' && message.data)?.data,
    [messages]
  );

  const ask = async (text: string) => {
    const clean = text.trim();
    if (!sessionId || !clean || loading) return;
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      text: clean,
      createdAt: new Date().toISOString()
    };
    setMessages((current) => [...current, userMessage]);
    setQuestion('');
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`/api/sessions/${sessionId}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: clean,
          mode,
          engine,
          allow_remote: engine === 'generative',
          language,
          conversation_history: messages.slice(-12).map((message) => ({
            role: message.role,
            content: message.text || message.data?.answer || ''
          }))
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'No se pudo analizar la pregunta.');
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          data,
          createdAt: new Date().toISOString()
        }
      ]);
    } catch (cause: any) {
      setError(cause.message || 'Error consultando el asistente.');
    } finally {
      setLoading(false);
    }
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    ask(question);
  };

  const startVoice = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('El reconocimiento de voz no está disponible en este equipo.');
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = speechLocale;
    recognition.interimResults = false;
    recognition.onresult = (event: any) => setQuestion(event.results[0][0].transcript);
    recognition.onerror = () => setError('No se pudo reconocer la voz.');
    recognition.start();
  };

  const clearHistory = () => {
    setMessages([]);
    if (storageKey) window.localStorage.removeItem(storageKey);
  };

  if (!sessionId) {
    return (
      <section className="race-panel ai-empty-state">
        <Bot size={38} />
        <h3>Asistente de diagnóstico</h3>
        <p>Finaliza una sesión con datos válidos para explicar el problema con tus propias palabras.</p>
      </section>
    );
  }

  return (
    <section className="ai-workspace">
      <header className="ai-workspace__header">
        <div>
          <span className="section-kicker">Asistente técnico // conversación con evidencias</span>
          <h2><Bot size={24} /> Asistente de diagnóstico</h2>
          <p>Cuéntame qué notas. Separaré hechos medidos, posibilidades y siguientes comprobaciones.</p>
        </div>
        <div className="ai-mode-switch" aria-label="Nivel de explicación">
          {Object.entries(MODE_LABELS).map(([id, label]) => (
            <button key={id} className={mode === id ? 'active' : ''} onClick={() => setMode(id)}>
              {label}
            </button>
          ))}
        </div>
      </header>

      <div className="ai-engine-choice">
        <div>
          <strong>Motor de respuesta</strong>
          <span>
            {engine === 'local'
              ? 'Análisis local verificable: los datos no salen del equipo.'
              : 'Añade una explicación generativa, manteniendo intactos los resultados OBD locales.'}
          </span>
        </div>
        <div className="ai-mode-switch" aria-label="Motor de respuesta">
          <button
            className={engine === 'local' ? 'active' : ''}
            onClick={() => setEngine('local')}
          >
            Local verificable
          </button>
          <button
            className={engine === 'generative' ? 'active' : ''}
            onClick={() => setEngine('generative')}
            disabled={!aiStatus?.available}
            title={aiStatus?.message}
          >
            Explicación generativa
          </button>
        </div>
        <small>{aiStatus?.message || 'Comprobando configuración de IA…'}</small>
      </div>

      <div className="ai-layout">
        <aside className="ai-context-column">
          <div className="ai-side-title"><Car size={16} /> Contexto real</div>
          <label className="ai-session-selector">
            <span>Sesión analizada</span>
            <select
              value={sessionId || ''}
              onChange={(event) => onSelectSession?.(event.target.value)}
              disabled={isRecording || sessions.length < 2}
            >
              {sessions.map((session) => (
                <option key={session.id} value={session.id}>
                  {new Date(session.started_at).toLocaleString(locale)} · {session.title || session.notes || t('Prueba sin título')}
                </option>
              ))}
            </select>
          </label>
          <div className="ai-data-scope">
            <span>Alcance de la respuesta</span>
            <strong>Una única sesión</strong>
            <p>{context?.scope?.message || (isRecording ? 'Finaliza la captura para analizar todos sus datos.' : 'Cargando el alcance de los datos…')}</p>
            {context?.session?.started_at && (
              <small>
                {t('Inicio')}: {new Date(context.session.started_at).toLocaleString(locale)} · {context.scope.sample_count} {t('lecturas')}
              </small>
            )}
            {context?.scope?.dtc_scope && <small>DTC: {context.scope.dtc_scope}</small>}
            {context?.scope?.symptom_scope && <small>Síntoma: {context.scope.symptom_scope}</small>}
            {context?.scope?.conversation_scope && <small>Conversación: {context.scope.conversation_scope}</small>}
            {context?.scope?.baseline_scope && <small>Histórico: {context.scope.baseline_scope}</small>}
            {context?.scope?.assistant_engine && <small>Motor: {context.scope.assistant_engine}</small>}
            {context?.scope?.data_sources?.simulated > 0 && <em>Esta sesión contiene datos simulados.</em>}
          </div>
          <div className="ai-context-card">
            <span>Vehículo</span>
            <strong>{context?.vehicle?.display_name || 'Cargando…'}</strong>
          </div>
          {context?.session?.symptom && (
            <div className="ai-context-card ai-context-card--symptom">
              <span>Motivo guardado de la prueba</span>
              <strong>{context.session.symptom}</strong>
            </div>
          )}
          <div className="ai-context-stats">
            <div><Database size={15} /><span>Señales</span><strong>{context?.signal_count ?? '--'}</strong></div>
            <div><Gauge size={15} /><span>Calidad</span><strong>{context?.quality?.overall_score ?? '--'}%</strong></div>
            <div><ShieldAlert size={15} /><span>DTC</span><strong>{context?.dtcs?.length ?? '--'}</strong></div>
          </div>
          <div className="ai-context-card">
            <span>Referencia del propio coche</span>
            <strong>
              {context?.historical_baseline?.available
                ? `${context.historical_baseline.qualifying_session_count} sesiones válidas`
                : `Aprendiendo · faltan ${context?.historical_baseline?.remaining_session_count ?? 3}`}
            </strong>
          </div>
          {context?.conclusion && (
            <div className={`ai-session-verdict ai-session-verdict--${context.conclusion.verdict}`}>
              <span>Resultado de sesión</span>
              <strong>{context.conclusion.title}</strong>
              <p>{context.conclusion.summary}</p>
            </div>
          )}
          <div className="ai-coverage">
            <span>Datos disponibles</span>
            <div>
              {context?.available_signals?.slice(0, 10).map((pid: string) => <small key={pid}>{telemetryLabel(pid)}</small>)}
              {!context?.available_signals?.length && <em>Sin señales válidas</em>}
            </div>
          </div>
          <button className="ai-clear-button" onClick={clearHistory} disabled={!messages.length}>
            <Trash2 size={14} /> Borrar conversación
          </button>
        </aside>

        <main className="ai-chat-column">
          <div className="ai-quick-prompts">
            {QUICK_QUESTIONS.map((prompt) => (
              <button key={prompt} onClick={() => ask(prompt)} disabled={loading || isRecording}>
                <Sparkles size={13} /> {prompt}
              </button>
            ))}
          </div>

          <div className="ai-conversation" aria-live="polite">
            {isRecording && (
              <div className="ai-recording-notice">
                <TriangleAlert size={22} />
                <strong>Captura en curso</strong>
                <p>Finaliza la prueba antes de preguntar. Así la respuesta utilizará la sesión completa y no un archivo parcial.</p>
              </div>
            )}
            {messages.length === 0 && (
              <div className="ai-welcome">
                <MessageSquareText size={28} />
                <strong>Explícame el problema como tú lo dirías</strong>
                <p>Por ejemplo: “al acelerar en tercera da un tirón y pierde fuerza”. Usaré únicamente la sesión indicada en el panel de contexto.</p>
              </div>
            )}

            {messages.map((message) => (
              <article key={message.id} className={`chat-message chat-message--${message.role}`}>
                {message.role === 'user' ? (
                  <p>{message.text}</p>
                ) : (
                  <AssistantAnswer
                    data={message.data}
                    onAsk={ask}
                    onStartTest={onStartTest}
                    isRecording={isRecording}
                  />
                )}
              </article>
            ))}
            {loading && (
              <div className="ai-thinking"><Bot size={17} /> Cruzando tu descripción con DTC, sensores y reglas…</div>
            )}
          </div>

          {error && <div className="ai-error"><TriangleAlert size={16} /> {error}</div>}

          <form className="ai-composer" onSubmit={submit}>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Describe el síntoma con tus palabras…"
              rows={3}
              disabled={loading || isRecording}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault();
                  ask(question);
                }
              }}
            />
            <div className="ai-composer__actions">
              <button type="button" className="voice-button" onClick={startVoice} title="Dictar síntoma">
                <Mic size={17} />
              </button>
              <span>Intro para enviar · Mayús+Intro para nueva línea</span>
              <button type="submit" className="send-button" disabled={!question.trim() || loading || isRecording}>
                <Send size={16} /> Analizar
              </button>
            </div>
          </form>
        </main>

        <aside className="ai-evidence-column">
          <div className="ai-side-title"><Database size={16} /> Evidencias citadas</div>
          {!lastAssistantData?.evidence?.length ? (
            <div className="ai-no-evidence">
              <CircleHelp size={22} />
              <p>Las evidencias de la última respuesta aparecerán aquí con sus valores exactos.</p>
            </div>
          ) : (
            lastAssistantData.evidence.map((item: any) => (
              <button
                className="evidence-card"
                key={item.id}
                onClick={() => onOpenEvidence?.(item.pid)}
              >
                <span>{item.id}</span>
                <strong>{telemetryLabel(item.pid)}</strong>
                <div>
                  <small>MÍN {item.min}</small>
                  <small>MEDIA {item.mean}</small>
                  <small>MÁX {item.max}</small>
                </div>
                <em>Ver en telemetría <ChevronRight size={12} /></em>
              </button>
            ))
          )}
          {lastAssistantData?.missing_data?.length > 0 && (
            <div className="missing-data-card">
              <strong>Datos que faltan</strong>
              {lastAssistantData.missing_data.map((pid: string) => <span key={pid}>{telemetryLabel(pid)}</span>)}
            </div>
          )}
        </aside>
      </div>
    </section>
  );
};

const AssistantAnswer = ({
  data,
  onAsk,
  onStartTest,
  isRecording
}: {
  data: any;
  onAsk: (question: string) => void;
  onStartTest?: (profileId: string) => void;
  isRecording: boolean;
}) => {
  const urgencyIcon = data.urgency?.level === 'stop' ? AlertOctagon : data.urgency?.level === 'soon' ? TriangleAlert : CheckCircle2;
  const UrgencyIcon = urgencyIcon;
  return (
    <div className="assistant-answer">
      <div className={`answer-urgency answer-urgency--${data.urgency?.level || 'unknown'}`}>
        <UrgencyIcon size={18} />
        <div><strong>{data.urgency?.label}</strong><span>{data.urgency?.message}</span></div>
      </div>
      <p className="answer-summary">{data.answer}</p>

      {data.generative_explanation && (
        <div className="answer-generative">
          <strong><Sparkles size={15} /> Explicación generativa acotada</strong>
          <p>{data.generative_explanation}</p>
          <small>{data.generative_status}</small>
        </div>
      )}

      {data.data_basis && (
        <div className="answer-data-basis">
          <div>
            <Database size={16} />
            <span>Base exacta de esta respuesta</span>
            <strong>
              {data.data_basis.sample_count} lecturas · {data.data_basis.valid_signal_count} señales OBD · {data.data_basis.relevant_finding_count} hallazgos relacionados
            </strong>
          </div>
          <small>{data.data_basis.dtc_scope}</small>
          {data.context_used?.length > 0 && (
            <details>
              <summary>Ver todo el contexto utilizado</summary>
              <ul>{data.context_used.map((item: string) => <li key={item}>{item}</li>)}</ul>
            </details>
          )}
        </div>
      )}

      <div className="answer-section">
        <h4><CheckCircle2 size={15} /> Lo que sabemos</h4>
        <ul>{data.facts?.map((fact: string, index: number) => <li key={index}>{fact}</li>)}</ul>
      </div>

      <div className="answer-section">
        <h4><CircleHelp size={15} /> Posibles causas — no confirmadas</h4>
        {data.hypotheses?.map((hypothesis: any, index: number) => (
          <div className="hypothesis-row" key={index}>
            <div><strong>{hypothesis.title}</strong><p>{hypothesis.basis}</p></div>
            <span>{Math.round(hypothesis.confidence * 100)}% indicio</span>
          </div>
        ))}
      </div>

      <div className="answer-section">
        <h4><Wrench size={15} /> Cómo avanzar sin cambiar piezas a ciegas</h4>
        <div className="solution-grid">
          {data.solutions?.map((solution: any) => (
            <article key={solution.level} className={`solution-card solution-card--${solution.level}`}>
              <strong>{solution.title}</strong>
              <ul>{solution.steps.map((step: string, index: number) => <li key={index}>{step}</li>)}</ul>
              <small>{solution.warning}</small>
            </article>
          ))}
        </div>
      </div>

      {data.recommended_test && (
        <div className="recommended-test">
          <div><span>Siguiente prueba recomendada</span><strong>{data.recommended_test.name}</strong><p>{data.recommended_test.reason}</p></div>
          <button
            className="race-button race-button--start"
            onClick={() => onStartTest?.(data.recommended_test.profile_id)}
            disabled={!onStartTest || isRecording}
          >
            Iniciar prueba
          </button>
        </div>
      )}

      <div className="follow-up-chips">
        {data.follow_up_questions?.map((followUp: string) => (
          <button key={followUp} onClick={() => onAsk(followUp)}>{followUp}</button>
        ))}
      </div>
      <p className="answer-disclaimer">{data.disclaimer}</p>
    </div>
  );
};
