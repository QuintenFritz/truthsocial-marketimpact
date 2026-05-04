"""FinBERT-gebaseerde sentiment scores. OPTIONEEL — alleen indien je voorloopt op planning.

Vereist: `pip install -e ".[nlp]"` (transformers + torch).

Modelkeuze: `ProsusAI/finbert` — getrained op financial PhraseBank.
Output per post: scores voor [positive, negative, neutral] + argmax label.
"""

from __future__ import annotations

import logging
from typing import Iterable

import pandas as pd

logger = logging.getLogger(__name__)


def load_finbert(model_name: str = "ProsusAI/finbert"):
    """Lazy import van transformers + torch."""
    try:
        import torch  # noqa: F401
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as e:
        raise ImportError(
            "FinBERT vereist optionele dependencies. Installeer met: pip install -e \".[nlp]\""
        ) from e

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()
    return tokenizer, model


def score_sentiment(texts: Iterable[str], batch_size: int = 32) -> pd.DataFrame:
    """Run FinBERT op een lijst teksten.

    Returns
    -------
    DataFrame
        Kolommen: positive, negative, neutral, label.
    """
    import torch
    tokenizer, model = load_finbert()

    rows = []
    texts = list(texts)
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        enc = tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            logits = model(**enc).logits
        probs = logits.softmax(dim=-1).cpu().numpy()
        for p in probs:
            rows.append({"positive": p[0], "negative": p[1], "neutral": p[2]})

    df = pd.DataFrame(rows)
    df["label"] = df[["positive", "negative", "neutral"]].idxmax(axis=1)
    return df
