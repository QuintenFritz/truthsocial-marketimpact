"""
fetch_gdelt_news_timing.py
--------------------------
Voor elke tariff- en Iran-gerelateerde Trump-post:
1. Download de GDELT Mentions bestanden in het 4u-window VOOR de post
2. Filter op relevante nieuwsbronnen (Reuters, AP, Bloomberg, ...) + keywords in URL
3. Bepaal het tijdstip van het EERSTE nieuwsbericht over het topic
4. Bereken lag: Trump_post_time - first_news_time
   - Positief = Trump postte NA het nieuws (reactief)
   - Negatief = Trump postte VOOR het nieuws (potentieel informatief / vooruitlopend)
5. Sla resultaten op als data/processed/gdelt_news_timing.parquet

Gebruik:
    python scripts/fetch_gdelt_news_timing.py
    python scripts/fetch_gdelt_news_timing.py --topic tariff
    python scripts/fetch_gdelt_news_timing.py --topic iran

Geschatte tijd: 30-60 min (veel kleine downloads, rate-limited door GDELT)
Output: data/processed/gdelt_news_timing.parquet
"""

import argparse
import io
import logging
import time
import zipfile
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import urllib.request
import urllib.error

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Nieuwsbronnen die we als "geloofwaardig nieuws" beschouwen
NEWS_SOURCES = [
    "reuters.com", "apnews.com", "bloomberg.com", "wsj.com",
    "ft.com", "nytimes.com", "washingtonpost.com", "cnbc.com",
    "bbc.co.uk", "bbc.com", "theguardian.com", "politico.com",
    "axios.com", "thehill.com",
]

# Keywords die in de URL van het nieuwsartikel moeten voorkomen
TARIFF_URL_KW = [
    "tariff", "trade-war", "trade-deal", "liberation-day", "liberation_day",
    "import-duty", "china-trade", "trade-deficit", "reciprocal",
    "sanctions", "trade-tension",
]

IRAN_URL_KW = [
    "iran", "tehran", "hormuz", "nuclear-deal", "nuclear_deal",
    "irgc", "ayatollah", "houthi", "persian-gulf",
]

# Hoeveel uur voor de post zoeken we naar nieuws
LOOKBACK_H = 4

# GDELT bestanden zijn beschikbaar per 15 minuten
GDELT_INTERVAL_MIN = 15

SLEEP_BETWEEN_DOWNLOADS = 1.5  # seconden — wees beleefd met GDELT servers


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def gdelt_timestamps_in_window(start: pd.Timestamp, end: pd.Timestamp) -> list:
    """Genereer lijst van GDELT bestandstijdstempels (15-min intervals) in window."""
    ts = start.floor(f"{GDELT_INTERVAL_MIN}min")
    result = []
    while ts <= end:
        result.append(ts)
        ts += pd.Timedelta(minutes=GDELT_INTERVAL_MIN)
    return result


def gdelt_url(ts: pd.Timestamp) -> str:
    return (
        f"http://data.gdeltproject.org/gdeltv2/"
        f"{ts.strftime('%Y%m%d%H%M%S')}.mentions.CSV.zip"
    )


def download_gdelt_mentions(ts: pd.Timestamp) -> pd.DataFrame | None:
    """Download en parse één GDELT mentions bestand. Retourneert None bij fout."""
    url = gdelt_url(ts)
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            zf = zipfile.ZipFile(io.BytesIO(resp.read()))
            fname = zf.namelist()[0]
            df = pd.read_csv(
                zf.open(fname),
                sep="\t",
                header=None,
                usecols=[1, 2, 4, 5, 13],  # EventTime, MentionTime, Source, URL, Tone
                names=["event_time", "mention_time", "source", "url", "tone"],
                dtype=str,
            )
        return df
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # Bestand bestaat niet (normaal voor sommige intervals)
        log.warning(f"HTTP {e.code} voor {ts}: {e}")
        return None
    except Exception as e:
        log.warning(f"Fout bij {ts}: {e}")
        return None


def find_first_news(
    post_time: pd.Timestamp,
    url_keywords: list,
    lookback_h: int = LOOKBACK_H,
) -> dict:
    """
    Zoek het eerste nieuwsbericht over het topic in de `lookback_h` uur vóór de post.
    Retourneert dict met first_news_time, lag_minutes, source, url.
    """
    window_start = post_time - pd.Timedelta(hours=lookback_h)
    timestamps   = gdelt_timestamps_in_window(window_start, post_time)

    earliest_time = None
    earliest_source = None
    earliest_url = None
    earliest_tone = None

    for ts in timestamps:
        df = download_gdelt_mentions(ts)
        time.sleep(SLEEP_BETWEEN_DOWNLOADS)

        if df is None or df.empty:
            continue

        # Filter op bekende nieuwsbronnen
        src_mask = df["source"].str.lower().str.contains(
            "|".join(NEWS_SOURCES), na=False, regex=True
        )
        # Filter op keywords in URL
        kw_mask = df["url"].str.lower().str.contains(
            "|".join(url_keywords), na=False, regex=True
        )
        hits = df[src_mask & kw_mask].copy()

        if hits.empty:
            continue

        # Parseer mention_time
        hits["mention_dt"] = pd.to_datetime(
            hits["mention_time"], format="%Y%m%d%H%M%S", errors="coerce", utc=True
        )
        hits = hits.dropna(subset=["mention_dt"])
        hits = hits[hits["mention_dt"] <= post_time]

        if hits.empty:
            continue

        earliest_hit = hits.loc[hits["mention_dt"].idxmin()]
        if earliest_time is None or earliest_hit["mention_dt"] < earliest_time:
            earliest_time   = earliest_hit["mention_dt"]
            earliest_source = earliest_hit["source"]
            earliest_url    = earliest_hit["url"]
            earliest_tone   = earliest_hit["tone"]

    lag_minutes = (
        (post_time - earliest_time).total_seconds() / 60
        if earliest_time is not None
        else None
    )

    return {
        "first_news_time":    earliest_time,
        "lag_minutes":        lag_minutes,         # positief = Trump NA nieuws
        "news_source":        earliest_source,
        "news_url":           earliest_url,
        "news_tone":          earliest_tone,
        "trump_after_news":   lag_minutes > 0 if lag_minutes is not None else None,
    }


