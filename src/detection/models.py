"""Model wrapper abstractions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


class DetectionModel:
    """Uniform wrapper around sklearn-compatible estimators."""

    def __init__(self, estimator: Any, feature_columns: list[str] | None = None) -> None:
        self.estimator = estimator
        self.feature_columns = feature_columns or []

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "DetectionModel":
        self.estimator.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.estimator.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not hasattr(self.estimator, "predict_proba"):
            raise AttributeError("Underlying estimator does not implement predict_proba.")
        return self.estimator.predict_proba(X)

    def save(self, path: str | Path) -> None:
        joblib.dump({"estimator": self.estimator, "feature_columns": self.feature_columns}, Path(path))

    @classmethod
    def load(cls, path: str | Path) -> "DetectionModel":
        payload = joblib.load(Path(path))
        return cls(payload["estimator"], payload.get("feature_columns", []))
