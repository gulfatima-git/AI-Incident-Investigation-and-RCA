"""Upload data and run the full pipeline."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.correlation.incident_builder import build_incidents
from src.detection.predict import run_detection
from src.reporting.report_generator import generate_report

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


st.header("Upload Data")
uploaded = st.file_uploader("Upload NSL-KDD CSV/TXT or preprocessed CSV", type=["csv", "txt"])

if st.button("Run Detection Pipeline") and uploaded is not None:
    with st.spinner("Running pipeline..."):
        if uploaded.name.lower().endswith(".txt"):
            df = pd.read_csv(uploaded, header=None)
        else:
            df = pd.read_csv(uploaded)
            if df.shape[1] not in (43, 44):
                uploaded.seek(0)
                df = pd.read_csv(uploaded, header=None)
        if df.shape[1] == 43:
            from config import NSL_KDD_COLUMNS

            df.columns = NSL_KDD_COLUMNS
        detected = run_detection(df)
        incidents = build_incidents(detected)
        reports = {}
        for incident in incidents:
            try:
                reports[incident.incident_id] = generate_report(incident)
            except Exception as exc:
                st.error(f"Report generation failed for {incident.incident_id}: {exc}")
        st.session_state["detected_df"] = detected
        st.session_state["incidents"] = incidents
        st.session_state["reports"] = reports
        if incidents:
            st.session_state["selected_incident_id"] = incidents[0].incident_id
        st.success(f"Detected {len(incidents)} incidents.")
