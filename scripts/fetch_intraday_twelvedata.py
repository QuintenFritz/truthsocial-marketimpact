"""
fetch_intraday_twelvedata.py
----------------------------
Haalt minuut-level marktdata op via Twelve Data API voor de event-windows
rond tariff- en Iran-gerelateerde Trump posts.

Strategie:
- Overlap-posts worden samengevoegd tot aaneengesloten blokken → zo min mogelijk API calls
- Elke blok = 1 API call per ticker (max 5000 bars/call)
- Output: data/processed/intraday_spy_1min.parquet
          data/processed/intraday_wti_proxy_1min.parquet  (XLE als WTI-proxy)

Gebruik:
    pip install twelvedata pandas pyarrow
    python scripts/fetch_intraday_twelvedata.py --api-key JOUW_KEY

Twelve Data gratis tier: 800 calls/dag
    → ~2-3 dagen voor alle windows (script pauzeert automatisch)
Grow tier ($29/maand): geen daglimiet → klaar in <1 uur

API key aanvragen: https://twelvedata.com/register
Studenten 20% korting: https://twelvedata.com/education
"""

import argparse
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "https://api.twelvedata.com/time_series"

# Tickers: SPY (S&P 500 ETF) + XLE (Energy sector ETF als WTI-proxy)
# Nota: WTI futures (CL=F) zijn beschikbaar op betaalde tiers
TICKERS = {
    "SPY": "SPY",
    "XLE": "XLE",   # WTI-proxy; vervang door "CL1!" op betaalde tier
}

TARIFF_KEYWORDS = [
    "tariff", "tariffs", "import duty", "reciprocal", "liberation day",
    "trade war", "trade deal", "trade deficit",
    "china", "chinese", "beijing", "xi jinping",
    "europe", "european union", "canada", "mexico",
    "retaliat", "decouple", "deal", "negotiat", "pause", "truce", "exemption", "sanction",
]

IRAN_KEYWORDS = [
    "iran", "iranian", "tehran", "ayatollah", "irgc",
    "hormuz", "persian gulf", "israel", "houthi", "opec",
    "saudi", "oil", "crude", "barrel", "missile", "nuclear", "sanctions",
]

WINDOW_H = 2          # uren voor en na elke post
MAX_BARS  = 4500      # veilige marge onder 5000 Twelve Data max
RATE_LIMIT_FREE = 7   # seconden tussen calls op gratis tier (800/dag ≈ 1 per ~108s, maar 8/min ook ok)
RATE_LIMIT_PAID = 0.5 # seconden tussen calls op betaalde tier

ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_posts() -> pd.DataFrame:
    """Laad en combineer archive + live posts."""
    dfs = []
    for p in [ROOT / "data/raw/posts.parquet",
              ROOT / "data/raw/posts_live.parquet"]:
        if p.exists():
            try:
                df = pd.read_parquet(p, engine="fastparquet")
            except Exception:
                df = pd.read_parquet(p, engine="pyarrow")
            df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
            dfs.append(df[["post_id", "timestamp_utc", "text"]])
    combined = pd.concat(dfs, ignore_index=True).drop_duplicates(subset="post_id")
    return combined.sort_values("timestamp_utc").reset_index(drop=True)


def filter_posts(posts: pd.DataFrame, keywords: list) -> pd.Series:
    pattern = "|".join(keywords)
    mask = posts["text"].str.lower().str.contains(pattern, na=False, regex=True)
    return posts[mask]["timestamp_utc"]


def merge_windows(timestamps: pd.Series, window_h: int = 2) -> list[tuple]:
    """Verklein N post-timestamps naar M aaneengesloten (start, end) windows."""
    if len(timestamps) == 0:
        return []
    windows = sorted([
        (t - pd.Timedelta(hours=window_h), t + pd.Timedelta(hours=window_h))
        for t in timestamps
    ])
    merged = [list(windows[0])]
    for start, end in windows[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(s, e) for s, e in merged]


def fetch_window(api_key: str, symbol: str, start: pd.Timestamp,
                 end: pd.Timestamp, sleep_s: float = RATE_LIMIT_FREE) -> pd.DataFrame:
    """Haal 1-minuut data op voor één window en één ticker."""
    params = {
        "symbol": symbol,
        "interval": "1min",
        "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date":   end.strftime("%Y-%m-%d %H:%M:%S"),
        "outputsize": MAX_BARS,
        "timezone": "UTC",
        "apikey": api_key,
        "format": "JSON",
    }
    time.sleep(sleep_s)
    try:
        resp = requests.get(BASE_URL, params=params, timeout=30)
        data = resp.json()
        if data.get("status") == "error":
            log.warning(f"API error voor {symbol} [{start.date()}]: {data.get('message')}")
            return pd.DataFrame()
        values = data.get("values", [])
        if not values:
            return pd.DataFrame()
        df = pd.DataFrame(values)
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
        df["close"]    = df["close"].astype(float)
        df["volume"]   = pd.to_numeric(df.get("volume", pd.Series()), errors="coerce")
        df["ticker"]   = symbol
        return df[["datetime", "ticker", "close", "volume"]].sort_values("datetime")
    except Exception as e:
        log.error(f"Fout bij {symbol}: {e}")
        return pd.DataFrame()


