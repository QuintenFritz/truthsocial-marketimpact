"""Truth Social posts collector.

We mikken op @realDonaldTrump posts vanaf de Truth Social launch (feb 2022)
tot vandaag. Twee mogelijke bronnen:

1. **truthbrush** (https://github.com/stanfordio/truthbrush) — unofficial Python
   client. Vereist login credentials. Werk in academische context, niet voor
   commercieel gebruik.
2. **trumpstruth.org** archive — heeft een statische JSON/CSV dump die
   regelmatig wordt geüpdatet. Geen auth nodig.

Voor de scriptie: download EERST een complete dump (bv. via trumpstruth.org)
zodat je niet afhankelijk bent van een werkende scraper midden in week 4.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

import click
import pandas as pd

from src.config import CONFIG, resolve_path

logger = logging.getLogger(__name__)


def fetch_posts_truthbrush(
    user: str,
    start_date: str | date,
    end_date: str | date | None = None,
) -> pd.DataFrame:
    """Scrape posts via truthbrush.

    TODO: implement na `pip install truthbrush` + login flow.
    Placeholder die NotImplementedError raised; vervang door echte call.

    Returns
    -------
    DataFrame
        Kolommen: post_id, timestamp_utc, text, reposts, favorites, replies, url.
    """
    raise NotImplementedError(
        "Implementeer truthbrush integratie of gebruik fetch_posts_archive()."
    )


def fetch_posts_archive(archive_path: Path | str) -> pd.DataFrame:
    """Load posts uit een lokale archive dump (CSV of JSON van trumpstruth.org).

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

    # TODO: kolom-mapping aanpassen aan daadwerkelijke archive schema
    expected_cols = {"post_id", "timestamp_utc", "text"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Archive mist verwachte kolommen: {missing}")

    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
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

    if archive:
        logger.info("Loading from archive: %s", archive)
        df = fetch_posts_archive(archive)
    else:
        logger.info("Scraping via truthbrush — user=%s start=%s", cfg["user"], cfg["start_date"])
        df = fetch_posts_truthbrush(cfg["user"], cfg["start_date"], cfg["end_date"])

    logger.info("Loaded %d posts. Writing to %s", len(df), out_path)
    df.to_parquet(out_path, index=False)


if __name__ == "__main__":
    main()
