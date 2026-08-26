"""Reusable dashboard chart helpers."""

from __future__ import annotations

import plotly.express as px
import pandas as pd


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str):
    """Create a plotly bar chart."""
    return px.bar(df, x=x, y=y, title=title)
