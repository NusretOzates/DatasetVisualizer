"""Tests for AIME 2026 loader normalization."""

from __future__ import annotations

import pandas as pd
import pytest

from dataset_visualizer.loaders.aime_2026 import load_aime_2026

SAMPLE_ROW = {
    "problem_idx": 1,
    "problem": "Find $m + n$ when the distance is $\\frac{m}{n}$ miles.",
    "answer": 277,
}


def test_load_aime_2026_casts_problem_idx(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = pd.DataFrame([SAMPLE_ROW, {**SAMPLE_ROW, "problem_idx": 2, "answer": 421}])

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.aime_2026.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    load_aime_2026.clear()

    df = load_aime_2026()

    assert pd.api.types.is_string_dtype(df["problem_idx"])
    assert df.loc[0, "problem_idx"] == "1"
    assert df.loc[1, "problem_idx"] == "2"
    assert df.loc[0, "answer"] == 277
    assert "problem" in df.columns
