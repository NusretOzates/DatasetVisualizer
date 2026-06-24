"""Tests for MMMLU loader normalization."""

from __future__ import annotations

import pandas as pd
import pytest

from dataset_visualizer.loaders.mmmlu import (
    _normalize_mmmlu_frame,
    load_mmmlu,
)

SAMPLE_ROW = {
    "Unnamed: 0": 42,
    "Question": "What is force?",
    "A": "F=ma",
    "B": "F=mv",
    "C": "F=m/a",
    "D": "F=a/m",
    "Answer": "A",
    "Subject": "physics",
}


def test_normalize_mmmlu_frame() -> None:
    raw = pd.DataFrame([SAMPLE_ROW])
    df = _normalize_mmmlu_frame(raw, locale="DE_DE", split="test")

    assert df.loc[0, "question"] == "What is force?"
    assert df.loc[0, "choices"] == ["F=ma", "F=mv", "F=m/a", "F=a/m"]
    assert df.loc[0, "answer_letter"] == "A"
    assert df.loc[0, "subject"] == "physics"
    assert df.loc[0, "sample_id"] == "DE_DE_42"
    assert df.loc[0, "language"] == "DE_DE"
    assert df.loc[0, "split"] == "test"


def test_load_mmmlu(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = pd.DataFrame([SAMPLE_ROW])

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.mmmlu.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    monkeypatch.setattr(
        "dataset_visualizer.loaders.mmmlu.select_smallest_split",
        lambda *_args, **_kwargs: "test",
    )
    load_mmmlu.clear()

    df = load_mmmlu(locale="FR_FR")
    assert len(df) == 1
    assert df.loc[0, "sample_id"] == "FR_FR_42"
    assert df.loc[0, "language"] == "FR_FR"
