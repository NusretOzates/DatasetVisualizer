"""Tests for ZebraLogic benchmark normalization and overview."""

from __future__ import annotations

import pandas as pd

from dataset_visualizer.api.generic_overview import overview_generic
from dataset_visualizer.loaders.benchmark_normalize import normalize_zebra_logic


def test_normalize_zebra_logic_does_not_create_answer_letter() -> None:
    df = pd.DataFrame(
        {
            "puzzle": ["Grid puzzle"],
            "question": ["Who owns the bird?"],
            "choices": [["BOB", "ALICE", "ERIC"]],
            "answer": ["BOB"],
        }
    )

    normalized = normalize_zebra_logic(df, "id")

    assert "answer_letter" not in normalized.columns
    assert normalized["answer"].iloc[0] == "BOB"


def test_overview_generic_omits_answer_pie_for_zebra_logic_answers() -> None:
    df = pd.DataFrame(
        {
            "question": ["Who owns the bird?", "Who has roses?"],
            "answer": ["BOB", "ALICE"],
            "choices": [["BOB", "ALICE"], ["BOB", "ALICE"]],
            "split": ["test", "test"],
        }
    )

    overview = overview_generic(df, {})
    titles = {chart["title"] for chart in overview["charts"]}

    assert "Answer letter distribution" not in titles
