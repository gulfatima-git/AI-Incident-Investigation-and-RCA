
"""End-to-end demo pipeline runner."""

from __future__ import annotations

import pandas as pd

from config import NSL_KDD_COLUMNS
from src.correlation.incident_builder import build_incidents
from src.detection.predict import run_detection
from src.detection.train import train_models
from src.reporting.report_generator import generate_report
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _demo_frame() -> pd.DataFrame:
    row = [0, "tcp", "http", "SF", 181, 5450, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 2, 2, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, "normal", 0]
    attack = [0, "tcp", "ftp", "S0", 123, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10, 10, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, "neptune", 0]
    return pd.DataFrame([row, attack] * 20, columns=NSL_KDD_COLUMNS)


def main() -> None:
    train_df = _demo_frame()
    test_df = _demo_frame()
    train_models(train_df, test_df)
    detected = run_detection(test_df)
    incidents = build_incidents(detected)
    for incident in incidents[:1]:
        generate_report(incident)
    logger.info("Pipeline completed with %s incidents.", len(incidents))


if __name__ == "__main__":
    main()