def save_progress(dfs: list, out_path: Path):
    if not dfs:
        return
    combined = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["datetime", "ticker"])
    combined = combined.sort_values(["ticker", "datetime"]).reset_index(drop=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(out_path, index=False)
    log.info(f"  → Opgeslagen: {out_path} ({len(combined):,} rijen)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Fetch intraday data via Twelve Data")
    parser.add_argument("--api-key", required=True, help="Twelve Data API key")
    parser.add_argument("--paid",    action="store_true",
                        help="Gebruik betaalde rate limit (sneller)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Toon windows zonder data te downloaden")
    parser.add_argument("--topic",   choices=["tariff", "iran", "both"], default="both",
                        help="Welk thema ophalen")
    args = parser.parse_args()

    sleep_s = RATE_LIMIT_PAID if args.paid else RATE_LIMIT_FREE
    posts = load_posts()

    # Bepaal windows per thema
    topics = {}
    if args.topic in ("tariff", "both"):
        tariff_ts = filter_posts(posts, TARIFF_KEYWORDS)
        # Beperk tot analysevenster Liberation Day
        tariff_ts = tariff_ts[
            (tariff_ts >= pd.Timestamp("2025-02-01", tz="UTC")) &
            (tariff_ts <= pd.Timestamp("2025-07-01", tz="UTC"))
        ]
        topics["tariff"] = merge_windows(tariff_ts, WINDOW_H)
        log.info(f"Tariff: {len(tariff_ts)} posts → {len(topics['tariff'])} merged windows")

    if args.topic in ("iran", "both"):
        iran_ts = filter_posts(posts, IRAN_KEYWORDS)
        iran_ts = iran_ts[iran_ts >= pd.Timestamp("2026-02-28", tz="UTC")]
        topics["iran"] = merge_windows(iran_ts, WINDOW_H)
        log.info(f"Iran: {len(iran_ts)} posts → {len(topics['iran'])} merged windows")

    total_calls = sum(len(w) for w in topics.values()) * len(TICKERS)
    log.info(f"Totaal API calls gepland: {total_calls}")
    log.info(f"Geschatte tijd op {'betaalde' if args.paid else 'gratis'} tier: "
             f"{total_calls * sleep_s / 60:.0f} minuten")

    if args.dry_run:
        for topic, windows in topics.items():
            print(f"\n=== {topic.upper()} windows ===")
            for i, (s, e) in enumerate(windows[:10]):
                print(f"  {i+1}. {s} → {e}  ({int((e-s).total_seconds()//60)} min)")
            if len(windows) > 10:
                print(f"  ... en {len(windows)-10} meer")
        return

    # Download per thema per ticker
    for topic, windows in topics.items():
        out_paths = {
            ticker: ROOT / f"data/processed/intraday_{ticker.lower()}_{topic}_1min.parquet"
            for ticker in TICKERS
        }
        # Laad eventueel al opgeslagen progress
        existing = {ticker: pd.read_parquet(p) if p.exists() else pd.DataFrame()
                    for ticker, p in out_paths.items()}

        for ticker, symbol in TICKERS.items():
            log.info(f"\n--- {topic.upper()} / {ticker} ({len(windows)} windows) ---")
            all_dfs = [existing[ticker]] if not existing[ticker].empty else []

            already_fetched = set()
            if not existing[ticker].empty:
                already_fetched = set(
                    existing[ticker]["datetime"].dt.floor("4H").dt.strftime("%Y%m%d%H")
                )

            for i, (start, end) in enumerate(windows):
                window_key = start.strftime("%Y%m%d%H")
                if window_key in already_fetched:
                    log.info(f"  [{i+1}/{len(windows)}] Skip (al opgeslagen): {start}")
                    continue

                log.info(f"  [{i+1}/{len(windows)}] {start} → {end}")
                df = fetch_window(args.api_key, symbol, start, end, sleep_s)
                if not df.empty:
                    all_dfs.append(df)
                    log.info(f"    {len(df)} bars opgehaald")

                # Sla elke 50 windows op als tussentijdse backup
                if (i + 1) % 50 == 0:
                    save_progress(all_dfs, out_paths[ticker])

            save_progress(all_dfs, out_paths[ticker])
            log.info(f"✓ {ticker} / {topic} klaar: {out_paths[ticker]}")

    log.info("\n✅ Alle data opgehaald. Controleer data/processed/intraday_*.parquet")


if __name__ == "__main__":
    main()
