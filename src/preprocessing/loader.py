"""Dataset loading helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import NSL_KDD_COLUMNS
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_nsl_kdd(path: str | Path) -> pd.DataFrame:
    """Load an NSL-KDD TXT/CSV file and assign canonical column names."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(file_path, header=None)
    if df.shape[1] == len(NSL_KDD_COLUMNS):
        df.columns = NSL_KDD_COLUMNS
    elif list(df.columns) != NSL_KDD_COLUMNS:
        if df.shape[1] >= len(NSL_KDD_COLUMNS):
            df = df.iloc[:, : len(NSL_KDD_COLUMNS)]
            df.columns = NSL_KDD_COLUMNS
        else:
            raise ValueError("Input does not match expected NSL-KDD column count.")
    return df


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Load a raw dataset, auto-detecting headered CSVs."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    if file_path.suffix.lower() in {".txt", ".csv"}:
        try:
            return load_nsl_kdd(file_path)
        except Exception:
            logger.info("Falling back to headered CSV parsing for %s", file_path)
            return pd.read_csv(file_path)
    return pd.read_csv(file_path)
