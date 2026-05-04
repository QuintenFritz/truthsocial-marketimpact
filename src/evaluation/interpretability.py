"""SHAP + permutation importance voor RF modellen.

Belangrijke design choice: GEEN sklearn Gini-based feature importance gebruiken
voor word features — Gini is biased richting hoog-cardinaliteit features wat
in TF-IDF context misleidend is. Permutation importance op held-out set is
de juiste maat.
"""

from __future__ import annotations

import logging
from typing import Sequence

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

logger = logging.getLogger(__name__)


def compute_permutation_importance(
    model,
    X_test,
    y_test,
    feature_names: Sequence[str],
    n_repeats: int = 10,
    random_state: int = 42,
) -> pd.DataFrame:
    """Permutation importance op held-out set.

    Returns
    -------
    DataFrame
        Sorted by importance descending. Kolommen: feature, importance_mean, importance_std.
    """
    result = permutation_importance(
        model, X_test, y_test, n_repeats=n_repeats,
        random_state=random_state, n_jobs=-1,
    )
    df = pd.DataFrame({
        "feature": feature_names,
        "importance_mean": result.importances_mean,
        "importance_std": result.importances_std,
    })
    return df.sort_values("importance_mean", ascending=False).reset_index(drop=True)


def compute_shap_values(model, X_sample, feature_names: Sequence[str]) -> "shap.Explanation":
    """SHAP TreeExplainer voor RF.

    Parameters
    ----------
    X_sample : sparse or dense matrix
        Subsample voor explainability — full set is te traag.

    Returns
    -------
    shap.Explanation object — gebruik .values, .base_values, .data.
    """
    import shap
    explainer = shap.TreeExplainer(model)
    # SHAP works beter met dense — convert if sparse
    if hasattr(X_sample, "toarray"):
        X_dense = X_sample.toarray()
    else:
        X_dense = np.asarray(X_sample)
    shap_values = explainer(X_dense)
    shap_values.feature_names = list(feature_names)
    return shap_values


def top_features_from_shap(shap_values, top_n: int = 30) -> pd.DataFrame:
    """Aggregate mean |SHAP| per feature voor global importance ranking."""
    abs_mean = np.abs(shap_values.values).mean(axis=0)
    if abs_mean.ndim > 1:  # multi-class case
        abs_mean = abs_mean.mean(axis=-1)
    df = pd.DataFrame({
        "feature": shap_values.feature_names,
        "mean_abs_shap": abs_mean,
    }).sort_values("mean_abs_shap", ascending=False).head(top_n).reset_index(drop=True)
    return df
