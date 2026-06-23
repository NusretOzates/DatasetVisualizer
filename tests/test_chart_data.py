"""Tests for chart payload builders."""

from __future__ import annotations

import pandas as pd

from dataset_visualizer.api.chart_data import answer_letter_pie_chart, pie_chart_data


def test_answer_letter_pie_chart_returns_payload_for_small_cardinality() -> None:
    series = pd.Series(["A", "B", "A"])

    chart = answer_letter_pie_chart(series, title="Answer letter distribution")

    assert chart == pie_chart_data(series, title="Answer letter distribution")


def test_answer_letter_pie_chart_skips_high_cardinality() -> None:
    series = pd.Series([f"ANSWER_{index}" for index in range(20)])

    assert answer_letter_pie_chart(series, title="Answer letter distribution") is None


def test_answer_letter_pie_chart_skips_non_letter_labels() -> None:
    series = pd.Series(["BIRD", "ALICE", "BOB", "BIRD"])

    assert answer_letter_pie_chart(series, title="Answer letter distribution") is None
