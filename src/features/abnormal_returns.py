"""Abnormal returns berekenen rond elke post.

Voor elk post `p` op tijdstip `t`, en voor elk asset, bereken:
    AR(t, Δ) = r_actual(t, t+Δ) - r_expected(t, t+Δ)

Met `r_expected` ofwel:
- *simple*: rolling mean over [t-30d, t-1d]
- *market_model*: OLS regressie op marktindex (factor model)

Eerste implementatie = simple. Market model is bonus voor week 5 robustness.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def align_post_to_market(
    posts: pd.DataFrame,
    market: pd.DataFrame,
    window: str = "1d",
) -> pd.DataFrame:
    """Align elke post met de eerstvolgende marktbeweging.

    Voor daily windows: post op zaterdag → maandag close return.
    Voor intraday: post om 03:00 UTC → open + window.

    Parameters
    ----------
    posts : DataFrame met `timestamp_utc`.
    market : DataFrame met `date`, `ticker`, `close`, `log_return` (uit collect_market).
    window : "1h" | "1d" | "3d"

    Returns
    -------
    DataFrame
        posts uitgebreid met `aligned_market_date` en `aligned_close`.
    """
    market = market.sort_values(["ticker", "date"])
    posts = posts.sort_values("timestamp_utc").copy()

    # TODO: voor intraday windows, interpolate op minute-level. Nu: daily-alignment.
    if window not in {"1h", "1d", "3d"}:
        raise ValueError(f"Onbekend window: {window}")

    # merge_asof: voor elke post, vind volgende marktdate >= post date
    posts["post_date"] = posts["timestamp_utc"].dt.normalize()
    aligned = pd.merge_asof(
        posts,
        market.rename(columns={"date": "aligned_market_date"}),
        left_on="post_date",
        right_on="aligned_market_date",
        direction="forward",
        by=None,
        tolerance=pd.Timedelta(days=5),
    )
    return aligned


def compute_abnormal_returns(
    market: pd.DataFrame,
    estimation_window: int = 30,
    method: str = "simple",
) -> pd.DataFrame:
    """Bereken abnormal return per ticker per dag.

    Parameters
    ----------
    market : DataFrame met `date`, `ticker`, `log_return`.
    estimation_window : int
        Aantal handelsdagen voor expected-return baseline.
    method : "simple" | "market_model"

    Returns
    -------
    DataFrame
        market + extra kolom `abnormal_return`.
    """
    if method != "simple":
        raise NotImplementedError("Market model: implementeer in week 5 robustness phase.")

    market = market.sort_values(["ticker", "date"]).copy()
    expected = (
        market.groupby("ticker")["log_return"]
        .transform(lambda s: s.rolling(estimation_window, min_periods=10).mean().shift(1))
    )
    market["expected_return"] = expected
    market["abnormal_return"] = market["log_return"] - market["expected_return"]
    logger.info("Computed abnormal returns (method=%s, window=%d)", method, estimation_window)
    return market


def aggregate_to_post_level(
    posts_with_market: pd.DataFrame,
    abnormal: pd.DataFrame,
    windows: list[str],
) -> pd.DataFrame:
    """Voeg AR over verschillende windows toe als targets per post.

    TODO: implementeer voor 1u/1d/3d. Initial focus = 1d voor MVP.
    """
    raise NotImplementedError("Implementeer in notebook 03_alignment_returns.")
