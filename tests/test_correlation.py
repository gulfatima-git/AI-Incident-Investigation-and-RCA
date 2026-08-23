from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from src.correlation.incident_builder import build_incidents


def test_incident_grouping_logic() -> None:
    base = datetime(2024, 1, 1, 12, 0, 0)
    df = pd.DataFrame(
        [
            {"is_flagged": True, "protocol_type": "tcp", "service": "http", "flag": "SF", "predicted_attack_category": "Probe", "event_time": base},
            {"is_flagged": True, "protocol_type": "tcp", "service": "http", "flag": "SF", "predicted_attack_category": "Probe", "event_time": base + timedelta(minutes=1)},
            {"is_flagged": True, "protocol_type": "tcp", "service": "http", "flag": "SF", "predicted_attack_category": "DoS", "event_time": base + timedelta(minutes=10)},
        ]
    )
    incidents = build_incidents(df)
    assert len(incidents) >= 1
