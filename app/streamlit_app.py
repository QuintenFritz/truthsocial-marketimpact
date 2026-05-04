"""Streamlit dashboard — viewer voor model resultaten en post-explorer.

Run: `streamlit run app/streamlit_app.py`

Tabs:
1. Top words per asset — geranked op SHAP/permutation importance.
2. Post explorer — zoek post, toon SHAP-decomposition + actual return.
3. Model performance — metrics per asset/window over de testperiode.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Truth Social → Markets", layout="wide")

st.title("Truth Social → Market Impact Dashboard")
st.caption(
    "Voorspelt en verklaart abnormal returns op de S&P 500 en WTI olie "
    "op basis van Donald Trump's Truth Social posts."
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"


@st.cache_data
def load_aligned_posts() -> pd.DataFrame:
    path = DATA_DIR / "aligned.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


@st.cache_data
def load_top_features(asset: str, window: str) -> pd.DataFrame:
    path = PROJECT_ROOT / "reports" / "figures" / f"top_features_{asset}_{window}.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


tab1, tab2, tab3 = st.tabs(["Top words", "Post explorer", "Model performance"])

with tab1:
    st.header("Welke woorden voorspellen abnormal returns?")
    col1, col2 = st.columns(2)
    asset = col1.selectbox("Asset", ["spx", "wti"])
    window = col2.selectbox("Window", ["1d", "3d"])

    df = load_top_features(asset, window)
    if df.empty:
        st.info("Geen feature-importance bestand gevonden. Run notebook 06 eerst.")
    else:
        st.dataframe(df, use_container_width=True)

with tab2:
    st.header("Post explorer")
    posts = load_aligned_posts()
    if posts.empty:
        st.info("Geen aligned posts gevonden. Run notebook 03 eerst.")
    else:
        query = st.text_input("Zoek post (substring match):")
        if query:
            mask = posts["text_clean"].str.contains(query.lower(), na=False)
            st.write(f"{mask.sum()} matches gevonden")
            st.dataframe(posts[mask].head(50), use_container_width=True)
        else:
            st.dataframe(posts.head(50), use_container_width=True)

with tab3:
    st.header("Model performance")
    st.info("TODO: laad metrics uit models/ + reports/.")
    # Placeholder
    st.metric("Dummy", "TBD")
