"""Smoke tests voor text preprocessing."""

from __future__ import annotations

import pandas as pd

from src.data.preprocess import clean_text, preprocess_posts


class TestCleanText:
    def test_lowercase(self) -> None:
        assert clean_text("HELLO World") == "hello world"

    def test_strip_url(self) -> None:
        out = clean_text("check this https://example.com/path here")
        assert "https" not in out
        assert "example.com" not in out

    def test_strip_mention(self) -> None:
        out = clean_text("hey @realDonaldTrump look")
        assert "@realdonaldtrump" not in out

    def test_keep_hashtag_word(self) -> None:
        out = clean_text("vote #MAGA today")
        assert "maga" in out
        assert "#" not in out

    def test_handles_non_string(self) -> None:
        assert clean_text(None) == ""  # type: ignore[arg-type]
        assert clean_text(42) == ""  # type: ignore[arg-type]


class TestPreprocessPosts:
    def test_filters_short_posts(self) -> None:
        df = pd.DataFrame({
            "text": ["short", "this is a much longer post with more than ten tokens in it for sure"],
            "timestamp_utc": pd.to_datetime(["2024-01-01", "2024-01-02"], utc=True),
        })
        out = preprocess_posts(df, min_length=10)
        assert len(out) == 1
        assert "longer" in out["text_clean"].iloc[0]
