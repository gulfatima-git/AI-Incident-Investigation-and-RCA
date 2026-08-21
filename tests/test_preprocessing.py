from __future__ import annotations

import pandas as pd

from config import NSL_KDD_COLUMNS
from src.preprocessing.cleaner import add_targets, fit_preprocessor, map_attack_category


def test_attack_category_mapping() -> None:
    assert map_attack_category("neptune") == "DoS"
    assert map_attack_category("normal") == "normal"


def test_cleaning_produces_targets_and_no_nans() -> None:
    df = pd.DataFrame(
        [[0, "tcp", "http", "SF", 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 2, 2, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, "normal", 0],
         [0, "tcp", "ftp", "S0", 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2, 2, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, "neptune", 0]],
        columns=NSL_KDD_COLUMNS,
    )
    cleaned, artifacts = fit_preprocessor(df)
    assert "binary_label" in cleaned.columns
    assert "attack_category" in cleaned.columns
    assert not cleaned.isna().any().any()
