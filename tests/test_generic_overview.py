"""Tests for generic benchmark overview payloads."""

from __future__ import annotations

import pandas as pd

from dataset_visualizer.api.generic_overview import overview_generic


def test_overview_generic_uses_benchmark_columns() -> None:
    df = pd.DataFrame(
        {
            "subject": ["math", "math", "science"],
            "difficulty": ["easy", "hard", "hard"],
            "answer_letter": ["A", "B", "A"],
            "choices": [["1", "2"], ["1", "2", "3"], ["1", "2"]],
            "question": ["What is $1+1$?", "Explain gravity.", "Pick the molecule."],
            "split": ["test", "test", "test"],
        }
    )

    overview = overview_generic(df, {})

    assert overview["metrics"] == [
        {"label": "Total rows", "value": "3"},
        {"label": "Split", "value": "test"},
        {"label": "Groups", "value": "2"},
    ]
    assert overview["tables"] == []


def test_overview_generic_without_grouping_column() -> None:
    df = pd.DataFrame(
        {
            "choices": [["1", "2"], ["3", "4"], ["5", "6"]],
            "question": ["Q1?", "Q2?", "Q3?"],
            "split": ["test", "test", "test"],
        }
    )

    overview = overview_generic(df, {"dataset_id": "winogrande"})

    assert overview["metrics"] == [
        {"label": "Total rows", "value": "3"},
        {"label": "Split", "value": "test"},
    ]


def test_overview_generic_uses_first_multi_value_category_column() -> None:
    df = pd.DataFrame(
        {
            "event_type": ["market", "news"],
            "date": ["2025-01-01", "2025-02-01"],
            "split": ["train", "train"],
        }
    )

    overview = overview_generic(df, {})

    assert overview["metrics"][-1] == {"label": "Groups", "value": "2"}
