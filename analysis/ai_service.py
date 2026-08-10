"""
Capa de Inteligencia Artificial Estructurada para 'Mi Coche por Dentro'.
Recibe contexto anonimizado, estadísticas de telemetría, DTCs y hallazgos del motor de reglas,
y genera análisis explicativos estructurados sin alucinaciones.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from analysis.spec_resolver import SpecResolver
from analysis.coherence_rules import PhysicalCoherenceValidator

logger = logging.getLogger(__name__)

class AiAnalysisResponse(BaseModel):
    observed_facts: List[str] = Field(description="Datos y evidencias reales observados en los sensores y DTCs")
    evidence_ids: List[str] = Field(default_factory=list, description="Lista de identificadores de evidencia citados (ej: EV-001)")
    mathematical_anomalies: List[str] = Field(description="Anomalías matemáticas calculadas previamente")
    hypotheses: List[str] = Field(description="Hipótesis técnicas ordenadas por probabilidad")
    recommended_checks: List[str] = Field(description="Comprobaciones mecánicas o eléctricas recomendadas")
    missing_data: List[str] = Field(description="PIDs o mediciones ausentes necesarias para confirmar las hipótesis")
    confidence_level: float = Field(description="Nivel de confianza global entre 0.0 y 1.0")
    warnings: List[str] = Field(description="Advertencias de seguridad o precauciones durante las pruebas")


SYSTEM_PROMPT = """
Eres el asistente especializado de diagnóstico automotriz e ingeniería de telemetría para la aplicación 'Mi Coche por Dentro'.
Tu objetivo es analizar la información estructurada proporcionada (DTCs, marcas temporales, estadísticas de telemetría, eventos de tirones y el NIVEL DE CONFIANZA DE LAS ESPECIFICACIONES TÉCNICAS).

REGLAS DE OBLIGADO CUMPLIMIENTO:
1. Revisa el nivel de confianza ('confidence_tier'):
   - Si es 'OEM_CONFIRMED', compara los valores medidos contra la Ficha Técnica Oficial validada por código de motor.
   - Si es 'GENERIC_ENGINEERING_RANGE', aclara explícitamente que el coche está en Cobertura Genérica OBD-II Nivel 1 y que los rangos son aproximaciones conservadoras.
