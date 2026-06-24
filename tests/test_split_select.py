"""Tests for Hugging Face split auto-selection."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from dataset_visualizer.loaders import split_select


def test_select_smallest_split_prefers_fewer_rows() -> None:
    split_select.select_smallest_split.cache_clear()
    info = MagicMock()
    info.splits = {
        "train": MagicMock(num_examples=1000),
        "test": MagicMock(num_examples=100),
        "validation": MagicMock(num_examples=200),
    }

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            split_select,
            "get_dataset_config_info",
            lambda hf_id, config_name=None: info,
        )
        assert split_select.select_smallest_split("org/example") == "test"


def test_select_smallest_split_breaks_ties_by_preference() -> None:
    split_select.select_smallest_split.cache_clear()
    info = MagicMock()
    info.splits = {
        "train": MagicMock(num_examples=50),
        "validation": MagicMock(num_examples=50),
        "dev": MagicMock(num_examples=50),
    }

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            split_select,
            "get_dataset_config_info",
            lambda hf_id, config_name=None: info,
        )
        assert split_select.select_smallest_split("org/example") == "validation"


def test_select_smallest_split_raises_when_no_splits() -> None:
    split_select.select_smallest_split.cache_clear()
    info = MagicMock()
    info.splits = {}

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            split_select,
            "get_dataset_config_info",
            lambda hf_id, config_name=None: info,
        )
        with pytest.raises(ValueError, match="no published splits"):
            split_select.select_smallest_split("org/empty")


def test_select_smallest_split_falls_back_to_preference_without_row_counts() -> None:
    split_select.select_smallest_split.cache_clear()
    info = MagicMock()
    info.splits = {
        "train": {"name": "train", "dataset_name": "org/example"},
        "test": {"name": "test", "dataset_name": "org/example"},
    }

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            split_select,
            "get_dataset_config_info",
            lambda hf_id, config_name=None: info,
        )
        assert split_select.select_smallest_split("org/example") == "test"
