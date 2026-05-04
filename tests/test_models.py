"""Smoke tests voor model module."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.models.random_forest import (chronological_split, evaluate_classifier,
                                      train_rf_classifier)


def test_chronological_split_preserves_order() -> None:
    df = pd.DataFrame({
        "timestamp_utc": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03",
                                          "2024-01-04", "2024-01-05"], utc=True),
        "x": [1, 2, 3, 4, 5],
    })
    train, test = chronological_split(df, test_size=0.4)
    assert len(train) == 3
    assert len(test) == 2
    assert train["x"].tolist() == [1, 2, 3]
    assert test["x"].tolist() == [4, 5]


def test_rf_classifier_trains() -> None:
    rng = np.random.default_rng(42)
    X = rng.normal(size=(200, 10))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    model = train_rf_classifier(X[:150], y[:150], n_estimators=20)
    metrics = evaluate_classifier(model, X[150:], y[150:])
    assert metrics["accuracy"] > 0.6
