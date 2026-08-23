"""Incident grouping and correlation logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd

from config import CORRELATION_WINDOW_MINUTES, HAS_REAL_TIMESTAMPS
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Incident:
    """Correlated incident structure."""

    incident_id: str
    source_ip: str
    start_time: datetime
    end_time: datetime
    event_count: int
    attack_categories: list[str]
    severity: str
    events: list[dict[str, Any]]


def _synthetic_timestamp(index: int) -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=index * 30)


def _incident_severity(categories: list[str], event_count: int) -> str:
    cats = {cat.lower() for cat in categories}
    if "u2r" in cats or "r2l" in cats:
        return "Critical"
    if "dos" in cats and event_count > 10:
        return "High"
    if cats - {"normal"}:
        return "Medium"
    return "Low"


def _prepare_event_frame(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    if HAS_REAL_TIMESTAMPS and "timestamp" in frame.columns:
        frame["event_time"] = pd.to_datetime(frame["timestamp"])
    else:
        frame["event_time"] = [_synthetic_timestamp(i) for i in range(len(frame))]
    if "source_id" not in frame.columns:
        required = ["protocol_type", "service", "flag"]
        available = [col for col in required if col in frame.columns]
        frame["source_id"] = frame[available].astype(str).agg("|".join, axis=1) if available else "synthetic"
    return frame


def build_incidents(df: pd.DataFrame) -> list[Incident]:
    """Group flagged rows into incidents by synthetic or real source identifiers."""
    if "is_flagged" not in df.columns:
        raise ValueError("Expected is_flagged column before correlation.")

    flagged = _prepare_event_frame(df[df["is_flagged"]].copy())
    if flagged.empty:
        return []

    incidents: list[Incident] = []
    window = timedelta(minutes=CORRELATION_WINDOW_MINUTES)
    grouped = flagged.sort_values(["source_id", "event_time"]).groupby("source_id", sort=False)

    for source_id, group in grouped:
        chunk: list[pd.Series] = []
        previous_time: datetime | None = None
        incident_index = 1
        for _, row in group.iterrows():
            current_time = row["event_time"].to_pydatetime() if hasattr(row["event_time"], "to_pydatetime") else row["event_time"]
            if previous_time is not None and current_time - previous_time > window and chunk:
                incidents.append(_build_incident(source_id, incident_index, chunk))
                incident_index += 1
                chunk = []
            chunk.append(row)
            previous_time = current_time
        if chunk:
            incidents.append(_build_incident(source_id, incident_index, chunk))
    return incidents


def _build_incident(source_id: str, index: int, rows: list[pd.Series]) -> Incident:
    events = [row.to_dict() for row in rows]
    times = [event["event_time"] for event in events]
    start_time = min(pd.to_datetime(times)).to_pydatetime()
    end_time = max(pd.to_datetime(times)).to_pydatetime()
    categories = sorted({str(event.get("predicted_attack_category", "normal")) for event in events})
    return Incident(
        incident_id=f"{source_id}-{index}",
        source_ip=source_id,
        start_time=start_time,
        end_time=end_time,
        event_count=len(events),
        attack_categories=categories,
        severity=_incident_severity(categories, len(events)),
        events=events,
    )
