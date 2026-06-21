"""Tests for the home page row-count helpers."""

from __future__ import annotations

import pandas as pd
import pytest

from dataset_visualizer.config import DatasetEntry, load_config
from dataset_visualizer.row_count import format_row_count, row_count


def _entry(**overrides: object) -> DatasetEntry:
    """Build a minimal dataset entry for home page tests."""
    data = {
        "id": "gpqa_diamond",
        "label": "GPQA Diamond",
        "loader": "gpqa",
    }
    data.update(overrides)
    return DatasetEntry.model_validate(data)


def test_format_row_count_adds_problems_suffix_for_arxivmath() -> None:
    assert format_row_count(40, "arxivmath") == "40 problems"
    assert format_row_count(198, "gpqa") == "198"


def test_row_count_uses_loader_result_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "dataset_visualizer.row_count.load_dataset_frame",
        lambda loader_name: pd.DataFrame({"x": [1, 2, 3]}),
    )

    assert row_count(_entry(loader="mmlu")) == "3"


def test_row_count_falls_back_to_config_when_loader_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(_loader_name: str) -> pd.DataFrame:
        msg = "gated dataset"
        raise RuntimeError(msg)

    monkeypatch.setattr("dataset_visualizer.row_count.load_dataset_frame", _raise)

    assert row_count(_entry(row_count=198)) == "198"


def test_row_count_returns_error_when_loader_fails_without_config_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(_loader_name: str) -> pd.DataFrame:
        msg = "download failed"
        raise RuntimeError(msg)

    monkeypatch.setattr("dataset_visualizer.row_count.load_dataset_frame", _raise)

    assert row_count(_entry()) == "error"


def test_row_count_uses_config_for_unregistered_loader() -> None:
    assert row_count(_entry(loader="missing_loader", row_count=42)) == "42"


def test_gpqa_diamond_config_has_row_count_fallback() -> None:
    config = load_config()
    gpqa = next(entry for entry in config.categories["reasoning"] if entry.id == "gpqa_diamond")
    assert gpqa.row_count == 198
