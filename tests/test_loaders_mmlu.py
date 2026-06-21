"""Tests for MMLU loader normalization."""

from __future__ import annotations

import pandas as pd
import pytest

from dataset_visualizer.loaders.mmlu import _normalize_answer, load_mmlu


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        (0, "A"),
        (1, "B"),
        (2, "C"),
        (3, "D"),
        ("b", "B"),
    ],
)
def test_normalize_answer(answer: int | str, expected: str) -> None:
    assert _normalize_answer(answer) == expected


def test_load_mmlu_normalizes_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = pd.DataFrame(
        {
            "question": ["Q1"],
            "choices": [["a", "b", "c", "d"]],
            "answer": [2],
            "subject": ["physics"],
        }
    )

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.mmlu.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    load_mmlu.clear()

    df = load_mmlu(split="test")

    assert len(df) == 1
    assert df.loc[0, "answer_letter"] == "C"
    assert df.loc[0, "split"] == "test"
    assert df.loc[0, "subject"] == "physics"
