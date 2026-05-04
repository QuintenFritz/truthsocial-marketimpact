"""Marktdata loader via yfinance — S&P 500, WTI, VIX, DXY."""

from __future__ import annotations

import logging
from pathlib import Path

import click
import pandas as pd
import yfinance as yf

from src.config import CONFIG, resolve_path

logger = logging.getLogger(__name__)


def download_market_data(
    tickers: dict[str, str],
    start: str,
    end: str | None = None,
    interval: str = "1d",
) -> pd.DataFrame:
    """Download OHLCV voor alle tickers.

    Parameters
    ----------
    tickers : dict
        {alias: ticker_symbol}, bv. {"spx": "^GSPC"}.
    start, end : str
        ISO dates.
    interval : str
        "1d", "1h", "5m" — let op yfinance limieten voor intraday (~60 dagen).

    Returns
    -------
    DataFrame
        MultiIndex (ticker_alias × date), kolommen Open/High/Low/Close/Volume.
    """
    frames = []
    for alias, sym in tickers.items():
        logger.info("Downloading %s (%s)", alias, sym)
        df = yf.download(sym, start=start, end=end, interval=interval, progress=False, auto_adjust=False)
        if df.empty:
            logger.warning("Geen data voor %s", sym)
            continue
        df.columns = [c.lower() for c in df.columns.get_level_values(0)] if df.columns.nlevels > 1 else [c.lower() for c in df.columns]
        df["ticker"] = alias
        df.index.name = "date"
        frames.append(df.reset_index())

    out = pd.concat(frames, ignore_index=True)
    out["date"] = pd.to_datetime(out["date"], utc=True)
    return out


def compute_returns(market: pd.DataFrame) -> pd.DataFrame:
    """Compute log returns per ticker."""
    import numpy as np
    market = market.sort_values(["ticker", "date"]).copy()
    market["log_return"] = market.groupby("ticker")["close"].transform(
        lambda s: np.log(s / s.shift(1))
    )
    return market


@click.command()
@click.option("--output", type=click.Path(), default=None)
def main(output: str | None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = CONFIG["data"]["market"]

    df = download_market_data(
        tickers=cfg["tickers"],
        start=cfg["start_date"],
        end=cfg["end_date"],
        interval=cfg["interval"],
    )
    df = compute_returns(df)

    out_path = Path(output) if output else (resolve_path(CONFIG["paths"]["data_raw"]) / "market.parquet")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Writing %d rows to %s", len(df), out_path)
    df.to_parquet(out_path, index=False)


if __name__ == "__main__":
    main()
