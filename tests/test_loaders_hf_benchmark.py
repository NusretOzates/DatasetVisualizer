"""Tests for generic Hugging Face benchmark loader."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd

from dataset_visualizer.config import DatasetEntry
from dataset_visualizer.loaders.hf_benchmark import load_hf_benchmark_entry


def test_load_hf_benchmark_entry_normalizes_arc() -> None:
    entry = DatasetEntry.model_validate(
        {
            "id": "arc_challenge",
            "label": "ARC Challenge",
            "loader": "hf_benchmark",
            "description": "ARC Challenge benchmark.",
            "hf_id": "allenai/ai2_arc",
            "hf_config": "ARC-Challenge",
            "split": "test",
            "profile": "arc",
            "id_column": "id",
        }
    )
    raw = pd.DataFrame(
        {
            "id": ["q1"],
            "question": ["Which is heavier?"],
            "choices": [{"text": ["rock", "feather"], "label": ["A", "B"]}],
            "answerKey": ["A"],
        }
    )

    with patch(
        "dataset_visualizer.loaders.hf_benchmark._load_frame",
        return_value=raw,
    ):
        df = load_hf_benchmark_entry(entry)

    assert df["answer_letter"].iloc[0] == "A"
    assert df["choices"].iloc[0] == ["rock", "feather"]


def test_load_hf_benchmark_entry_reads_jsonl_source() -> None:
    entry = DatasetEntry.model_validate(
        {
            "id": "apps",
            "label": "APPS",
            "loader": "hf_benchmark",
            "description": "APPS benchmark.",
            "hf_id": "codeparrot/apps",
            "source_file": "test.jsonl",
            "profile": "apps",
            "id_column": "id",
        }
    )
    raw = pd.DataFrame(
        {
            "id": [1],
            "question": ["Write factorial"],
            "difficulty": ["interview"],
            "starter_code": ["def fact(n): pass"],
        }
    )

    with patch(
        "dataset_visualizer.loaders.hf_benchmark._load_frame",
        return_value=raw,
    ):
        df = load_hf_benchmark_entry(entry)

    assert df["question_content"].iloc[0] == "Write factorial"
    assert df["question_id"].iloc[0] == "1"
