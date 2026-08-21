"""Prediction helpers for the incident platform."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    BINARY_MODEL_PATH,
    ISOLATION_MODEL_PATH,
    MULTICLASS_MODEL_PATH,
    PREPROCESSOR_ARTIFACT_PATH,
)
from src.detection.models import DetectionModel
from src.preprocessing.cleaner import PreprocessingArtifacts, transform_with_artifacts
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_detection(df: pd.DataFrame) -> pd.DataFrame:
    """Run binary, multiclass, and anomaly detection on a dataframe."""
    artifacts = PreprocessingArtifacts.load(PREPROCESSOR_ARTIFACT_PATH)
    processed = transform_with_artifacts(df, artifacts)

    binary_model = DetectionModel.load(BINARY_MODEL_PATH)
    multiclass_model = DetectionModel.load(MULTICLASS_MODEL_PATH)
    isolation_model = DetectionModel.load(ISOLATION_MODEL_PATH)

    exclude = {"binary_label", "attack_category", "label"}
    X = processed.drop(columns=[col for col in exclude if col in processed.columns])

    predicted_binary = binary_model.predict(X)
    predicted_attack_category = multiclass_model.predict(X)
    anomaly_raw = isolation_model.estimator.predict(X)
    anomaly_score = isolation_model.estimator.score_samples(X)

    result = df.copy()
    result["predicted_binary"] = predicted_binary
    result["predicted_attack_category"] = predicted_attack_category
    result["anomaly_score"] = anomaly_score
    result["is_anomaly"] = anomaly_raw == -1
    result["is_flagged"] = (result["predicted_binary"].astype(str) == "attack") | result["is_anomaly"]
    return result
