"""Tests for benchmark normalization helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from dataset_visualizer.loaders.benchmark_normalize import (
    normalize_arc,
    normalize_arc_agi,
    normalize_hellaswag,
    normalize_piqa,
    normalize_winogrande,
)


def test_normalize_arc_maps_answer_key() -> None:
    df = pd.DataFrame(
        {
            "id": ["1"],
            "question": ["What is 2+2?"],
            "choices": [{"text": ["3", "4"], "label": ["A", "B"]}],
            "answerKey": ["B"],
        }
    )
    normalized = normalize_arc(df, "id")
    assert normalized["choices"].iloc[0] == ["3", "4"]
    assert normalized["answer_letter"].iloc[0] == "B"


def test_normalize_winogrande_maps_options() -> None:
    df = pd.DataFrame(
        {
            "sentence": ["The trophy does not fit in the suitcase because it is too large."],
            "option1": ["the trophy"],
            "option2": ["the suitcase"],
            "answer": ["1"],
        }
    )
    normalized = normalize_winogrande(df, "sample_id")
    assert normalized["choices"].iloc[0] == ["the trophy", "the suitcase"]
    assert normalized["answer_letter"].iloc[0] == "A"


def test_normalize_hellaswag_maps_endings() -> None:
    df = pd.DataFrame(
        {
            "ctx": ["A person opens a door"],
            "endings": [["then leaves", "then sings"]],
            "label": [0],
        }
    )
    normalized = normalize_hellaswag(df, "sample_id")
    assert normalized["answer_letter"].iloc[0] == "A"
    assert normalized["choices"].iloc[0] == ["then leaves", "then sings"]


def test_normalize_hellaswag_accepts_string_labels() -> None:
    df = pd.DataFrame(
        {
            "ctx": ["A person opens a door"],
            "endings": [["then leaves", "then sings"]],
            "label": ["1"],
        }
    )
    normalized = normalize_hellaswag(df, "sample_id")
    assert normalized["answer_letter"].iloc[0] == "B"


def test_normalize_piqa_maps_solutions() -> None:
    df = pd.DataFrame(
        {
            "goal": ["Boil water"],
            "sol1": ["Use a kettle"],
            "sol2": ["Use a freezer"],
            "label": [0],
        }
    )
    normalized = normalize_piqa(df, "sample_id")
    assert normalized["answer_letter"].iloc[0] == "A"


def test_normalize_arc_agi_serializes_nested_arrays() -> None:
    df = pd.DataFrame(
        {
            "question": [
                {
                    "train": [
                        {
                            "input": np.array([[0, 1], [1, 0]]),
                            "output": np.array([[1, 0], [0, 1]]),
                        }
                    ],
                    "test": [{"input": [[0]], "output": [[1]]}],
                }
            ],
        }
    )

    normalized = normalize_arc_agi(df, "sample_id")

    assert '"train"' in normalized["puzzle_json"].iloc[0]
    assert "array(" not in normalized["puzzle_json"].iloc[0]
