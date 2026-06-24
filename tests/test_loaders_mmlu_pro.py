"""Tests for MMLU-Pro loader normalization."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from dataset_visualizer.loaders.mmlu_pro import _filter_options, load_mmlu_pro


def test_filter_options_removes_na_and_empty() -> None:
    options = ["Alpha", "N/A", "", "  ", "Beta", "n/a", "Gamma"]
    assert _filter_options(options) == ["Alpha", "Beta", "Gamma"]


def test_filter_options_handles_numpy_option_arrays() -> None:
    options = np.array(["Alpha", "N/A", "Beta"])
    assert _filter_options(options) == ["Alpha", "Beta"]


def test_load_mmlu_pro_filters_options_and_adds_option_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = pd.DataFrame(
        {
            "question_id": ["q1"],
            "question": ["What is 2+2?"],
            "options": [["A", "N/A", "B", "N/A", "C", "D", "E", "F", "G", "H"]],
            "answer": ["C"],
            "answer_index": [2],
            "category": ["math"],
            "src": ["ori_mmlu-high_school_mathematics"],
            "cot_content": ["Step by step reasoning."],
        }
    )

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.mmlu_pro.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    monkeypatch.setattr(
        "dataset_visualizer.loaders.mmlu_pro.select_smallest_split",
        lambda *_args, **_kwargs: "validation",
    )
    load_mmlu_pro.clear()

    df = load_mmlu_pro()

    assert len(df) == 1
    assert df.loc[0, "options"] == ["A", "B", "C", "D", "E", "F", "G", "H"]
    assert df.loc[0, "option_count"] == 8
    assert df.loc[0, "split"] == "validation"
    assert df.loc[0, "category"] == "math"
