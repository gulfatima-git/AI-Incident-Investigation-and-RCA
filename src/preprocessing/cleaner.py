"""Cleaning, encoding, and scaling for intrusion data."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

from config import (
    ATTACK_CATEGORY_MAP,
    PROCESSED_DATA_DIR,
    SCALER_PATH,
    PREPROCESSOR_ARTIFACT_PATH,
)
from src.preprocessing.feature_engineering import add_features
from src.utils.logger import get_logger

logger = get_logger(__name__)

TARGET_COLUMNS = ["binary_label", "attack_category"]
CATEGORICAL_COLUMNS = ["protocol_type", "service", "flag"]


@dataclass
class PreprocessingArtifacts:
    """Artifacts required to transform raw NSL-KDD data consistently."""

    service_encoder: LabelEncoder = field(default_factory=LabelEncoder)
    protocol_categories: list[str] = field(default_factory=list)
    flag_categories: list[str] = field(default_factory=list)
    scaler: StandardScaler = field(default_factory=StandardScaler)
    numeric_columns: list[str] = field(default_factory=list)
    feature_columns: list[str] = field(default_factory=list)

    def save(self, path: str | Path = PREPROCESSOR_ARTIFACT_PATH) -> None:
        """Persist preprocessing artifacts to disk."""
        joblib.dump(self, Path(path))

    @classmethod
    def load(cls, path: str | Path = PREPROCESSOR_ARTIFACT_PATH) -> "PreprocessingArtifacts":
        """Load preprocessing artifacts from disk."""
        return joblib.load(Path(path))


def map_attack_category(label: str) -> str:
    """Map a raw NSL-KDD label to the standard attack category."""
    normalized = str(label).strip().lower()
    normalized = normalized.replace(".", "")
    normalized = normalized.replace("_", "_")
    if normalized in {"normal", "normal."}:
        return "normal"
    return ATTACK_CATEGORY_MAP.get(normalized, "normal")


def add_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Attach binary and attack-category targets."""
    result = df.copy()
    if "label" in result.columns:
        result["binary_label"] = np.where(result["label"].astype(str).str.lower().str.contains("normal"), "normal", "attack")
        result["attack_category"] = result["label"].map(map_attack_category)
    else:
        result["binary_label"] = pd.NA
        result["attack_category"] = pd.NA
    return result


def _one_hot_align(df: pd.DataFrame, column: str, categories: list[str]) -> pd.DataFrame:
    encoded = pd.get_dummies(df[column].astype(str), prefix=column)
    expected = [f"{column}_{category}" for category in categories]
    return encoded.reindex(columns=expected, fill_value=0)


def _prepare_features(df: pd.DataFrame, artifacts: PreprocessingArtifacts, fit: bool) -> pd.DataFrame:
    result = add_features(add_targets(df))

    if fit:
        artifacts.protocol_categories = sorted(result["protocol_type"].astype(str).unique().tolist())
        artifacts.flag_categories = sorted(result["flag"].astype(str).unique().tolist())
        service_values = sorted(result["service"].fillna("unknown").astype(str).unique().tolist())
        artifacts.service_encoder.fit(["unknown", *service_values])

    protocol_oh = _one_hot_align(result, "protocol_type", artifacts.protocol_categories)
    flag_oh = _one_hot_align(result, "flag", artifacts.flag_categories)
    service_values = result["service"].fillna("unknown").astype(str)
    service_values = service_values.where(service_values.isin(artifacts.service_encoder.classes_), "unknown")
    service_encoded = pd.Series(
        artifacts.service_encoder.transform(service_values),
        index=result.index,
        name="service_encoded",
    )

    numeric_columns = [
        col
        for col in result.columns
        if col not in {"label", "attack_category", "binary_label", "protocol_type", "service", "flag", "difficulty"}
        and pd.api.types.is_numeric_dtype(result[col])
    ]
    if fit:
        artifacts.numeric_columns = numeric_columns
        artifacts.scaler.fit(result[numeric_columns].fillna(0))

    scaled_numeric = pd.DataFrame(
        artifacts.scaler.transform(result[numeric_columns].fillna(0)),
        columns=numeric_columns,
        index=result.index,
    )
    model_df = pd.concat([scaled_numeric, service_encoded, protocol_oh, flag_oh], axis=1)
    if fit:
        artifacts.feature_columns = model_df.columns.tolist()
    model_df = model_df.reindex(columns=artifacts.feature_columns, fill_value=0)

    cleaned = pd.concat([result.drop(columns=numeric_columns, errors="ignore"), model_df], axis=1)
    cleaned = cleaned.drop(columns=[col for col in ["protocol_type", "service", "flag"] if col in cleaned.columns])
    cleaned = cleaned.drop(columns=["difficulty"], errors="ignore")
    return cleaned


def fit_preprocessor(train_df: pd.DataFrame) -> tuple[pd.DataFrame, PreprocessingArtifacts]:
    """Fit preprocessing artifacts and transform the training set."""
    artifacts = PreprocessingArtifacts()
    cleaned_train = _prepare_features(train_df.copy(), artifacts, fit=True)
    return cleaned_train, artifacts


def transform_with_artifacts(df: pd.DataFrame, artifacts: PreprocessingArtifacts) -> pd.DataFrame:
    """Transform a dataframe using fitted preprocessing artifacts."""
    raw_required = {"protocol_type", "service", "flag", "src_bytes", "dst_bytes"}
    if raw_required.issubset(df.columns):
        return _prepare_features(df.copy(), artifacts, fit=False)

    if set(artifacts.feature_columns).issubset(df.columns):
        result = df.copy()
        for column in artifacts.feature_columns:
            if column not in result.columns:
                result[column] = 0
        for column in ["binary_label", "attack_category"]:
            if column not in result.columns:
                result[column] = pd.NA
        metadata_columns = [column for column in ["label", "binary_label", "attack_category"] if column in result.columns]
        return result.reindex(columns=[*artifacts.feature_columns, *metadata_columns], fill_value=0)

    missing = ", ".join(sorted(raw_required.difference(df.columns)))
    raise ValueError(f"Input data is missing raw fields required for preprocessing: {missing}")


def save_processed_dataframe(df: pd.DataFrame, path: str | Path) -> Path:
    """Persist processed data as parquet if available, otherwise CSV."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(target, index=False)
        return target
    except Exception:
        csv_path = target.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        return csv_path


def process_and_save(train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, PreprocessingArtifacts]:
    """Fit preprocessing on train and persist train/test artifacts."""
    cleaned_train, artifacts = fit_preprocessor(train_df)
    cleaned_test = transform_with_artifacts(test_df, artifacts)
    save_processed_dataframe(cleaned_train, PROCESSED_DATA_DIR / "train.parquet")
    save_processed_dataframe(cleaned_test, PROCESSED_DATA_DIR / "test.parquet")
    artifacts.save(PREPROCESSOR_ARTIFACT_PATH)
    joblib.dump(artifacts.scaler, SCALER_PATH)
    return cleaned_train, cleaned_test, artifacts
