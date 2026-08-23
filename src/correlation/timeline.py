"""Timeline formatting for incidents."""

from __future__ import annotations

from datetime import datetime

from src.correlation.incident_builder import Incident


def build_timeline(incident: Incident) -> list[dict[str, str]]:
    """Convert incident events into a chronological human-readable timeline."""
    timeline: list[dict[str, str]] = []
    for event in sorted(incident.events, key=lambda item: item.get("event_time")):
        timestamp = event.get("event_time")
        if isinstance(timestamp, datetime):
            formatted_time = timestamp.strftime("%H:%M:%S")
        else:
            formatted_time = str(timestamp)
        category = event.get("predicted_attack_category", "normal")
        if str(category).lower() == "normal":
            description = f"{formatted_time} — normal activity observed via service={event.get('service')}, flag={event.get('flag')}"
        else:
            description = f"{formatted_time} — {category} attack detected via service={event.get('service')}, flag={event.get('flag')}"
        timeline.append({"time": formatted_time, "description": description})
    return timeline
