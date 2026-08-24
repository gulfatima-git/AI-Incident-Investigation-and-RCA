"""Prompt construction for incident RCA reports."""

from __future__ import annotations

from src.correlation.incident_builder import Incident
from src.correlation.timeline import build_timeline


def build_rca_prompt(incident: Incident) -> str:
    """Create a grounded prompt with structured incident data."""
    timeline = build_timeline(incident)
    formatted_timeline = "\n".join(f"- {event['description']}" for event in timeline)
    return f"""System: You are a cybersecurity incident analyst. Given structured intrusion detection
data, write a clear, factual root-cause analysis report. Do not invent facts not present
in the data. Use the following structure:
1. Incident Summary (1-2 sentences)
2. Timeline of Events
3. Likely Attack Methodology
4. Affected Systems/Services
5. Severity Justification
6. Recommended Remediation Steps

User: Here is the incident data:
- Incident ID: {incident.incident_id}
- Source: {incident.source_ip}
- Duration: {incident.start_time} to {incident.end_time}
- Event count: {incident.event_count}
- Attack categories observed: {incident.attack_categories}
- Severity: {incident.severity}
- Timeline: {formatted_timeline}

Write the RCA report now."""
