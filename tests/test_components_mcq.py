"""Tests for MCQ viewer helpers."""

from __future__ import annotations

import pandas as pd

from dataset_visualizer.components.mcq_viewer import format_options, resolve_correct_letter


def test_resolve_correct_letter_from_answer_letter() -> None:
    row = pd.Series({"answer_letter": "c"})
    assert resolve_correct_letter(row) == "C"


def test_resolve_correct_letter_from_int_answer() -> None:
    row = pd.Series({"answer": 1})
    assert resolve_correct_letter(row) == "B"


def test_resolve_correct_letter_from_answer_index() -> None:
    row = pd.Series({"answer_index": 3})
    assert resolve_correct_letter(row) == "D"


def test_format_options_filters_na() -> None:
    options = format_options(["Yes", "N/A", "No", "Maybe", "N/A"])
    letters = [letter for letter, _ in options]
    texts = [text for _, text in options]
    assert letters == ["A", "B", "C"]
    assert texts == ["Yes", "No", "Maybe"]


def test_format_options_empty_input() -> None:
    assert format_options(None) == []
    assert format_options([]) == []
