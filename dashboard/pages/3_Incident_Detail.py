"""Incident detail page."""

from __future__ import annotations

import re

import streamlit as st

from src.correlation.timeline import build_timeline
from src.reporting.report_generator import generate_report

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

st.header("Incident Detail")
incident_id = st.session_state.get("selected_incident_id")
incidents = st.session_state.get("incidents", [])
incident = next((item for item in incidents if item.incident_id == incident_id), None)

if incident is None:
    st.info("Select an incident from the incidents page.")
else:
    st.subheader(incident.incident_id)
    st.write(f"Source: {incident.source_ip}")
    st.write(f"Severity: {incident.severity}")
    st.write(f"Window: {incident.start_time} - {incident.end_time}")
    st.dataframe(build_timeline(incident), use_container_width=True)
    if st.button("Regenerate Report"):
        st.session_state.setdefault("reports", {})
        st.session_state["reports"][incident.incident_id] = generate_report(incident)
    report_text = st.session_state.get("reports", {}).get(incident.incident_id, "_No report available._")
    st.markdown(report_text)
    safe_id = re.sub(r"[^A-Za-z0-9._-]+", "_", incident.incident_id)
    st.download_button("Download Report", data=report_text, file_name=f"incident_{safe_id}.md", mime="text/markdown")
