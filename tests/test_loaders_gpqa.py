"""Tests for GPQA Diamond loader normalization."""

from __future__ import annotations

import pandas as pd
import pytest

from dataset_visualizer.loaders.gpqa import (
    _normalize_gpqa_frame,
    _shuffle_choices,
    load_gpqa_diamond,
)

SAMPLE_ROW = {
    "Question": "What is 2+2?",
    "Correct Answer": "4",
    "Incorrect Answer 1": "3",
    "Incorrect Answer 2": "5",
    "Incorrect Answer 3": "22",
}


def test_shuffle_choices_is_deterministic() -> None:
    first = _shuffle_choices("q1", "4", ["3", "5", "22"])
    second = _shuffle_choices("q1", "4", ["3", "5", "22"])
    assert first == second
    assert len(first[0]) == 4
    assert first[1] in {"A", "B", "C", "D"}


def test_normalize_gpqa_frame_builds_mcq_columns() -> None:
    raw = pd.DataFrame([SAMPLE_ROW])
    df = _normalize_gpqa_frame(raw)

    assert len(df.loc[0, "choices"]) == 4
    assert df.loc[0, "answer_letter"] in {"A", "B", "C", "D"}
    assert df.loc[0, "question"] == "What is 2+2?"
    assert df.loc[0, "split"] == "gpqa_diamond"


def test_load_gpqa_diamond(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = pd.DataFrame([SAMPLE_ROW])

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.gpqa.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    load_gpqa_diamond.clear()

    df = load_gpqa_diamond()
    assert len(df) == 1
    assert "choices" in df.columns
