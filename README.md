# Truth Social → S&P 500 & WTI olieprijs

Eindwerk Data Science. Predictive en interpretable modeling van Donald Trump's
Truth Social posts vs. short-term abnormal returns op de S&P 500 index en de
WTI ruwe-olieprijs, met TF-IDF / FinBERT features en Random Forest + SHAP.

## Onderzoeksvraag

Welke woorden of n-grams in Trump's Truth Social posts hebben de grootste
voorspellende kracht voor abnormal returns op respectievelijk de S&P 500 en
WTI olie, over time windows van 1u, 1d en 3d?

Zie `reports/scriptie/` voor het volledige projectplan en de scriptie.

## Setup

```bash
# Python 3.11+
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Of met uv:
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

Voor de optionele FinBERT features:

```bash
pip install -e ".[nlp]"
```

## Data

Posts en marktdata worden NIET in de repo gecheckt. Run de collection scripts:

```bash
python -m src.data.collect_truthsocial --start 2022-02-01 --output data/raw/posts.parquet
python -m src.data.collect_market --output data/raw/market.parquet
```

## Reproduceerbare pipeline

```bash
# 1. Data collection (eenmalig)
python -m src.data.collect_truthsocial
python -m src.data.collect_market

# 2. Preprocessing + alignment
python -m src.data.preprocess

# 3. Features
python -m src.features.tfidf
python -m src.features.abnormal_returns

# 4. Modeling
python -m src.models.random_forest --asset spx --window 1d

# 5. Interpretability
python -m src.evaluation.interpretability --model models/rf_spx_1d.joblib
```

Of stap-voor-stap via de notebooks in `notebooks/`.

## Structuur

```
truthsocial-marketimpact/
├── data/                # raw + processed (niet gecommit)
├── notebooks/           # 01..06 — exploratory analyse
├── src/                 # productie-code
│   ├── data/            # scrapers, downloaders, preprocessing
│   ├── features/        # TF-IDF, sentiment, abnormal returns
│   ├── models/          # baseline + Random Forest
│   └── evaluation/      # metrics + SHAP/permutation importance
├── app/                 # Streamlit dashboard
├── reports/             # figures + scriptie source
└── tests/               # pytest suite
```

## Tests

```bash
pytest tests/
```

## Dashboard

```bash
streamlit run app/streamlit_app.py
```

## Licentie

MIT. Zie `LICENSE`.
