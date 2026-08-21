from __future__ import annotations

import pandas as pd

from config import NSL_KDD_COLUMNS
from src.detection.models import DetectionModel
from src.detection.predict import run_detection
from src.preprocessing.cleaner import fit_preprocessor


def test_detection_model_wrapper_roundtrip(tmp_path) -> None:
    df = pd.DataFrame(
        [[0, "tcp", "http", "SF", 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 2, 2, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, "normal", 0],
         [0, "tcp", "ftp", "S0", 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2, 2, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, "neptune", 0]],
        columns=NSL_KDD_COLUMNS,
    )
    cleaned, artifacts = fit_preprocessor(df)
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from src.detection.models import DetectionModel
    from config import BINARY_MODEL_PATH, MULTICLASS_MODEL_PATH, ISOLATION_MODEL_PATH, PREPROCESSOR_ARTIFACT_PATH
    import joblib

    X = cleaned.drop(columns=["binary_label", "attack_category", "label"])
    y = cleaned["binary_label"]
    DetectionModel(RandomForestClassifier(n_estimators=10, random_state=42)).fit(X, y).save(BINARY_MODEL_PATH)
    DetectionModel(RandomForestClassifier(n_estimators=10, random_state=42)).fit(X, cleaned["attack_category"]).save(MULTICLASS_MODEL_PATH)
    DetectionModel(IsolationForest(random_state=42)).fit(X, None).save(ISOLATION_MODEL_PATH)
    artifacts.save(PREPROCESSOR_ARTIFACT_PATH)

    detected = run_detection(df)
    assert {"predicted_binary", "predicted_attack_category", "anomaly_score", "is_flagged"}.issubset(detected.columns)
