"""Streamlit dashboard entrypoint."""

from __future__ import annotations

import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


st.set_page_config(page_title="AI Incident RCA Platform", layout="wide")
st.title("AI Incident Investigation & Root-Cause Analysis Platform")
st.write("Upload intrusion data, detect malicious activity, correlate incidents, and generate grounded RCA reports.")
st.sidebar.title("Navigation")
st.sidebar.write("Use the pages in the dashboard/ pages folder.")
