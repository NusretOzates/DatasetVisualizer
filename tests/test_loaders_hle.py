"""Tests for Humanity's Last Exam (HLE) loader normalization."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from dataset_visualizer.loaders.hle import (
    ANSWER_TYPE_EXACT_MATCH,
    ANSWER_TYPE_MULTIPLE_CHOICE,
    _has_image_value,
    _normalize_hle_frame,
    load_hle,
)

SAMPLE_ROW = {
    "id": "q1",
    "question": "What is the capital of France?",
    "image": "",
    "answer": "Paris",
    "answer_type": ANSWER_TYPE_EXACT_MATCH,
    "author_name": "Expert A",
    "rationale": "Paris is the capital.",
    "raw_subject": "Geography",
    "category": "Humanities/Social Science",
}


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", False),
        ("data:image/png;base64,abc", True),
        (None, False),
        (float("nan"), False),
    ],
)
def test_has_image_value(value: object, expected: bool) -> None:
    assert _has_image_value(value) is expected


def test_normalize_hle_frame_adds_metadata_columns() -> None:
    raw = pd.DataFrame([SAMPLE_ROW])
    df = _normalize_hle_frame(raw)

    assert df.loc[0, "split"] == "test"
    assert not df.loc[0, "has_image"]
    assert df.loc[0, "answer_type"] == ANSWER_TYPE_EXACT_MATCH


def test_normalize_hle_frame_detects_multimodal_rows() -> None:
    row = {**SAMPLE_ROW, "image": "data:image/png;base64,abc"}
    df = _normalize_hle_frame(pd.DataFrame([row]))
    assert df.loc[0, "has_image"]


def test_load_hle(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = pd.DataFrame(
        [
            SAMPLE_ROW,
            {
                **SAMPLE_ROW,
                "id": "q2",
                "answer_type": ANSWER_TYPE_MULTIPLE_CHOICE,
                "answer": "B",
                "image": "data:image/png;base64,abc",
            },
        ]
    )

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.hle.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    load_hle.clear()

    df = load_hle()
    assert len(df) == 2
    assert "has_image" in df.columns
    assert not df.loc[0, "has_image"]
    assert df.loc[1, "has_image"]
    assert df.loc[1, "answer_type"] == ANSWER_TYPE_MULTIPLE_CHOICE


def test_hle_row_to_dict_is_json_displayable() -> None:
    """Regression: ``Series.to_json()`` fails on ``image_preview`` JPEG bytes."""
    row = pd.Series(
        {
            **SAMPLE_ROW,
            "image": "data:image/png;base64,abc",
            "image_preview": {"bytes": b"\xff\xd8\xff\xe0\x00\x10JFIF", "path": None},
            "rationale_image": None,
            "has_image": True,
            "split": "test",
        }
    )

    with pytest.raises(OverflowError):
        row.to_json()

    payload = json.dumps(row.to_dict(), default=repr)
    parsed = json.loads(payload)
    assert parsed["id"] == "q1"
    assert "bytes" in parsed["image_preview"]
