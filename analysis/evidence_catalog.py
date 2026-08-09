"""
Catálogo cerrado de evidencias para análisis determinista e integración con la IA.
Genera identificadores de evidencia estrictos (EV-001, EV-002...) respaldados por datos observados.
"""
from typing import Dict, Any, List, Optional

class EvidenceObject:
    def __init__(self, ev_id: str, session_id: str, start_monotonic: float, end_monotonic: float,
                 signals: List[str], summary: str, details: Dict[str, Any]):
        self.ev_id = ev_id
        self.session_id = session_id
        self.start_monotonic = start_monotonic
        self.end_monotonic = end_monotonic
        self.signals = signals
        self.summary = summary
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.ev_id,
            "session_id": self.session_id,
            "start_monotonic": round(self.start_monotonic, 2),
            "end_monotonic": round(self.end_monotonic, 2),
            "signals": self.signals,
            "summary": self.summary,
            "details": self.details
        }

class EvidenceCatalog:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.evidences: List[EvidenceObject] = []
        self._counter = 1

    def add_evidence(self, start_monotonic: float, end_monotonic: float,
                     signals: List[str], summary: str, details: Dict[str, Any]) -> str:
        ev_id = f"EV-{self._counter:03d}"
        self._counter += 1
        obj = EvidenceObject(ev_id, self.session_id, start_monotonic, end_monotonic, signals, summary, details)
        self.evidences.append(obj)
        return ev_id

    def get_evidence(self, ev_id: str) -> Optional[Dict[str, Any]]:
        for ev in self.evidences:
            if ev.ev_id == ev_id:
                return ev.to_dict()
        return None

    def validate_citation(self, cited_ev_id: str) -> bool:
        """Verifica si un identificador citado existe en este catálogo cerrado."""
        return any(ev.ev_id == cited_ev_id for ev in self.evidences)

    def to_list(self) -> List[Dict[str, Any]]:
        return [ev.to_dict() for ev in self.evidences]
