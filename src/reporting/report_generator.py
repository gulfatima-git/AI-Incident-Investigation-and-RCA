"""Incident RCA report generation."""

from __future__ import annotations

from pathlib import Path
import re

from config import REPORTS_DIR
from src.correlation.incident_builder import Incident
from src.reporting.llm_client import get_llm_client
from src.reporting.prompt_templates import build_rca_prompt


def generate_report(incident: Incident) -> str:
    """Generate and save a markdown RCA report for an incident."""
    prompt = build_rca_prompt(incident)
    client = get_llm_client()
    report = client.generate(prompt)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^A-Za-z0-9._-]+", "_", incident.incident_id)
    output_path = Path(REPORTS_DIR) / f"incident_{safe_id}.md"
    output_path.write_text(report, encoding="utf-8")
    return report
