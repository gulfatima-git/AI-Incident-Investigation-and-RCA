"""Train and persist detection models."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import IsolationForest, RandomForestClassifier

from config import (
    BINARY_MODEL_PATH,
    ISOLATION_MODEL_PATH,
    MULTICLASS_MODEL_PATH,
    RANDOM_SEED,
)
from src.detection.evaluate import evaluate_predictions
from src.detection.models import DetectionModel
from src.preprocessing.cleaner import fit_preprocessor, transform_with_artifacts
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _feature_target_split(df: pd.DataFrame, target: str) -> tuple[pd.DataFrame, pd.Series]:
    exclude = {"binary_label", "attack_category", "label"}
    X = df.drop(columns=[col for col in exclude if col in df.columns])
    y = df[target]
    return X, y


def train_models(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict[str, float]:
    """Fit all detection models and save them to disk."""
    cleaned_train, artifacts = fit_preprocessor(train_df)
    cleaned_test = transform_with_artifacts(test_df, artifacts)

    X_train_binary, y_train_binary = _feature_target_split(cleaned_train, "binary_label")
    X_test_binary, y_test_binary = _feature_target_split(cleaned_test, "binary_label")

    binary_model = DetectionModel(
        RandomForestClassifier(n_estimators=200, max_depth=None, random_state=RANDOM_SEED, class_weight="balanced")
    ).fit(X_train_binary, y_train_binary)
    binary_model.save(BINARY_MODEL_PATH)
    binary_predictions = binary_model.predict(X_test_binary)
    binary_metrics = evaluate_predictions(y_test_binary, binary_predictions, ["normal", "attack"], "Binary Confusion Matrix")

    X_train_multi, y_train_multi = _feature_target_split(cleaned_train, "attack_category")
    X_test_multi, y_test_multi = _feature_target_split(cleaned_test, "attack_category")

    smote = SMOTE(random_state=RANDOM_SEED, k_neighbors=1)
    X_resampled, y_resampled = smote.fit_resample(X_train_multi, y_train_multi)
    multiclass_model = DetectionModel(RandomForestClassifier(n_estimators=300, random_state=RANDOM_SEED)).fit(
        pd.DataFrame(X_resampled, columns=X_train_multi.columns),
        pd.Series(y_resampled),
    )
    multiclass_model.save(MULTICLASS_MODEL_PATH)
    multiclass_predictions = multiclass_model.predict(X_test_multi)
    multiclass_labels = sorted(set(map(str, y_test_multi.tolist())) | set(map(str, multiclass_predictions.tolist())))
    evaluate_predictions(y_test_multi, multiclass_predictions, multiclass_labels, "Multiclass Confusion Matrix")

    normal_rows = cleaned_train[cleaned_train["binary_label"] == "normal"]
    X_normal, _ = _feature_target_split(normal_rows, "binary_label")
    isolation_model = DetectionModel(IsolationForest(contamination=0.1, random_state=RANDOM_SEED)).fit(X_normal, None)
    isolation_model.save(ISOLATION_MODEL_PATH)

    artifacts.save()
    joblib.dump(artifacts.scaler, Path(ISOLATION_MODEL_PATH).with_name("scaler.joblib"))
    return {
        "binary_f1_weighted": float(binary_metrics["f1_weighted"]),
    }
