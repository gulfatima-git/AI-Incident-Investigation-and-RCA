"""Incident list page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

st.header("Detected Incidents")
incidents = st.session_state.get("incidents", [])
if not incidents:
    st.info("Run the pipeline first.")
else:
    rows = [
        {
            "incident_id": item.incident_id,
            "source": item.source_ip,
            "severity": item.severity,
            "attack_categories": ", ".join(item.attack_categories),
            "event_count": item.event_count,
            "start_time": item.start_time,
            "end_time": item.end_time,
        }
        for item in incidents
    ]
    df = pd.DataFrame(rows)
    def _severity_style(value: str) -> str:
        return {
            "Critical": "background-color: #ff4d4d; color: white;",
            "High": "background-color: #ff9933;",
            "Medium": "background-color: #ffd966;",
            "Low": "background-color: #b6d7a8;",
        }.get(value, "")

    st.dataframe(df.style.map(_severity_style, subset=["severity"]), use_container_width=True)
    selected = st.selectbox("Select incident", df["incident_id"].tolist())
    st.session_state["selected_incident_id"] = selected
