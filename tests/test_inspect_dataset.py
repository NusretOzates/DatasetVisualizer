"""Tests for scripts/inspect_dataset.py CLI."""

from __future__ import annotations

import inspect_dataset as inspect_script
import pandas as pd
import pytest
from inspect_dataset import _format_sample_row, _truncate_value, inspect_dataset


def test_truncate_value_short_string_unchanged() -> None:
    assert _truncate_value("hello") == "hello"


def test_truncate_value_long_string() -> None:
    text = "x" * 300
    result = _truncate_value(text, max_len=50)
    assert isinstance(result, str)
    assert "300 chars" in result
    assert len(result) < 300


def test_truncate_value_long_list() -> None:
    value = list(range(100))
    result = _truncate_value(value, max_len=30)
    assert isinstance(result, str)
    assert "len=100" in result


def test_format_sample_row_truncates_fields() -> None:
    row = pd.Series({"short": "ok", "long": "z" * 500})
    formatted = _format_sample_row(row)
    assert formatted["short"] == "ok"
    assert "500 chars" in str(formatted["long"])


def test_inspect_dataset_unknown_id(capsys: pytest.CaptureFixture[str]) -> None:
    code = inspect_dataset("not_a_real_dataset")
    captured = capsys.readouterr()
    assert code == 1
    assert "Unknown dataset_id" in captured.err
    assert "mmlu" in captured.err


def test_inspect_dataset_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    df = pd.DataFrame(
        {
            "question": ["What is 2+2?"],
            "answer_letter": ["B"],
        }
    )

    class FakeDescriptor:
        def loader(self, _params: dict[str, object]) -> tuple[pd.DataFrame, dict[str, object]]:
            return df, {}

    monkeypatch.setattr(inspect_script, "get_descriptor", lambda _dataset_id: FakeDescriptor())

    code = inspect_dataset("mmlu")
    captured = capsys.readouterr()

    assert code == 0
    assert "MMLU" in captured.out
    assert "Rows: 1" in captured.out
    assert "question" in captured.out
    assert "data/cache/mmlu" in captured.out
    assert "answer_letter: B" in captured.out