def load_posts(keywords: list, parquet_path: str,
               date_start: str = None, date_end: str = None) -> pd.Series:
    try:
        df = pd.read_parquet(parquet_path, engine="fastparquet")
    except Exception:
        df = pd.read_parquet(parquet_path, engine="pyarrow")
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    pattern = "|".join(keywords)
    mask = df["text"].str.lower().str.contains(pattern, na=False, regex=True)
    result = df[mask][["post_id", "timestamp_utc", "text"]].copy()
    if date_start:
        result = result[result["timestamp_utc"] >= pd.Timestamp(date_start, tz="UTC")]
    if date_end:
        result = result[result["timestamp_utc"] <= pd.Timestamp(date_end, tz="UTC")]
    return result.sort_values("timestamp_utc").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TARIFF_KW = [
    "tariff", "tariffs", "reciprocal", "liberation day", "trade war",
    "trade deal", "trade deficit", "china", "chinese", "beijing",
    "europe", "european union", "canada", "mexico", "retaliat",
    "deal", "pause", "truce", "exemption", "sanction",
]

IRAN_KW = [
    "iran", "iranian", "tehran", "ayatollah", "irgc", "hormuz",
    "persian gulf", "israel", "houthi", "opec", "saudi",
    "oil", "crude", "barrel", "missile", "nuclear", "sanctions",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", choices=["tariff", "iran", "both"], default="both")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max aantal posts per topic (voor testing)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Toon posts zonder GDELT te downloaden")
    args = parser.parse_args()

    out_path = ROOT / "data/processed/gdelt_news_timing.parquet"
    existing = pd.read_parquet(out_path, engine="fastparquet") if out_path.exists() else pd.DataFrame()
    already_done = set(existing["post_id"].astype(str)) if not existing.empty else set()

    topics = {}
    if args.topic in ("tariff", "both"):
        posts = load_posts(TARIFF_KW, str(ROOT / "data/raw/posts.parquet"),
                           "2025-02-01", "2025-07-01")
        topics["tariff"] = (posts, TARIFF_URL_KW)
    if args.topic in ("iran", "both"):
        posts = load_posts(IRAN_KW, str(ROOT / "data/raw/posts_live.parquet"),
                           "2026-02-28", None)
        topics["iran"] = (posts, IRAN_URL_KW)

    all_rows = [existing] if not existing.empty else []

    for topic, (posts_df, url_kw) in topics.items():
        if args.limit:
            posts_df = posts_df.head(args.limit)

        log.info(f"\n=== {topic.upper()}: {len(posts_df)} posts ===")

        # Dedupleer op dag: één post per dag per topic is genoeg
        # (eerste post van die dag, want die is het meest relevant)
        posts_df["date"] = posts_df["timestamp_utc"].dt.date
        posts_df = posts_df.drop_duplicates(subset="date", keep="first")
        log.info(f"Na deduplicatie op dag: {len(posts_df)} unieke dagen")

        for i, (_, row) in enumerate(posts_df.iterrows()):
            pid = str(row["post_id"])
            if pid in already_done:
                log.info(f"  [{i+1}/{len(posts_df)}] Skip (al gedaan): {row['timestamp_utc'].date()}")
                continue

            log.info(f"  [{i+1}/{len(posts_df)}] {row['timestamp_utc']}  {str(row['text'])[:80]}")

            if args.dry_run:
                continue

            result = find_first_news(row["timestamp_utc"], url_kw)
            result["post_id"]       = pid
            result["post_time"]     = row["timestamp_utc"]
            result["post_text"]     = str(row["text"])[:300]
            result["topic"]         = topic
            all_rows.append(pd.DataFrame([result]))

            # Sla elke 10 posts op
            if len(all_rows) % 10 == 0 and not args.dry_run:
                combined = pd.concat(all_rows, ignore_index=True)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                combined.to_parquet(out_path, index=False, engine="fastparquet")
                log.info(f"  → Tussentijds opgeslagen ({len(combined)} rijen)")

    if not args.dry_run and all_rows:
        combined = pd.concat(all_rows, ignore_index=True)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        combined.to_parquet(out_path, index=False, engine="fastparquet")
        log.info(f"\n✅ Klaar. Opgeslagen: {out_path} ({len(combined)} rijen)")

        # Samenvatting
        print("\n=== SAMENVATTING ===")
        print(combined.groupby("topic")["trump_after_news"].value_counts())
        print("\nGemiddelde lag per topic (minuten):")
        print(combined.groupby("topic")["lag_minutes"].describe().round(1))


if __name__ == "__main__":
    main()
