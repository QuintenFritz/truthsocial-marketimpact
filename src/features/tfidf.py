"""TF-IDF feature extractie."""

from __future__ import annotations

import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from src.config import CONFIG

logger = logging.getLogger(__name__)


def fit_tfidf(
    texts: pd.Series,
    *,
    max_features: int = 5000,
    ngram_range: tuple[int, int] = (1, 2),
    min_df: int = 5,
    max_df: float = 0.9,
) -> tuple[TfidfVectorizer, "scipy.sparse.csr_matrix"]:
    """Fit TF-IDF op trainingstexts.

    Returns
    -------
    (vectorizer, X)
    """
    vec = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
        sublinear_tf=True,
    )
    X = vec.fit_transform(texts)
    logger.info("TF-IDF: %d features, %d samples", X.shape[1], X.shape[0])
    return vec, X


def transform_tfidf(vec: TfidfVectorizer, texts: pd.Series):
    """Transform nieuwe teksten met een gefitte vectorizer."""
    return vec.transform(texts)


def save_vectorizer(vec: TfidfVectorizer, path: Path | str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vec, path)


def load_vectorizer(path: Path | str) -> TfidfVectorizer:
    return joblib.load(path)
