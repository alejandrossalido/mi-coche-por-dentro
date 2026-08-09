"""Línea base histórica verificable del propio vehículo."""
from __future__ import annotations

from statistics import median
from typing import Any, Callable, Dict, List, Optional

import polars as pl


class HistoricalBaselineService:
    """Construye referencias solo con sesiones OBD medidas y sin alertas."""

    def __init__(
        self,
        db_manager: Any,
        telemetry_store: Any,
        findings_evaluator: Callable[[pl.DataFrame, str], List[Dict[str, Any]]],
        minimum_sessions: int = 3,
    ):
        self.db = db_manager
        self.telemetry_store = telemetry_store
        self.findings_evaluator = findings_evaluator
        self.minimum_sessions = minimum_sessions

    def build(
        self,
        vehicle_id: str,
        *,
        engine_condition: Optional[str] = None,
        exclude_session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        vehicle = self.db.get_vehicle(vehicle_id) or {}
        qualifying: List[Dict[str, Any]] = []
        rejected: Dict[str, int] = {
            "estado_o_calidad": 0,
            "sin_datos_medidos": 0,
            "con_alertas": 0,
        }

        for session in self.db.list_sessions(vehicle_id=vehicle_id):
            if session["id"] == exclude_session_id:
                continue
            if engine_condition and session.get("engine_condition") != engine_condition:
                continue
            if (
                session.get("status") != "completed"
                or float(session.get("capture_quality_score") or 0) < 75
            ):
                rejected["estado_o_calidad"] += 1
                continue
            try:
                frame = self.telemetry_store.load_session_dataframe(session["id"])
            except Exception:
                frame = None
            measured = self._measured_rows(frame)
            if measured is None or measured.is_empty():
                rejected["sin_datos_medidos"] += 1
                continue
            findings = self.findings_evaluator(
                measured,
                vehicle.get("powertrain_type", "gasoline"),
            )
            if any(
                str(item.get("severity", "")).lower() in {"warning", "critical"}
                for item in findings
            ):
                rejected["con_alertas"] += 1
                continue
            qualifying.append(
                {
                    "session": session,
                    "signals": self._session_signal_summary(measured),
                }
            )

        if len(qualifying) < self.minimum_sessions:
            return {
                "vehicle_id": vehicle_id,
                "available": False,
                "status": "LEARNING",
                "context": engine_condition or "cualquier condición",
                "qualifying_session_count": len(qualifying),
                "minimum_session_count": self.minimum_sessions,
                "remaining_session_count": self.minimum_sessions - len(qualifying),
                "source_session_ids": [
                    item["session"]["id"] for item in qualifying
                ],
                "signals": {},
                "rejected_sessions": rejected,
                "message": (
                    f"Faltan {self.minimum_sessions - len(qualifying)} sesiones "
                    "completas, medidas, de calidad suficiente y sin alertas para "
                    "crear una referencia fiable del propio coche."
                ),
            }

        signal_names = sorted(
            {
                name
                for item in qualifying
                for name in item["signals"].keys()
            }
        )
        signals: Dict[str, Any] = {}
        for name in signal_names:
            summaries = [
                item["signals"][name]
                for item in qualifying
                if name in item["signals"]
            ]
            if len(summaries) < self.minimum_sessions:
                continue
            unit = next(
                (summary["unit"] for summary in summaries if summary.get("unit")),
                "",
            )
            signals[name] = {
                "p10": round(median(summary["p10"] for summary in summaries), 3),
                "p50": round(median(summary["p50"] for summary in summaries), 3),
                "p90": round(median(summary["p90"] for summary in summaries), 3),
                "mean": round(median(summary["mean"] for summary in summaries), 3),
                "unit": unit,
                "session_count": len(summaries),
                "sample_count": sum(summary["sample_count"] for summary in summaries),
            }

        return {
            "vehicle_id": vehicle_id,
            "available": bool(signals),
            "status": "VALID" if signals else "INSUFFICIENT_SIGNAL_OVERLAP",
            "context": engine_condition or "cualquier condición",
            "qualifying_session_count": len(qualifying),
            "minimum_session_count": self.minimum_sessions,
            "remaining_session_count": 0,
            "source_session_ids": [
                item["session"]["id"] for item in qualifying
            ],
            "signals": signals,
            "rejected_sessions": rejected,
            "message": (
                "Referencia calculada con sesiones anteriores del mismo vehículo; "
                "no es una especificación oficial del fabricante."
            ),
        }

    def compare_session(
        self,
        session_id: str,
        baseline: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        session = self.db.get_session(session_id)
        if not session:
            return {"available": False, "status": "SESSION_NOT_FOUND", "deviations": []}
        reference = baseline or self.build(
            session["vehicle_id"],
            engine_condition=session.get("engine_condition"),
            exclude_session_id=session_id,
        )
        if not reference.get("available"):
            return {**reference, "deviations": []}
        current = self._session_signal_summary(
            self._measured_rows(
                self.telemetry_store.load_session_dataframe(session_id)
            )
        )
        deviations = []
        for pid, values in current.items():
            expected = reference["signals"].get(pid)
            if not expected:
                continue
            value = values["p50"]
            if value < expected["p10"] or value > expected["p90"]:
                center = expected["p50"]
                difference = (
                    round(((value - center) / abs(center)) * 100, 1)
                    if center
                    else None
                )
                deviations.append(
                    {
                        "pid": pid,
                        "status": (
                            "BELOW_BASELINE"
                            if value < expected["p10"]
                            else "ABOVE_BASELINE"
                        ),
                        "current_p50": value,
                        "baseline_p10": expected["p10"],
                        "baseline_p50": center,
                        "baseline_p90": expected["p90"],
                        "deviation_percent": difference,
                        "unit": expected.get("unit") or values.get("unit", ""),
                    }
                )
        return {
            **reference,
            "compared_session_id": session_id,
            "deviations": deviations,
        }

    @staticmethod
    def _measured_rows(frame: Optional[pl.DataFrame]) -> Optional[pl.DataFrame]:
        if frame is None or frame.is_empty():
            return frame
        result = frame.filter(pl.col("value").is_not_null())
        if "data_source" in result.columns:
            result = result.filter(pl.col("data_source") == "measured")
        return result

    @staticmethod
    def _session_signal_summary(frame: Optional[pl.DataFrame]) -> Dict[str, Any]:
        if frame is None or frame.is_empty():
            return {}
        summaries: Dict[str, Any] = {}
        for pid in frame["pid"].drop_nulls().unique().to_list():
            pid_frame = frame.filter(pl.col("pid") == pid)
            values = pid_frame["value"].drop_nulls()
            if len(values) < 5:
                continue
            unit = ""
            if "unit" in pid_frame.columns:
                units = pid_frame["unit"].drop_nulls().unique().to_list()
                unit = str(units[0]) if units else ""
            summaries[str(pid)] = {
                "p10": float(values.quantile(0.10)),
                "p50": float(values.median()),
                "p90": float(values.quantile(0.90)),
                "mean": float(values.mean()),
                "unit": unit,
                "sample_count": len(values),
            }
        return summaries
