"""Scrape Donald Trump's Truth Social posts via trumpstruth.org RSS feed.

Geen authenticatie, geen ToS-grijszone. De RSS endpoint accepteert date-parameters
zoals gedocumenteerd op https://trumpstruth.org/faq.

Usage:
    python -m src.data.scrape_trumpstruth_rss --start 2026-02-28 --end 2026-05-18

Output:
    data/raw/posts_live.parquet — schema-compatibel met posts.parquet
    (post_id, timestamp_utc, text, url + scrape metadata)
"""

from __future__ import annotations

import logging
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from pathlib import Path

import click
import pandas as pd
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://trumpstruth.org/feed"


def parse_rss(xml_text: str) -> list[dict]:
    """Parse trumpstruth.org RSS feed XML naar lijst van dicts."""
    root = ET.fromstring(xml_text)
    posts = []

    # Standaard RSS 2.0 structure: rss > channel > item*
    for item in root.iter("item"):
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        pub_date = item.findtext("pubDate", default="").strip()
        description = item.findtext("description", default="").strip()
        guid = item.findtext("guid", default="").strip()

        # Convert pubDate (RFC 822 format: "Wed, 03 May 2026 22:51:00 +0000")
        try:
            ts = pd.to_datetime(pub_date, utc=True)
        except Exception:
            ts = None

        # post_id uit URL halen (e.g., /statuses/38158)
        post_id = link.rsplit("/", 1)[-1] if link else guid

        posts.append({
            "post_id": post_id,
            "timestamp_utc": ts,
            "text": description or title,  # description bevat de post-inhoud
            "url": link,
            "title": title,
        })

    return posts


def fetch_range(start: date, end: date, throttle_sec: float = 1.0) -> pd.DataFrame:
    """Haal posts op tussen [start, end] in chunks van max 31 dagen.

    De RSS feed retourneert mogelijk een gelimiteerd aantal items per request.
    We splitsen daarom op per maand om volledigheid te garanderen.
    """
    all_posts = []
    chunk_start = start

    while chunk_start <= end:
        chunk_end = min(chunk_start + timedelta(days=30), end)
        params = {
            "start_date": chunk_start.isoformat(),
            "end_date": chunk_end.isoformat(),
        }
        logger.info("Fetching %s → %s", chunk_start, chunk_end)
        resp = requests.get(BASE_URL, params=params, timeout=30,
                            headers={"User-Agent": "thesis-research-scraper/0.1"})
        resp.raise_for_status()

        posts = parse_rss(resp.text)
        logger.info("  got %d posts", len(posts))
        all_posts.extend(posts)

        chunk_start = chunk_end + timedelta(days=1)
        time.sleep(throttle_sec)  # vriendelijk voor de server

    df = pd.DataFrame(all_posts)
    if df.empty:
        return df

    # Drop duplicates (post_id is unique)
    df = df.drop_duplicates(subset="post_id").reset_index(drop=True)
    df = df.sort_values("timestamp_utc").reset_index(drop=True)
    return df


def clean_html_from_text(text: str) -> str:
    """Verwijder simpele HTML tags uit description (RSS bevat soms <p>, <br>, etc.)."""
    if not isinstance(text, str):
        return ""
    import re
    text = re.sub(r"<[^>]+>", " ", text)  # strip alle HTML tags
    text = re.sub(r"\s+", " ", text).strip()
    return text


@click.command()
@click.option("--start", required=True, help="Start date YYYY-MM-DD")
@click.option("--end", default=None, help="End date YYYY-MM-DD (default: today)")
@click.option("--output", default=None, help="Output parquet path")
def main(start: str, end: str | None, output: str | None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    start_date = pd.Timestamp(start).date()
    end_date = pd.Timestamp(end).date() if end else date.today()

    if start_date > end_date:
        raise ValueError(f"start {start_date} > end {end_date}")

    project_root = Path(__file__).resolve().parent.parent.parent
    out_path = Path(output) if output else (project_root / "data" / "raw" / "posts_live.parquet")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = fetch_range(start_date, end_date)

    if df.empty:
        logger.warning("Geen posts gevonden in [%s, %s]", start_date, end_date)
        return

    # Cleaning
    df["text"] = df["text"].apply(clean_html_from_text)

    logger.info("Total unique posts: %d", len(df))
    logger.info("Date range in result: %s → %s",
                df["timestamp_utc"].min(), df["timestamp_utc"].max())
    logger.info("Writing to %s", out_path)
    df.to_parquet(out_path, index=False)
    logger.info("Done.")


if __name__ == "__main__":
    main()
