"""Feature engineering for NSL-KDD data."""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import HIGH_RISK_SERVICES


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add lightweight derived features."""
    result = df.copy()
    dst_bytes = result["dst_bytes"].replace(0, np.nan)
    result["bytes_ratio"] = (result["src_bytes"] / dst_bytes).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    result["is_high_risk_service"] = result["service"].astype(str).str.lower().isin(HIGH_RISK_SERVICES).astype(int)
    return result
