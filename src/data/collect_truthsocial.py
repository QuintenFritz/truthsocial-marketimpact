"""Truth Social posts collector.

We mikken op @realDonaldTrump posts vanaf de Truth Social launch (feb 2022)
tot vandaag. We scrapen Truth Social NIET rechtstreeks; we werken uitsluitend
met publiek beschikbare archieven/mirrors:

1. **Kaggle-archief** — statische CSV-dump van het @realDonaldTrump account.
   Vormt de historische bulk. Geen auth nodig.
2. **trumpstruth.org** — externe mirror met RSS-feed voor de laatste posts.
   De live-aanvulling gebeurt via `src/data/scrape_trumpstruth_rss.py`.

Deze module laadt het Kaggle-archief en normaliseert het schema. Voor de
live-aanvulling: zie `scrape_trumpstruth_rss.py`.
"""

from __future__ import annotations

import logging
from pathlib import Path

import click
import pandas as pd

from src.config import CONFIG, resolve_path

logger = logging.getLogger(__name__)


def fetch_posts_archive(archive_path: Path | str) -> pd.DataFrame:
    """Load posts uit een lokale archive dump (CSV of JSON, Kaggle-export).

    Parameters
    ----------
    archive_path : Path | str
        Pad naar de gedownloade dump.

    Returns
    -------
    DataFrame
        Genormaliseerd schema. timestamp_utc is timezone-aware UTC.
    """
    path = Path(archive_path)
    if path.suffix == ".csv":
        df = pd.read_csv(path)
    elif path.suffix in {".json", ".jsonl"}:
        df = pd.read_json(path, lines=path.suffix == ".jsonl")
    else:
        raise ValueError(f"Onbekend formaat: {path.suffix}")

    # Schema-mapping: Kaggle-archive kolomnamen → genormaliseerd schema
    rename_map = {
        "id": "post_id",
        "created_at": "timestamp_utc",
        "text": "text",
        "like_count": "favorites",
        "retruth_count": "reposts",
        "reply_count": "replies",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    expected_cols = {"post_id", "timestamp_utc", "text"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Archive mist verwachte kolommen: {missing}")

    # Mixed ISO formats (sommige posts hebben microseconden, andere niet)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True, format="ISO8601")
    # Drop posts without text (media-only) — geen TF-IDF mogelijk
    df = df.dropna(subset=["text"]).reset_index(drop=True)
    df = df.sort_values("timestamp_utc").reset_index(drop=True)
    return df


@click.command()
@click.option("--archive", type=click.Path(exists=True), default=None,
              help="Pad naar gedownloade Truth Social archive (CSV/JSON).")
@click.option("--output", type=click.Path(), default=None,
              help="Output parquet path. Default uit config.yaml.")
def main(archive: str | None, output: str | None) -> None:
    """CLI entrypoint."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    cfg = CONFIG["data"]["truthsocial"]
    out_path = Path(output) if output else (
        resolve_path(CONFIG["paths"]["data_raw"]) / cfg["output_file"]
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not archive:
        raise click.UsageError(
            "--archive is verplicht: geef het pad naar de Kaggle-archive dump (CSV/JSON). "
            "Voor live-aanvulling, gebruik scrape_trumpstruth_rss.py."
        )

    logger.info("Loading from archive: %s", archive)
    df = fetch_posts_archive(archive)

    logger.info("Loaded %d posts. Writing to %s", len(df), out_path)
    df.to_parquet(out_path, index=False)


if __name__ == "__main__":
    main()
