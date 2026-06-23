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
    titles = {chart["title"] for chart in overview["charts"]}

    assert overview["metrics"][:3] == [
        {"label": "Total rows", "value": "3"},
        {"label": "Split", "value": "test"},
        {"label": "Groups", "value": "2"},
    ]
    assert "Rows per subject" in titles
    assert "Rows per difficulty" in titles
    assert "Answer letter distribution" in titles
    assert "Choice count distribution" in titles
    assert "Question length" in titles


def test_overview_generic_adds_date_timeline() -> None:
    df = pd.DataFrame(
        {
            "event_type": ["market", "news"],
            "date": ["2025-01-01", "2025-02-01"],
            "split": ["train", "train"],
        }
    )

    overview = overview_generic(df, {})

    assert any(chart["type"] == "timeline" for chart in overview["charts"])


def test_overview_generic_skips_answer_pie_for_high_cardinality() -> None:
    df = pd.DataFrame(
        {
            "subject": ["logic"] * 20,
            "answer_letter": [f"ANSWER_{index}" for index in range(20)],
            "split": ["test"] * 20,
        }
    )

    overview = overview_generic(df, {})
    titles = {chart["title"] for chart in overview["charts"]}

    assert "Answer letter distribution" not in titles
