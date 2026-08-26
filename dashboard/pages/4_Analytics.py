"""Analytics dashboard page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


st.header("Analytics")
incidents = st.session_state.get("incidents", [])
if not incidents:
    st.info("Run the pipeline first.")
else:
    df = pd.DataFrame(
        [
            {
                "incident_id": item.incident_id,
                "source": item.source_ip,
                "severity": item.severity,
                "attack_categories": ", ".join(item.attack_categories),
                "start_time": item.start_time,
            }
            for item in incidents
        ]
    )
    attack_counts = df.assign(attack_category=df["attack_categories"].str.split(", ")).explode("attack_category")["attack_category"].value_counts().reset_index()
    attack_counts.columns = ["attack_category", "count"]
    st.plotly_chart(px.bar(attack_counts, x="attack_category", y="count", title="Attack Category Distribution"))

    incident_over_time = df.sort_values("start_time").assign(count=1)
    st.plotly_chart(px.line(incident_over_time, x="start_time", y="count", title="Incidents Over Time"))

    source_counts = df["source"].value_counts().reset_index()
    source_counts.columns = ["source", "count"]
    st.plotly_chart(px.bar(source_counts.head(10), x="source", y="count", title="Top 10 Source IDs by Incident Count"))
    st.plotly_chart(px.pie(df, names="severity", title="Severity Distribution"))