2. Filtra PIDs incoherentes: NUNCA evalúes Fuel Trims de gasolina en diésel ni DPF/RPM en vehículos eléctricos.
3. Distingue estrictamente HECHOS MEDIDOS de HIPÓTESIS.
"""

class AIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")

    def generative_status(self) -> Dict[str, Any]:
        provider = os.getenv("AI_PROVIDER", "disabled").lower()
        enabled = provider == "openai" and bool(self.openai_api_key)
        return {
            "available": enabled,
            "provider": "OpenAI" if enabled else "Motor local",
            "configured_provider": provider,
            "model": self.openai_model if enabled else None,
            "default_engine": "local",
            "sends_data_outside_device": enabled,
            "message": (
                "La explicación generativa está disponible y requiere autorización en cada consulta."
                if enabled
                else (
                    "El motor local verificable está activo. La IA generativa es opcional "
                    "y permanece desactivada hasta configurar AI_PROVIDER=openai y una clave."
                )
            ),
        }

    def build_context_prompt(self, vehicle_info: Dict[str, Any], dtcs: List[Dict[str, Any]],
                             stats: Dict[str, Any], rule_findings: List[Dict[str, Any]],
                             symptom_note: Optional[str] = None, event_impacts: Optional[List[Dict[str, Any]]] = None) -> str:
        """Construye el prompt estructurado en JSON aplicando SpecResolver y CoherenceValidator."""
        vehicle_id = vehicle_info.get("id", "")
        make = vehicle_info.get("make", "")
        model = vehicle_info.get("model", "")
        engine_code = (
            vehicle_info.get("engine_code", "")
            if "engine_code" in vehicle_info
            else vehicle_info.get("engine", "")
        )
        powertrain = vehicle_info.get("powertrain_type", "gasoline")

        resolved_spec = SpecResolver.resolve_spec(
            vehicle_id=vehicle_id,
            make=make,
            model=model,
            engine_code=engine_code,
            powertrain_type=powertrain
        )

        raw_signals = stats.get("signals", {})
        coherent_signals = PhysicalCoherenceValidator.filter_coherent_signals(raw_signals, powertrain)

        payload = {
            "vehicle": {
                "display_name": vehicle_info.get("display_name", "Vehículo no especificado"),
                "make": make,
                "model": model,
                "engine": vehicle_info.get("engine", ""),
                "engine_code": engine_code,
                "fuel_type": vehicle_info.get("fuel_type", "Desconocido"),
                "powertrain_type": powertrain,
                "specification_confidence_tier": resolved_spec["confidence_tier"],
                "resolved_specifications": resolved_spec
            },
            "symptom_user_note": symptom_note or "Sin nota de síntoma",
            "dtcs": dtcs,
            "deterministic_rule_findings": rule_findings,
            "event_markers_and_impacts": event_impacts or [],
            "telemetry_statistics_summary": coherent_signals
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)


    def query_interactive(self, user_question: str, vehicle_info: Dict[str, Any], dtcs: List[Dict[str, Any]],
                          stats: Dict[str, Any], rule_findings: List[Dict[str, Any]],
                          event_impacts: Optional[List[Dict[str, Any]]] = None,
                          symptom_note: Optional[str] = None,
                          session_context: Optional[Dict[str, Any]] = None,
                          mode: str = "simple",
                          conversation_history: Optional[List[Dict[str, str]]] = None,
                          engine: str = "local",
                          allow_remote: bool = False,
                          language: str = "es") -> Dict[str, Any]:
        """Responde con hechos, hipótesis y acciones sin convertir posibilidades en certezas."""
        local_result = self.query_diagnostic_chat(
            user_question=user_question,
            vehicle_info=vehicle_info,
            dtcs=dtcs,
            stats=stats,
            rule_findings=rule_findings,
            event_impacts=event_impacts,
            symptom_note=symptom_note,
            session_context=session_context,
            mode=mode,
            conversation_history=conversation_history,
            language=language,
        )
        local_result["engine"] = "local"
        local_result["generative_explanation"] = None
        if engine != "generative":
            return local_result
        if not allow_remote:
            local_result["generative_status"] = (
                "No se enviaron datos: falta la autorización explícita de esta consulta."
            )
            return local_result
        status = self.generative_status()
        if not status["available"]:
            local_result["generative_status"] = status["message"]
            return local_result
        explanation = self._openai_grounded_explanation(
            local_result,
            session_context=session_context or {},
            conversation_history=conversation_history or [],
            language=language,
        )
        if explanation:
            local_result["engine"] = "local_with_generative_explanation"
            local_result["generative_explanation"] = explanation
            local_result["generative_status"] = (
                "Explicación redactada por IA sobre el resultado local; hechos, "
                "evidencias, hipótesis y urgencia no han sido sustituidos."
            )
        else:
            local_result["generative_status"] = (
                "La explicación remota no respondió; se conserva íntegro el análisis local."
            )
        return local_result

    def _openai_grounded_explanation(
        self,
        local_result: Dict[str, Any],
        *,
        session_context: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        language: str = "es",
    ) -> Optional[str]:
        """Añade lenguaje natural sin permitir que el modelo cambie la evidencia."""
        try:
            import httpx

            payload_for_model = {
                "question": local_result.get("question"),
                "local_answer": local_result.get("answer"),
                "facts": local_result.get("facts", []),
                "hypotheses_unconfirmed": local_result.get("hypotheses", []),
                "evidence": local_result.get("evidence", []),
                "missing_data": local_result.get("missing_data", []),
                "urgency": local_result.get("urgency"),
                "session_scope": session_context,
                "recent_conversation": conversation_history[-12:],
            }
            language_names = {
                "es": "Spanish", "en": "English", "it": "Italian", "de": "German"
            }
            response = httpx.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.openai_model,
                    "instructions": (
                        f"Always answer in {language_names.get(language, 'Spanish')}. Explain clearly the "
                        "resultado diagnóstico proporcionado. No añadas valores, DTC, "
                        "piezas averiadas ni conclusiones que no estén en el JSON. "
                        "Distingue hechos de hipótesis y di expresamente qué falta para "
                        "confirmar. No cambies la urgencia. Devuelve solo la explicación."
                    ),
                    "input": json.dumps(payload_for_model, ensure_ascii=False),
                    "max_output_tokens": 500,
                    "store": False,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            body = response.json()
            if body.get("output_text"):
                return str(body["output_text"]).strip()
            for output in body.get("output", []):
                for content in output.get("content", []):
                    if content.get("type") in {"output_text", "text"} and content.get("text"):
                        return str(content["text"]).strip()
        except Exception:
            logger.exception("No se pudo obtener la explicación generativa acotada.")
        return None

    def query_diagnostic_chat(
        self,
        user_question: str,
        vehicle_info: Dict[str, Any],
        dtcs: List[Dict[str, Any]],
        stats: Dict[str, Any],
        rule_findings: List[Dict[str, Any]],
        event_impacts: Optional[List[Dict[str, Any]]] = None,
        symptom_note: Optional[str] = None,
        session_context: Optional[Dict[str, Any]] = None,
        mode: str = "simple",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        language: str = "es",
    ) -> Dict[str, Any]:
        question = (user_question or "").strip()
        previous_user_text = " ".join(
            str(item.get("content", ""))
            for item in (conversation_history or [])[-12:]
            if item.get("role") == "user"
        )
        normalized = f"{symptom_note or ''} {previous_user_text} {question}".lower()
        powertrain = vehicle_info.get("powertrain_type", "gasoline")
        signals = PhysicalCoherenceValidator.filter_coherent_signals(
            stats.get("signals", {}),
            powertrain,
        )
        valid_signals = {
            pid: signal for pid, signal in signals.items() if signal.get("has_data")
        }
        symptom = "general"
        symptom_rules = [
            ("cooling", ("temperatura", "calienta", "refrigerante", "termostato")),
            ("battery", ("batería", "bateria", "alternador", "arranque", "voltaje")),
            ("idle", ("ralentí", "ralenti", "vibra parado", "inestable")),
            ("intake", ("tirón", "tiron", "potencia", "turbo", "aceler", "silbido")),
            ("fuel", ("consumo", "mezcla", "gasolina", "combustible")),
            ("emissions", ("humo", "itv", "emisiones", "escape")),
        ]
        for candidate, words in symptom_rules:
            if any(word in normalized for word in words):
                symptom = candidate
                break
        relevant_findings = [
            finding
            for finding in rule_findings
            if symptom == "general" or self._finding_matches_symptom(finding, symptom)
        ]
        requested_pids = self._requested_pids(normalized)
        context_question = any(
            phrase in normalized
            for phrase in (
                "qué datos", "que datos", "qué contexto", "que contexto",
                "en qué te basas", "en que te basas", "datos usaste",
                "información usaste", "informacion usaste",
            )
        )

        profile_map = {
            "cooling": ("COOLING_SYSTEM", "Prueba de termostato y refrigeración"),
            "battery": ("BATTERY_CHARGING", "Prueba de batería y alternador"),
            "idle": ("IDLE_STABILITY", "Prueba de ralentí caliente"),
            "intake": ("INTAKE_TURBO", "Prueba de turbo y admisión"),
            "fuel": ("FUEL_MIXTURE", "Prueba de consumo y mezcla"),
            "emissions": ("EMISSIONS_ITV", "Prueba de emisiones / ITV"),
            "general": ("COMPLETE_DIAGNOSTIC", "Diagnóstico completo guiado"),
        }
        follow_ups = {
            "cooling": [
                "¿Ocurre en ciudad, carretera o en ambas?",
                "¿Se enciende el ventilador y baja después la temperatura?",
            ],
            "battery": [
                "¿El problema aparece al arrancar en frío o también en caliente?",
                "¿Se atenúan las luces o aparece el testigo de batería?",
            ],
            "idle": [
                "¿Sucede con el motor frío, caliente o siempre?",
                "¿Cambian las vibraciones al encender el aire acondicionado?",
            ],
            "intake": [
                "¿En qué marcha y rango de RPM notas el tirón?",
                "¿Aparece humo, silbido o testigo de avería al acelerar?",
            ],
            "fuel": [
                "¿El consumo aumentó de forma repentina o progresiva?",
                "¿Notas olor a combustible o dificultad para arrancar?",
            ],
            "emissions": [
                "¿De qué color es el humo y cuándo aparece?",
                "¿Hay algún testigo encendido en el cuadro?",
            ],
            "general": [
                "¿Cuándo empezó y en qué condiciones sucede?",
                "¿Aparece algún testigo, ruido, humo o vibración?",
            ],
        }[symptom]

        evidence = []
        symptom_preferred = {
            "cooling": ["COOLANT_TEMP", "INTAKE_TEMP", "RPM", "SPEED"],
            "battery": ["CONTROL_MODULE_VOLTAGE", "RPM", "ENGINE_LOAD"],
            "idle": ["RPM", "ENGINE_LOAD", "MAF", "INTAKE_PRESSURE"],
            "intake": ["RPM", "THROTTLE_POS", "ENGINE_LOAD", "MAF", "INTAKE_PRESSURE"],
            "fuel": ["SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "MAF", "FUEL_PRESSURE"],
            "emissions": ["COOLANT_TEMP", "LONG_FUEL_TRIM_1", "RPM"],
            "general": list(valid_signals.keys()),
        }[symptom]
        preferred = list(dict.fromkeys(requested_pids + symptom_preferred))
        for pid in preferred:
            signal = valid_signals.get(pid)
            if signal and len(evidence) < 6:
                evidence.append(
                    {
                        "id": f"EV-{len(evidence) + 1:03d}",
                        "pid": pid,
                        "min": signal.get("min"),
                        "max": signal.get("max"),
                        "mean": signal.get("mean"),
                        "std": signal.get("std"),
                        "unit": signal.get("unit", ""),
                        "summary": f"{pid}: media {signal.get('mean')}, rango {signal.get('min')}–{signal.get('max')}.",
                    }
                )
        requested_evidence = [
            item for item in evidence if item["pid"] in requested_pids
        ]

        facts = []
        for dtc in dtcs[:4]:
            facts.append(f"DTC {dtc.get('code')}: {dtc.get('description') or 'sin descripción'}")
        for finding in relevant_findings[:4]:
            facts.append(str(finding.get("message", "Hallazgo determinista")))
        significant_event_count = 0
        for impact in (event_impacts or [])[:3]:
            if not impact.get("found"):
                continue
            significant = [
                (pid, values)
                for pid, values in impact.get("signal_impacts", {}).items()
                if values.get("significant_change")
            ]
            if significant:
                significant_event_count += 1
                pid, values = max(significant, key=lambda item: item[1].get("z_score", 0))
                facts.append(
                    f"En el marcador «{impact.get('marker_note') or impact.get('event_type') or 'evento'}», "
                    f"{pid} cambió de {values.get('mean_before')} a {values.get('mean_after')} "
                    f"en la ventana medida."
                )
        historical_baseline = dict(
            (session_context or {}).get("historical_baseline") or {}
        )
        baseline_deviations = historical_baseline.get("deviations", [])
        for deviation in baseline_deviations[:3]:
            direction = (
                "por debajo"
                if deviation.get("status") == "BELOW_BASELINE"
                else "por encima"
            )
            facts.append(
                f"{deviation.get('pid')}: mediana {deviation.get('current_p50')} "
                f"{deviation.get('unit', '')}, {direction} de la referencia histórica "
                f"del propio vehículo ({deviation.get('baseline_p10')}–"
                f"{deviation.get('baseline_p90')} {deviation.get('unit', '')})."
            )
        if not facts and valid_signals:
            facts.append(f"La sesión contiene {len(valid_signals)} señales OBD con datos válidos.")
        if not valid_signals:
            facts.append("No hay telemetría OBD válida suficiente para comprobar el síntoma.")

        hypotheses = []
        for finding in relevant_findings[:3]:
            hypotheses.append(
                {
                    "title": self._hypothesis_from_finding(finding),
                    "confidence": round(float(finding.get("confidence", 0.65)), 2),
                    "basis": str(finding.get("message", "Hallazgo del motor de reglas")),
                    "confirmed": False,
                }
            )
        if not hypotheses:
            generic = {
                "cooling": ("Termostato, ventilación o sensor ECT", "Se necesita observar la curva térmica para distinguirlos."),
                "battery": ("Batería, conexiones o sistema de carga", "La tensión bajo distintas cargas permite separarlos."),
                "idle": ("Admisión, EGR, encendido o inyección", "Son posibilidades habituales; aún no hay evidencia suficiente para elegir una."),
                "intake": ("Fuga de admisión, control de turbo o medición MAF/MAP", "El síntoma descrito puede proceder de varios elementos del circuito de aire."),
                "fuel": ("Medición de aire, presión o corrección de combustible", "Hace falta comparar mezcla en ralentí y carga parcial."),
                "emissions": ("Combustión, EGR o postratamiento", "El color del humo, DTC y monitores I/M son necesarios para concretar."),
                "general": ("Causa todavía no determinada", "La descripción inicial no permite aislar un sistema."),
            }[symptom]
            hypotheses.append(
                {
                    "title": generic[0],
                    "confidence": 0.35 if valid_signals else 0.15,
                    "basis": generic[1],
                    "confirmed": False,
                }
            )

        severity_values = [str(finding.get("severity", "warning")).lower() for finding in rule_findings]
        if "critical" in severity_values:
            urgency = {
                "level": "stop",
                "label": "Detener y revisar",
                "can_drive": False,
                "message": "Existe una condición crítica registrada. Detén el vehículo con seguridad y solicita revisión.",
            }
        elif dtcs or relevant_findings:
            urgency = {
                "level": "soon",
                "label": "Revisar pronto",
                "can_drive": None,
                "message": "Hay evidencias que justifican una comprobación dirigida antes de seguir usando el coche con normalidad.",
            }
        elif not valid_signals:
            urgency = {
                "level": "unknown",
                "label": "No evaluable",
                "can_drive": None,
                "message": "Sin datos válidos no puedo valorar con seguridad si conviene seguir circulando.",
            }
        else:
            urgency = {
                "level": "monitor",
                "label": "Sin urgencia demostrada",
                "can_drive": True,
                "message": "La sesión no muestra una condición crítica, pero esto no descarta fallos fuera de los sensores medidos.",
            }

        profile_id, profile_name = profile_map[symptom]
        solutions = [
            {
                "level": "safe",
                "title": "Comprobaciones sencillas y seguras",
                "steps": self._safe_checks(symptom),
                "warning": "Realízalas con el vehículo inmovilizado y siguiendo el manual del fabricante.",
            },
            {
                "level": "test",
                "title": "Prueba para confirmar",
                "steps": [f"Ejecuta «{profile_name}» y marca el instante exacto en que aparece el síntoma."],
                "warning": "El conductor no debe manipular la aplicación durante la marcha.",
            },
            {
                "level": "repair",
                "title": "Posible reparación, solo tras confirmar",
                "steps": ["No sustituyas piezas por esta hipótesis. Confirma primero con la prueba y una inspección física."],
                "warning": "No borres DTC antes de guardar su estado y freeze frame.",
            },
        ]

        tone_prefix = {
            "simple": "En palabras sencillas",
            "technical": "Lectura técnica",
            "workshop": "Orden de trabajo de taller",
        }.get(mode, "En palabras sencillas")
        if not valid_signals:
            answer = f"{tone_prefix}: entiendo el problema que describes, pero esta sesión no contiene datos válidos para confirmar una causa."
        elif context_question:
            answer = (
                f"{tone_prefix}: esta respuesta se basa en {stats.get('total_samples', 0)} lecturas "
                f"de la sesión seleccionada, {len(valid_signals)} señales OBD aplicables, "
                f"{len(relevant_findings)} hallazgos relacionados, {len(dtcs)} DTC y "
                f"{len(event_impacts or [])} marcadores. El detalle exacto aparece debajo."
            )
        elif requested_evidence:
            values = "; ".join(
                f"{item['pid']}: media {item['mean']}, mínimo {item['min']} y máximo {item['max']} {item.get('unit', '')}".strip()
                for item in requested_evidence
            )
            answer = f"{tone_prefix}: en esta sesión OBD se registró {values}."
        elif requested_pids:
            answer = (
                f"{tone_prefix}: esta sesión no contiene una lectura válida de "
                f"{', '.join(requested_pids)}; no voy a estimar ni inventar ese valor."
            )
        elif relevant_findings:
            answer = f"{tone_prefix}: hay indicios medidos relacionados con tu consulta, pero todavía son hipótesis y deben confirmarse."
        elif significant_event_count:
            answer = (
                f"{tone_prefix}: hay cambios medidos alrededor de {significant_event_count} "
                "marcadores, aunque por sí solos no confirman una pieza averiada."
            )
        elif dtcs:
            answer = (
                f"{tone_prefix}: hay {len(dtcs)} DTC guardados para el vehículo, pero no aparece "
                "un hallazgo determinista relacionado en la telemetría de esta sesión."
            )
        else:
            answer = f"{tone_prefix}: no aparece una anomalía determinista clara en las señales disponibles. Conviene reproducir el síntoma con una prueba específica."

        missing_data = [
            pid for pid in preferred[:5] if pid not in valid_signals
        ]
        source_counts = dict((session_context or {}).get("data_sources") or {})
        sample_count = int((session_context or {}).get("sample_count") or stats.get("total_samples") or 0)
        history_turns = len(conversation_history or [])
        context_used = [
            f"Sesión OBD seleccionada: {(session_context or {}).get('title') or (session_context or {}).get('id') or 'sin título'}",
            f"{sample_count} lecturas registradas y {len(valid_signals)} señales físicamente aplicables",
            f"{len(relevant_findings)} hallazgos relacionados con la pregunta de {len(rule_findings)} hallazgos totales",
            f"{len(dtcs)} DTC del alcance indicado",
            f"{len(event_impacts or [])} marcadores de conducción analizados",
            f"{history_turns} mensajes recientes usados como contexto conversacional",
        ]
        if historical_baseline.get("available"):
            context_used.append(
                "Referencia histórica separada de "
                f"{historical_baseline.get('qualifying_session_count', 0)} "
                "sesiones anteriores válidas del mismo vehículo"
            )
        else:
            context_used.append(
                "Referencia histórica aún no disponible; no se usó para inferir valores"
            )
        if symptom_note:
            context_used.append("Síntoma guardado al iniciar la prueba")
        if source_counts.get("simulated", 0):
            facts.insert(0, "La sesión contiene datos simulados; no equivalen a mediciones de una ECU real.")
        disclaimer = (
            "Orientación diagnóstica basada en los datos disponibles; no sustituye una inspección mecánica "
            "ni confirma por sí sola una reparación."
        )
        if source_counts.get("simulated", 0):
            disclaimer = (
                "Respuesta de demostración basada en datos simulados. No debe utilizarse para decidir "
                "una reparación real."
            )
        return {
            "question": question,
            "answer": answer,
            "status": "success",
            "provider": "Motor diagnóstico local con evidencia",
            "mode": mode,
            "urgency": urgency,
            "facts": facts,
            "hypotheses": hypotheses,
            "solutions": solutions,
            "recommended_test": {
                "profile_id": profile_id,
                "name": profile_name,
                "reason": "Es la prueba que mejor separa las causas posibles con los PIDs disponibles.",
            },
            "follow_up_questions": follow_ups,
            "missing_data": missing_data,
            "evidence": evidence,
            "data_basis": {
                "session_id": (session_context or {}).get("id"),
                "vehicle_id": vehicle_info.get("id"),
                "sample_count": sample_count,
                "valid_signal_count": len(valid_signals),
                "rule_finding_count": len(rule_findings),
                "relevant_finding_count": len(relevant_findings),
                "dtc_count": len(dtcs),
                "event_marker_count": len(event_impacts or []),
                "conversation_turn_count": history_turns,
                "data_sources": source_counts,
                "dtc_scope": (session_context or {}).get("dtc_scope", "Último escaneo DTC guardado para el vehículo"),
                "specification_scope": (session_context or {}).get("specification_scope"),
                "historical_baseline_available": historical_baseline.get(
                    "available",
                    False,
                ),
                "historical_baseline_session_count": historical_baseline.get(
                    "qualifying_session_count",
                    0,
                ),
                "historical_deviation_count": len(baseline_deviations),
            },
            "context_used": context_used,
            "disclaimer": disclaimer,
        }

    @staticmethod
    def _hypothesis_from_finding(finding: Dict[str, Any]) -> str:
        finding_type = str(finding.get("finding_type", "")).upper()
        if "COOLING" in finding_type:
            return "Termostato abierto, sensor ECT o funcionamiento térmico anómalo"
        if "FUEL" in finding_type:
            return "Entrada de aire no medida, presión de combustible o sensor MAF"
        if "IDLE" in finding_type:
            return "Inestabilidad de admisión, EGR, encendido o inyección"
        return "Causa relacionada con el hallazgo determinista registrado"

    @staticmethod
    def _finding_matches_symptom(finding: Dict[str, Any], symptom: str) -> bool:
        text = " ".join(
            str(finding.get(key, ""))
            for key in ("finding_type", "rule_id", "message")
        ).lower()
        keywords = {
            "cooling": ("cool", "temper", "termost", "refriger"),
            "battery": ("batter", "volt", "charg", "altern"),
            "idle": ("idle", "ralent", "rpm", "stability"),
            "intake": ("intake", "turbo", "boost", "maf", "map", "admis", "potencia"),
            "fuel": ("fuel", "trim", "mezcla", "combust", "inye"),
            "emissions": ("emission", "egr", "dpf", "catal", "humo", "escape"),
        }.get(symptom, ())
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def _requested_pids(text: str) -> List[str]:
        aliases = {
            "RPM": ("rpm", "revoluciones"),
            "SPEED": ("velocidad", "km/h"),
            "ENGINE_LOAD": ("carga del motor", "carga motor"),
            "THROTTLE_POS": ("acelerador", "mariposa"),
            "COOLANT_TEMP": ("refrigerante", "temperatura del motor", "temperatura motor"),
            "INTAKE_TEMP": ("temperatura de admisión", "temperatura admision"),
            "CONTROL_MODULE_VOLTAGE": ("voltaje", "tensión", "tension", "batería", "bateria"),
            "MAF": ("maf", "caudalímetro", "caudalimetro", "caudal de aire"),
            "INTAKE_PRESSURE": ("map", "presión de admisión", "presion de admision", "turbo"),
            "SHORT_FUEL_TRIM_1": ("stft", "corrección a corto", "correccion a corto"),
            "LONG_FUEL_TRIM_1": ("ltft", "corrección a largo", "correccion a largo"),
            "FUEL_PRESSURE": ("presión de combustible", "presion de combustible"),
        }
        return [
            pid
            for pid, words in aliases.items()
            if any(word in text for word in words)
        ]

    @staticmethod
    def _safe_checks(symptom: str) -> List[str]:
        return {
            "cooling": ["Con el motor frío, comprueba visualmente nivel, fugas y estado exterior de manguitos."],
            "battery": ["Revisa que los bornes estén firmes, limpios y sin corrosión visible."],
            "idle": ["Inspecciona manguitos de admisión y conectores accesibles sin desmontar componentes."],
            "intake": ["Busca manguitos sueltos, rotos o con restos de aceite alrededor de uniones."],
            "fuel": ["Comprueba si hay olor o fugas visibles; si los hay, no arranques el vehículo."],
            "emissions": ["Anota color, duración y condiciones del humo sin acercarte al escape caliente."],
            "general": ["Revisa niveles y testigos con el vehículo estacionado y el motor frío."],
        }[symptom]

    def analyze_session(self, vehicle_info: Dict[str, Any], dtcs: List[Dict[str, Any]],
                        stats: Dict[str, Any], rule_findings: List[Dict[str, Any]],
                        symptom_note: Optional[str] = None,
                        allow_remote: bool = False) -> AiAnalysisResponse:
        """
        Ejecuta el análisis determinista local. La rama remota heredada solo se
        habilita mediante ``allow_remote=True``; configurar una clave por sí sola
        nunca debe transmitir telemetría.
        """
        context_json = self.build_context_prompt(vehicle_info, dtcs, stats, rule_findings, symptom_note)

        # Si se configura la clave de Anthropic en .env
        if allow_remote and self.api_key and self.api_key.startswith("sk-ant"):
            try:
                import httpx
                headers = {
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
                user_msg = f"{SYSTEM_PROMPT}\n\nAnaliza los siguientes datos del vehículo y responde en JSON estricto:\n{context_json}"
                payload = {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": user_msg}]
                }
                resp = httpx.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    res_data = resp.json()
                    text = res_data["content"][0]["text"]
                    clean_text = text.replace("```json", "").replace("```", "").strip()
                    parsed = json.loads(clean_text)
                    return AiAnalysisResponse(**parsed)
            except Exception as e:
                logger.error(f"Error invocando la API de Anthropic Claude: {e}")

        # Si se dispusiera de cliente OpenAI / Anthropic remoto, se invocaría aquí.
        # Fallback local totalmente determinista y conforme al esquema:
        observed = []
        if dtcs:
            for d in dtcs:
                observed.append(f"Código DTC detectado: {d.get('code')} - {d.get('description')}")
        else:
            observed.append("No se registran códigos de avería genéricos (DTC) activos.")

        signals = stats.get("signals", {})
        for pid, s in signals.items():
            if s.get("has_data"):
                observed.append(f"Señal {pid}: rango [{s.get('min')} a {s.get('max')}] {s.get('unit', '')}, media {s.get('mean')}")

        math_anomalies = []
        hypotheses = []
        checks = []
        warnings = [
            "Realizar las comprobaciones mecánicas únicamente con el vehículo estacionado y el motor apagado a menos que la prueba requiera explícitamente motor en marcha.",
            "No manipular componentes del sistema de escape o refrigeración cuando el motor esté a temperatura de servicio."
        ]

        from analysis.evidence_catalog import EvidenceCatalog
        catalog = EvidenceCatalog(session_id="local_session")
        ev_ids = []

        if rule_findings:
            for idx, f in enumerate(rule_findings):
                math_anomalies.append(f.get("message", ""))
                ev_id = catalog.add_evidence(
                    start_monotonic=0.0,
                    end_monotonic=10.0,
                    signals=["COOLANT_TEMP", "LONG_FUEL_TRIM_1", "RPM"],
                    summary=f.get("message", "Anomalía determinista"),
                    details=f.get("evidence", {})
                )
                ev_ids.append(ev_id)
                if f.get("finding_type") == "COOLING_SYSTEM_ANOMALY":
                    hypotheses.append(f"[{ev_id}] Termostato atascado en posición abierta o sensor de temperatura descalibrado.")
                    checks.append("Comprobar la temperatura del manguito superior del radiador manualmente mediante infrarrojos o termómetro.")
                    checks.append("Verificar la resistencia eléctrica del sensor ECT a 20°C y a 90°C.")
                elif f.get("finding_type") == "FUEL_TRIM_ANOMALY":
                    hypotheses.append(f"[{ev_id}] Entrada de aire no medida en el colector de admisión o sensor MAF sucio.")
                    checks.append("Inspeccionar tubos de vacío y manguitos de admisión mediante máquina de humo.")
                    checks.append("Limpiar el filamento del sensor MAF con un limpiador dieléctrico específico.")
        else:
            hypotheses.append("No se detectan patrones anómalos evidentes en la muestra recopilada.")
            checks.append("Realizar una prueba de conducción prolongada bajo diferentes condiciones de carga de motor.")

        missing = []
        if "COOLANT_TEMP" not in signals:
            missing.append("Temperatura de refrigerante (COOLANT_TEMP)")
        if "LONG_FUEL_TRIM_1" not in signals:
            missing.append("Ajuste de combustible a largo plazo (LONG_FUEL_TRIM_1)")

        confidence = 0.85 if rule_findings else 0.70

        return AiAnalysisResponse(
            observed_facts=observed,
            evidence_ids=ev_ids,
            mathematical_anomalies=math_anomalies,
            hypotheses=hypotheses,
            recommended_checks=checks,
            missing_data=missing,
            confidence_level=confidence,
            warnings=warnings
        )
