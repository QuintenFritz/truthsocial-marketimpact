"""Tekst preprocessing voor Truth Social posts.

Pipeline:
1. Lowercase
2. URL/mention strippen
3. Tokenization
4. Stopword removal
5. Lemmatization (optioneel — kost tijd, vaak weinig extra waarde voor TF-IDF)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import click
import pandas as pd

from src.config import CONFIG, resolve_path

logger = logging.getLogger(__name__)

URL_RE = re.compile(r"https?://\S+|www\.\S+")
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str, *, lowercase: bool = True, strip_urls: bool = True,
               strip_mentions: bool = True, keep_hashtag_word: bool = True) -> str:
    """Clean a single post.

    Notes
    -----
    Hashtags worden default behouden (alleen `#` symbol weggehaald) — ze dragen
    semantische betekenis (`#MAGA`, `#Tariffs`).
    """
    if not isinstance(text, str):
        return ""
    if lowercase:
        text = text.lower()
    if strip_urls:
        text = URL_RE.sub(" ", text)
    if strip_mentions:
        text = MENTION_RE.sub(" ", text)
    if keep_hashtag_word:
        text = HASHTAG_RE.sub(r"\1", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def preprocess_posts(posts: pd.DataFrame, min_length: int = 10) -> pd.DataFrame:
    """Apply cleaning + filter te-korte posts.

    Parameters
    ----------
    posts : DataFrame met kolom `text` en `timestamp_utc`.
    min_length : int
        Minimum aantal tokens; kortere posts worden gedropt.
    """
    cfg = CONFIG["preprocessing"]
    posts = posts.copy()
    posts["text_clean"] = posts["text"].apply(
        lambda t: clean_text(
            t,
            lowercase=cfg["lowercase"],
            strip_urls=cfg["strip_urls"],
            strip_mentions=cfg["strip_mentions"],
        )
    )
    posts["n_tokens"] = posts["text_clean"].str.split().str.len()
    n_before = len(posts)
    posts = posts[posts["n_tokens"] >= min_length].reset_index(drop=True)
    logger.info("Filtered %d → %d posts (min_length=%d)", n_before, len(posts), min_length)
    return posts


@click.command()
@click.option("--input", "input_path", type=click.Path(exists=True), default=None)
@click.option("--output", type=click.Path(), default=None)
def main(input_path: str | None, output: str | None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    in_path = Path(input_path) if input_path else (
        resolve_path(CONFIG["paths"]["data_raw"]) / CONFIG["data"]["truthsocial"]["output_file"]
    )
    out_path = Path(output) if output else (
        resolve_path(CONFIG["paths"]["data_processed"]) / "posts_clean.parquet"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    posts = pd.read_parquet(in_path)
    cleaned = preprocess_posts(posts, min_length=CONFIG["preprocessing"]["min_post_length"])
    cleaned.to_parquet(out_path, index=False)
    logger.info("Wrote %d cleaned posts to %s", len(cleaned), out_path)


if __name__ == "__main__":
    main()
