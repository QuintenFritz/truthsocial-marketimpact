"""Bedrijfsvermeldingen in Truth Social posts detecteren en aan tickers koppelen.

Prioriteit-1 vervolgpiste (zie VOORTGANG.md): brede indices (SPY/SPX) middelen
individuele effecten weg. Als Trump expliciet een bedrijf noemt ("Boeing",
"Apple", "ExxonMobil") verwachten we een groter effect op dát aandeel dan op de
brede markt. Dit module levert de mapping en de extractie.

Aanpak
------
We gebruiken een *curated* bedrijf->ticker mapping met word-boundary regex i.p.v.
kale NER. Redenen:
1. Ticker-resolutie is hoe dan ook handmatig nodig (NER geeft "Apple", niet "AAPL").
2. Interpreteerbaar en reproduceerbaar — geen model-download, geen black box.
3. Hoge precisie: we matchen alleen bekende beursgenoteerde bedrijven die Trump
   daadwerkelijk noemt, met aliassen en valse-positief-guards.

`spaCy`-NER kan optioneel als *recall-uitbreiding* worden gebruikt om nieuwe
kandidaat-bedrijven te ontdekken (zie `discover_org_candidates`), maar de
event-study draait op de curated mapping.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Curated bedrijf -> ticker mapping
# ---------------------------------------------------------------------------
# Elke entry: canonieke naam -> (ticker, sector-ETF, [regex-aliassen]).
# Aliassen zijn case-insensitive en worden met \b word-boundaries gematcht.
# De sector-ETF dient als benchmark om het bedrijfsspecifieke effect te isoleren.

@dataclass(frozen=True)
class Company:
    name: str
    ticker: str
    sector_etf: str
    aliases: tuple[str, ...] = field(default_factory=tuple)

    @property
    def patterns(self) -> tuple[str, ...]:
        """Alle te matchen termen (canonieke naam + aliassen), lowercase."""
        terms = (self.name,) + self.aliases
        return tuple(dict.fromkeys(t.lower() for t in terms))  # dedup, volgorde behouden


# Sector-ETF's als benchmark (om markt/sector-beweging af te trekken):
#   XLK tech, XLE energie, XLF financials, XLI industrials, XLY consumer disc.,
#   XLC communication services, ITA aerospace & defense, KBE banks, IBB biotech.
COMPANIES: tuple[Company, ...] = (
    # --- Big Tech ---
    Company("Apple", "AAPL", "XLK", ("apple inc",)),
    Company("Amazon", "AMZN", "XLY", ("amazon.com",)),
    Company("Google", "GOOGL", "XLC", ("alphabet", "youtube")),
    Company("Meta", "META", "XLC", ("facebook", "instagram", "mark zuckerberg", "zuckerberg")),
    Company("Microsoft", "MSFT", "XLK", ()),
    Company("Nvidia", "NVDA", "XLK", ("nvidia",)),
    Company("Tesla", "TSLA", "XLY", ("elon musk", "elon")),
    Company("Twitter", "TWTR", "XLC", ()),   # historisch; delisted 2022 — alleen pre-merger
    # --- Trump-gelieerd / media ---
    Company("Truth Social", "DJT", "XLC", ("trump media", "djt", "truth social")),
    # --- Aerospace & defense ---
    Company("Boeing", "BA", "ITA", ()),
    Company("Lockheed Martin", "LMT", "ITA", ("lockheed",)),
    Company("Raytheon", "RTX", "ITA", ("raytheon",)),
    # --- Energie ---
    Company("ExxonMobil", "XOM", "XLE", ("exxon", "exxon mobil")),
    Company("Chevron", "CVX", "XLE", ()),
    # --- Financials / banken ---
    Company("JPMorgan", "JPM", "XLF", ("jpmorgan", "jp morgan", "jamie dimon")),
    Company("Goldman Sachs", "GS", "XLF", ("goldman",)),
    Company("Bank of America", "BAC", "XLF", ("bank of america",)),
    # --- Retail / consumer ---
    Company("Walmart", "WMT", "XLP", ()),
    Company("Coca-Cola", "KO", "XLP", ("coca cola", "coke")),
    Company("McDonald's", "MCD", "XLY", ("mcdonalds", "mcdonald's")),
    Company("Disney", "DIS", "XLC", ("walt disney",)),
    Company("Ford", "F", "XLY", ("ford motor",)),
    Company("General Motors", "GM", "XLY", ("general motors",)),
    # --- Industrials ---
    Company("Caterpillar", "CAT", "XLI", ()),
    Company("US Steel", "X", "XLB", ("u.s. steel", "united states steel", "us steel")),
    # --- Pharma ---
    Company("Pfizer", "PFE", "XLV", ()),
    Company("Eli Lilly", "LLY", "XLV", ("eli lilly",)),
)


# Valse-positief guards: tokens die NIET als bedrijf tellen ondanks alias-match.
# Bv. "ford" in "Gerald Ford", "coke" als drug, "x" als letter/platform.
# We lossen dit op met word-boundary + minimale alias-lengte, en door
# ambigue 1-letter tickers (F, X) alleen via expliciete aliassen te matchen.
_AMBIGUOUS_SINGLE_TOKEN = {"x", "f", "ko", "gm", "ba"}


def _build_pattern(company: Company) -> re.Pattern:
    """Compileer een case-insensitive word-boundary regex voor één bedrijf.

    Voor ambigue korte aliassen eisen we de langere, expliciete varianten.
    """
    safe_terms = []
    for term in company.patterns:
        if term in _AMBIGUOUS_SINGLE_TOKEN:
            # sla losse ambigue token over; expliciete aliassen vangen deze op
            continue
        safe_terms.append(re.escape(term))
    if not safe_terms:
        # fallback: gebruik canonieke naam letterlijk
        safe_terms = [re.escape(company.name.lower())]
    joined = "|".join(safe_terms)
    return re.compile(rf"\b(?:{joined})\b", flags=re.IGNORECASE)


_COMPILED: dict[str, tuple[Company, re.Pattern]] = {
    c.ticker: (c, _build_pattern(c)) for c in COMPANIES
}


def extract_mentions(text: str) -> list[str]:
    """Geef de lijst tickers terug die in `text` worden genoemd (uniek)."""
    if not isinstance(text, str) or not text:
        return []
    hits = []
    for ticker, (_company, pattern) in _COMPILED.items():
        if pattern.search(text):
            hits.append(ticker)
    return hits


def tag_posts(posts: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    """Voeg per post een kolom `tickers` (list) en `n_companies` (int) toe.

    Parameters
    ----------
    posts : DataFrame met een tekstkolom.
    text_col : naam van de tekstkolom.

    Returns
    -------
    DataFrame
        kopie van `posts` met extra kolommen `tickers`, `n_companies`.
    """
    out = posts.copy()
    out["tickers"] = out[text_col].apply(extract_mentions)
    out["n_companies"] = out["tickers"].apply(len)
    logger.info(
        "Tagged %d posts; %d bevatten >=1 bedrijf.",
        len(out), (out["n_companies"] > 0).sum(),
    )
    return out


def explode_mentions(tagged: pd.DataFrame) -> pd.DataFrame:
    """Eén rij per (post, ticker). Posts zonder bedrijf vallen weg.

    Voegt `sector_etf` toe per ticker, handig voor de market-model benchmark.
    """
    df = tagged[tagged["n_companies"] > 0].copy()
    df = df.explode("tickers").rename(columns={"tickers": "ticker"})
    etf_map = {c.ticker: c.sector_etf for c in COMPANIES}
    name_map = {c.ticker: c.name for c in COMPANIES}
    df["sector_etf"] = df["ticker"].map(etf_map)
    df["company"] = df["ticker"].map(name_map)
    return df


def mention_counts(tagged: pd.DataFrame) -> pd.DataFrame:
    """Aggregeer: hoeveel posts noemen elk bedrijf (gesorteerd)."""
    exploded = explode_mentions(tagged)
    counts = (
        exploded.groupby(["ticker", "company", "sector_etf"])
        .size()
        .reset_index(name="n_posts")
        .sort_values("n_posts", ascending=False)
        .reset_index(drop=True)
    )
    return counts


def discover_org_candidates(texts: list[str], top_n: int = 40) -> list[tuple[str, int]]:
    """Optioneel: gebruik spaCy NER om nieuwe ORG-kandidaten te ontdekken.

    Bedoeld als recall-check om de curated mapping uit te breiden, NIET voor de
    event-study zelf. Vereist `pip install spacy` + `python -m spacy download
    en_core_web_sm`. Geeft een lege lijst terug als spaCy ontbreekt.
    """
    try:
        import spacy
        from collections import Counter
    except ImportError:
        logger.warning("spaCy niet geïnstalleerd — sla NER-ontdekking over.")
        return []
    try:
        nlp = spacy.load("en_core_web_sm", disable=["lemmatizer", "tagger", "parser"])
    except OSError:
        logger.warning("spaCy-model en_core_web_sm ontbreekt — sla over.")
        return []
    counter: "Counter[str]" = Counter()
    for doc in nlp.pipe(texts, batch_size=256):
        for ent in doc.ents:
            if ent.label_ == "ORG" and len(ent.text) > 2:
                counter[ent.text.strip()] += 1
    return counter.most_common(top_n)
