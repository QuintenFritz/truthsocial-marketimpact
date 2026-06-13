# Trump's Truth Social & Financial Markets — Eindwerk Data Science

**Auteur:** Quinten Friederichs  
**Jaar:** 2026  
**Repository:** https://github.com/QuintenFritz/truthsocial-marketimpact

---

## Onderzoeksvraag

*Beïnvloeden Donald Trump's berichten op Truth Social de financiële markten — en zo ja, in welke mate en op welk tijdsschaal?*

We richten ons op twee concrete contexten: de **Liberation Day importheffingencyclus** (april–mei 2025) en de **Iran-oorlog** (februari–juni 2026). Voor beide contexten testen we of Trump als informatieve bron fungeert of simpelweg reageert op bestaand nieuws.

---

## Resultaten in één oogopslag

Alle toetsen gebruiken **bootstrap-95%-confidence-intervals** (resampling) i.p.v. parametrische t-toetsen; een CI dat 0 uitsluit geldt als "significant".

| Analyse | Bevinding |
|---|---|
| Bulk event-study (dagelijks) | Geen significant verschil na Iran- of tariff-posts (alle CI's omvatten 0) |
| Iran intraday-returns | Niet consistent gericht: uur-niveau significant positief (SPY t+4u +14 bp, XLE t+24u +44 bp), minuut-CAR significant negatief (SPY −32 bp/2u); WTI nergens significant |
| Volume rond posts | **Robuust:** tariff SPY +0,32σ, Iran XLE +0,25σ, tariff volume-ratio = **1,50** — alle CI's sluiten 0/1 uit |
| Granger-causaliteit | Posts voorspellen returns niet; WTI-returns voorspellen wél Trumps post-frequentie (lag 2–4 u) → reactief |
| Per aandeel (nb14) | Waar de index niets toont, vertonen losse genoemde bedrijven wél richting: DJT CAR_3d −158 bp en TSLA AR_1d −115 bp (CI's sluiten 0 uit); TSLA fragiel |
| GDELT news-timing | In **100% van gevallen** postte Trump ná het nieuws, gemiddeld **~3 uur later** |

**Hoofdconclusie:** Trump fungeert als nieuwsreageerder, niet als marktbeweger. Er is geen robuust, consistent gericht koerseffect; wat overeind blijft is verhoogd handelsvolume rond posts en een reactief Granger-patroon. De correlaties reflecteren een gemeenschappelijke oorzaak (onderliggend nieuws), geen directe causaliteit.

De volledige scriptie en onderzoeksverslagen worden na de mondelinge verdediging (23 juni 2026) gepubliceerd; tot dan beschikbaar op aanvraag.

---

## Projectstructuur

```
truthsocial-marketimpact/
│
├── notebooks/                          # Analyse-keten (zie volgorde hieronder)
│   ├── 01_data_collection.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_alignment_returns.ipynb
│   ├── 04_features.ipynb
│   ├── 05_modeling_rf.ipynb
│   ├── 06_interpretability.ipynb
│   ├── 07_sentiment_exploration.ipynb
│   ├── 08_sentiment_classifier.ipynb
│   ├── 09_toxicity_classifier.ipynb
│   ├── 10_iran_oil_event_study.ipynb
│   ├── 11_tariffs_liberation_day_event_study.ipynb
│   ├── 12_intraday_event_study.ipynb
│   ├── 13_gdelt_news_timing.ipynb
│   └── 14_individual_stocks_event_study.ipynb   # Event-study per genoemd aandeel
│
├── src/
│   ├── features/company_mentions.py    # Bedrijf→ticker-mapping (per-aandeel event-study)
│   └── evaluation/bootstrap.py         # Bootstrap-CI's voor groeps-/event-verschillen
│
├── scripts/
│   ├── fetch_intraday_twelvedata.py    # 1-minuut marktdata via Twelve Data API
│   └── fetch_gdelt_news_timing.py      # Koppelt posts aan GDELT-nieuwstijdstippen
│
├── data/
│   ├── raw/                            # Brondata (zie sectie Data hieronder)
│   └── processed/                      # Afgeleide datasets (kleine bestanden meegeleverd)
│
└── models/                             # Getrainde classifiers (joblib)
```

> De map `reports/` (scriptie, onderzoeksverslagen, figuren) wordt na de verdediging op 23 juni 2026 toegevoegd.

---

## Data

### Meegeleverd in deze repository

De volgende datasets zijn direct beschikbaar — geen download nodig:

| Bestand | Inhoud | Grootte |
|---|---|---|
| `data/raw/market.parquet` | Dagelijkse OHLCV voor SPX, WTI, DXY, VIX (2022–2026) | 212 KB |
| `data/raw/posts_live.parquet` | Gescrapte posts feb–jun 2026 (2.161 posts, incl. Iran-periode) | 732 KB |
| `data/processed/gdelt_news_timing.parquet` | GDELT news-timing analyse (128 posts) | 36 KB |
| `data/processed/intraday_spy_tariff_1min.parquet` | 1-minuut SPY rond tariff-posts | 296 KB |
| `data/processed/intraday_spy_iran_1min.parquet` | 1-minuut SPY rond Iran-posts | 156 KB |
| `data/processed/intraday_xle_tariff_1min.parquet` | 1-minuut XLE rond tariff-posts | 252 KB |
| `data/processed/intraday_xle_iran_1min.parquet` | 1-minuut XLE rond Iran-posts | 140 KB |

### Handmatig te downloaden: Kaggle archief (~17 MB)

Benodigd voor notebooks 01–14 (de event-studies en de per-aandeel-analyse gebruiken het volledige post-archief).

1. Maak een gratis account op [kaggle.com](https://www.kaggle.com)
2. Download: `https://www.kaggle.com/datasets/[DATASET-LINK-HIER]`
3. Sla op als `data/raw/trump_truth_archive.csv`
4. Draai `01_data_collection.ipynb` om `data/raw/posts.parquet` te genereren

### Optioneel: intraday data opnieuw ophalen

De intraday bestanden zijn meegeleverd. Wil je ze zelf ophalen via Twelve Data:

```bash
# Gratis tier (~1 uur, 534 API-calls)
python scripts/fetch_intraday_twelvedata.py --api-key JOUW_KEY --topic both

# Betaalde tier (sneller)
python scripts/fetch_intraday_twelvedata.py --api-key JOUW_KEY --paid --topic both
```

API-key: [twelvedata.com](https://twelvedata.com) (gratis tier volstaat)

---

## Installatie

```bash
git clone https://github.com/QuintenFritz/truthsocial-marketimpact.git
cd truthsocial-marketimpact

conda create -n truthsocial python=3.11
conda activate truthsocial
pip install -r requirements.txt
```

**requirements.txt:**
```
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
scipy>=1.10
scikit-learn>=1.3
yfinance>=0.2
pyarrow>=12.0
fastparquet
requests>=2.28
beautifulsoup4>=4.12
joblib>=1.3
```

---

## Notebooks uitvoeren

Voor een volledige reproductie, draai de notebooks in volgorde 01 → 14. Draai elke notebook bij voorkeur met **Restart & Run All** om volgorde-afhankelijke fouten te vermijden.

Voor de **kernresultaten** volstaan deze notebooks (alle benodigde data is meegeleverd):

| Notebook | Kernresultaten |
|---|---|
| `12_intraday_event_study.ipynb` | CAR-profielen (bootstrap-CI), volume-ratio, mean reversion |
| `13_gdelt_news_timing.ipynb` | GDELT news-timing: lag-distributie, reactief vs. geen_nieuws |
| `10_iran_oil_event_study.ipynb` | Iran event-study + volume (vereist Kaggle CSV) |
| `11_tariffs_liberation_day_event_study.ipynb` | Liberation Day event-study + volume (vereist Kaggle CSV) |
| `14_individual_stocks_event_study.ipynb` | Event-study per genoemd aandeel (vereist Kaggle CSV) |

---

## Methoden

Inferentie gebeurt overal via **bootstrap-confidence-intervals** (resampling, `src/evaluation/bootstrap.py`) i.p.v. parametrische t-toetsen of Mann-Whitney — robuust tegen de zware staarten van returns en zonder aparte Bonferroni-correctie.

| # | Methode | Notebook |
|---|---|---|
| 1 | Event-study (bootstrap-CI, dagelijks + uur) | nb 10, 11 |
| 2 | Granger-causaliteitstoets | nb 10, 11 |
| 3 | Volume-anomalie + price-timing (bootstrap-CI) | nb 10, 11 |
| 4 | Intraday CAR-analyse 1-minuut (bootstrap-CI) | nb 12 |
| 5 | GDELT news-timing | nb 13 |
| 6 | Event-study per individueel aandeel (market-model AR + bootstrap-CI) | nb 14 |

Classifiers: sentiment (83% acc.) en toxiciteit (86% acc., AUC 0,91) via L1-logistische regressie op TF-IDF features — zie notebooks 08 en 09.

---

## Licentie

MIT — vrij te gebruiken voor academische doeleinden met bronvermelding.
