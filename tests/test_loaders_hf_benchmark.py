"""Tests for generic Hugging Face benchmark loader."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

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


def test_load_hf_benchmark_entry_uses_smallest_split(monkeypatch: pytest.MonkeyPatch) -> None:
    entry = DatasetEntry.model_validate(
        {
            "id": "arc_challenge",
            "label": "ARC Challenge",
            "loader": "hf_benchmark",
            "description": "ARC Challenge benchmark.",
            "hf_id": "allenai/ai2_arc",
            "hf_config": "ARC-Challenge",
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
    captured: dict[str, str] = {}

    def _fake_load_single(hf_id: str, hf_config: str | None, split: str) -> pd.DataFrame:
        captured["split"] = split
        frame = raw.copy()
        frame["split"] = split
        return frame

    monkeypatch.setattr(
        "dataset_visualizer.loaders.hf_benchmark.select_smallest_split",
        lambda *_args, **_kwargs: "validation",
    )
    monkeypatch.setattr(
        "dataset_visualizer.loaders.hf_benchmark._load_single",
        _fake_load_single,
    )

    df = load_hf_benchmark_entry(entry)

    assert captured["split"] == "validation"
    assert df["split"].iloc[0] == "validation"


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


def test_resolve_split_uses_representative_config_for_multi_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = DatasetEntry.model_validate(
        {
            "id": "math",
            "label": "MATH",
            "loader": "hf_benchmark",
            "description": "MATH benchmark.",
            "hf_id": "EleutherAI/hendrycks_math",
            "profile": "math_competition",
            "id_column": "problem_idx",
            "multi_config": True,
        }
    )
    captured: dict[str, str | None] = {}

    monkeypatch.setattr(
        "dataset_visualizer.loaders.hf_benchmark._config_names",
        lambda *_args, **_kwargs: ["algebra", "geometry"],
    )
    monkeypatch.setattr(
        "dataset_visualizer.loaders.hf_benchmark.select_smallest_split",
        lambda hf_id, hf_config: captured.update({"hf_id": hf_id, "hf_config": hf_config})
        or "test",
    )

    from dataset_visualizer.loaders.hf_benchmark import _resolve_split

    assert _resolve_split(entry) == "test"
    assert captured == {
        "hf_id": "EleutherAI/hendrycks_math",
        "hf_config": "algebra",
    }


def test_resolve_split_uses_yaml_split_when_set() -> None:
    entry = DatasetEntry.model_validate(
        {
            "id": "hellaswag",
            "label": "HellaSwag",
            "loader": "hf_benchmark",
            "description": "HellaSwag benchmark.",
            "hf_id": "Rowan/hellaswag",
            "profile": "hellaswag",
            "id_column": "sample_id",
            "split": "validation",
        }
    )

    from dataset_visualizer.loaders.hf_benchmark import _resolve_split

    assert _resolve_split(entry) == "validation"


def test_resolve_split_uses_yaml_split_for_commonsenseqa() -> None:
    entry = DatasetEntry.model_validate(
        {
            "id": "commonsenseqa",
            "label": "CommonsenseQA",
            "loader": "hf_benchmark",
            "description": "CommonsenseQA benchmark.",
            "hf_id": "tau/commonsense_qa",
            "profile": "commonsenseqa",
            "id_column": "id",
            "split": "validation",
        }
    )

    from dataset_visualizer.loaders.hf_benchmark import _resolve_split

    assert _resolve_split(entry) == "validation"
