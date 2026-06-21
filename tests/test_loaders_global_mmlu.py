"""Tests for Global-MMLU loader normalization."""

from __future__ import annotations

import pandas as pd
import pytest

from dataset_visualizer.loaders.global_mmlu import (
    _normalize_global_mmlu_frame,
    _parse_annotation_list,
    load_global_mmlu,
)

SAMPLE_ROW = {
    "sample_id": "en_001",
    "subject": "physics",
    "subject_category": "STEM",
    "question": "What is force?",
    "option_a": "F=ma",
    "option_b": "F=mv",
    "option_c": "F=m/a",
    "option_d": "F=a/m",
    "answer": "A",
    "required_knowledge": "['none']",
    "time_sensitive": "No",
    "reference": "[]",
    "culture": "[]",
    "region": "[]",
    "country": "[]",
    "cultural_sensitivity_label": "CA",
    "is_annotated": False,
}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("['cultural', 'none']", ["cultural", "none"]),
        (["x"], ["x"]),
        ("", []),
    ],
)
def test_parse_annotation_list(raw: object, expected: list[str]) -> None:
    assert _parse_annotation_list(raw) == expected


def test_normalize_global_mmlu_frame() -> None:
    raw = pd.DataFrame([SAMPLE_ROW])
    df = _normalize_global_mmlu_frame(raw, language="en", split="dev")

    assert df.loc[0, "choices"] == ["F=ma", "F=mv", "F=m/a", "F=a/m"]
    assert df.loc[0, "answer_letter"] == "A"
    assert df.loc[0, "language"] == "en"
    assert df.loc[0, "required_knowledge"] == ["none"]


def test_load_global_mmlu(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = pd.DataFrame([SAMPLE_ROW])

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.global_mmlu.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    load_global_mmlu.clear()

    df = load_global_mmlu(language="en", split="dev")
    assert len(df) == 1
    assert df.loc[0, "sample_id"] == "en_001"
