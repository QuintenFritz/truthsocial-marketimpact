"""Project-specifieke metrics + statistical tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Fraction of predictions that match the sign of the actual return."""
    return float(((y_pred > 0) == (y_true > 0)).mean())


def mean_abnormal_return_test(
    abnormal_returns: np.ndarray, threshold: float = 0.0
) -> dict:
    """One-sample t-test: mean abnormal return ≠ threshold (default 0)."""
    t, p = stats.ttest_1samp(abnormal_returns, popmean=threshold)
    return {"mean": float(abnormal_returns.mean()), "t_stat": float(t), "p_value": float(p)}


def fdr_correction(p_values: pd.Series, alpha: float = 0.05) -> pd.Series:
    """Benjamini-Hochberg FDR correction. Returns boolean Series of significant tests."""
    from statsmodels.stats.multitest import multipletests
    rejected, _, _, _ = multipletests(p_values.values, alpha=alpha, method="fdr_bh")
    return pd.Series(rejected, index=p_values.index, name="significant_after_fdr")


def granger_causality(
    series1: pd.Series, series2: pd.Series, maxlag: int = 5
) -> dict:
    """Granger causality test — does series1 Granger-cause series2?

    Sanity check tegen reverse causality (markt → posts ipv andersom).
    """
    from statsmodels.tsa.stattools import grangercausalitytests
    df = pd.DataFrame({"y": series2, "x": series1}).dropna()
    result = grangercausalitytests(df, maxlag=maxlag, verbose=False)
    return {lag: r[0]["ssr_ftest"][1] for lag, r in result.items()}  # p-values per lag
