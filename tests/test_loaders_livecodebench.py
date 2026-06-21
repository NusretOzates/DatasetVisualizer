"""Tests for LiveCodeBench loader normalization and private-test decoding."""

from __future__ import annotations

import base64
import json
import pickle
import zlib

import pandas as pd
import pytest

from dataset_visualizer.loaders.livecodebench import (
    _normalize_livecodebench_frame,
    decode_private_test_cases,
    load_livecodebench,
)

SAMPLE_ROW = {
    "question_title": "Two Sum",
    "question_content": "Given an array of integers...",
    "platform": "leetcode",
    "question_id": "lc_1",
    "contest_id": "weekly_400",
    "contest_date": "2024-05-12T00:00:00",
    "starter_code": "class Solution:\n    def twoSum(self, nums, target):\n        pass",
    "difficulty": "easy",
    "public_test_cases": json.dumps(
        [
            {
                "input": "[2,7,11,15]\n9",
                "output": "[0,1]",
                "testtype": "functional",
            }
        ]
    ),
    "private_test_cases": json.dumps(
        [{"input": "a", "output": "b", "testtype": "stdin"}],
    ),
    "metadata": json.dumps({"func_name": "twoSum"}),
}


def _encode_compressed_private(cases: list[dict[str, str]]) -> str:
    """Build a base64+zlib+pickle private-test payload like the HF dataset."""
    payload = json.dumps(cases)
    compressed = zlib.compress(pickle.dumps(payload))
    return base64.b64encode(compressed).decode("utf-8")


def test_decode_private_test_cases_plain_json() -> None:
    cases = [{"input": "1", "output": "2", "testtype": "stdin"}]
    encoded = json.dumps(cases)
    assert decode_private_test_cases(encoded) == cases


def test_decode_private_test_cases_compressed() -> None:
    cases = [{"input": "x", "output": "y", "testtype": "functional"}]
    encoded = _encode_compressed_private(cases)
    assert decode_private_test_cases(encoded) == cases


def test_normalize_livecodebench_frame_parses_columns() -> None:
    raw = pd.DataFrame([SAMPLE_ROW])
    df = _normalize_livecodebench_frame(raw)

    assert len(df) == 1
    assert df.loc[0, "public_test_count"] == 1
    assert df.loc[0, "metadata"]["func_name"] == "twoSum"
    assert df.loc[0, "public_test_cases"][0]["testtype"] == "functional"
    assert str(df.loc[0, "contest_date"].date()) == "2024-05-12"
    assert df.loc[0, "private_test_cases"] == SAMPLE_ROW["private_test_cases"]


def test_load_livecodebench_from_jsonl(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = pd.DataFrame([SAMPLE_ROW])

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.livecodebench.hf_hub_download",
        lambda *args, **kwargs: "/tmp/test6.jsonl",
    )
    monkeypatch.setattr(
        "dataset_visualizer.loaders.livecodebench.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    load_livecodebench.clear()

    df = load_livecodebench()

    assert len(df) == 1
    assert df.loc[0, "question_id"] == "lc_1"
    assert df.loc[0, "platform"] == "leetcode"
    assert df.loc[0, "public_test_count"] == 1
