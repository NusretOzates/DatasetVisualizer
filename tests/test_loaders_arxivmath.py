"""Tests for ArXiv Math 0526 loader normalization."""

from __future__ import annotations

import pandas as pd
import pytest

from dataset_visualizer.loaders.arxivmath import load_outputs, load_problems


def test_load_problems_casts_problem_idx(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = pd.DataFrame(
        {
            "problem_idx": [1, 2],
            "title": ["Paper A", "Paper B"],
            "problem": ["Find x", "Find y"],
            "answer": ["42", "7"],
            "source": ["1234.5678", "2345.6789"],
            "authors": ["Alice", "Bob, Carol"],
        }
    )

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.arxivmath.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    load_problems.clear()

    df = load_problems()

    assert pd.api.types.is_string_dtype(df["problem_idx"])
    assert df.loc[0, "problem_idx"] == "1"
    assert df.loc[1, "problem_idx"] == "2"


def test_load_outputs_casts_problem_idx(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = pd.DataFrame(
        {
            "problem_idx": [1, 2],
            "model_name": ["model-a", "model-b"],
            "correct": [True, False],
            "parsed_answer": ["42", "8"],
            "gold_answer": ["42", "7"],
            "input_tokens": [100, 120],
            "output_tokens": [50, 60],
            "cost": [0.01, 0.02],
            "idx_answer": [0, 0],
            "answer": ["The answer is 42", "The answer is 8"],
            "user_message": ["Solve this", "Solve that"],
        }
    )

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.arxivmath.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    load_outputs.clear()

    df = load_outputs()

    assert pd.api.types.is_string_dtype(df["problem_idx"])
    assert set(df["problem_idx"]) == {"1", "2"}


def test_problem_idx_join_after_cast(monkeypatch: pytest.MonkeyPatch) -> None:
    problems_raw = pd.DataFrame(
        {
            "problem_idx": [1],
            "title": ["Paper A"],
            "problem": ["Find x"],
            "answer": ["42"],
            "source": ["1234.5678"],
            "authors": ["Alice"],
        }
    )
    outputs_raw = pd.DataFrame(
        {
            "problem_idx": ["1"],
            "model_name": ["model-a"],
            "correct": [True],
            "parsed_answer": ["42"],
            "gold_answer": ["42"],
            "input_tokens": [100],
            "output_tokens": [50],
            "cost": [0.01],
            "idx_answer": [0],
            "answer": ["The answer is 42"],
            "user_message": ["Solve this"],
        }
    )

    class FakeProblems:
        def to_pandas(self) -> pd.DataFrame:
            return problems_raw.copy()

    class FakeOutputs:
        def to_pandas(self) -> pd.DataFrame:
            return outputs_raw.copy()

    def fake_load_dataset(repo_id: str, split: str = "train") -> object:
        if repo_id.endswith("arxivmath-0526_outputs"):
            return FakeOutputs()
        return FakeProblems()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.arxivmath.load_dataset",
        fake_load_dataset,
    )
    load_problems.clear()
    load_outputs.clear()

    problems = load_problems()
    outputs = load_outputs()
    merged = outputs.merge(problems, on="problem_idx", suffixes=("_out", "_prob"))

    assert len(merged) == 1
    assert merged.loc[0, "title"] == "Paper A"
    assert merged.loc[0, "model_name"] == "model-a"
