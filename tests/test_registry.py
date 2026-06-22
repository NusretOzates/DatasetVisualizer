"""Registry and config alignment tests."""

from __future__ import annotations

import pandas as pd
import pytest

from dataset_visualizer.api.dataset_registry import DATASET_REGISTRY
from dataset_visualizer.api.filters import build_filter_options
from dataset_visualizer.api.service import DatasetContext, find_sample, get_catalog
from dataset_visualizer.config import load_config


def test_config_dataset_ids_match_dataset_registry() -> None:
    config = load_config()
    config_ids = {
        entry.id for datasets in config.categories.values() for entry in datasets
    }
    assert config_ids == set(DATASET_REGISTRY.keys())


def test_get_catalog_calls_row_count_once_per_dataset(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def _mock_row_count(entry: object) -> str:
        calls.append(entry.id)  # type: ignore[attr-defined]
        return "1"

    monkeypatch.setattr("dataset_visualizer.api.service.row_count", _mock_row_count)
    catalog = get_catalog()
    dataset_count = sum(len(category["datasets"]) for category in catalog["categories"])
    assert len(calls) == dataset_count
    assert len(calls) == len(set(calls))


def test_build_filter_options_date_range() -> None:
    df = pd.DataFrame({"contest_date": pd.to_datetime(["2024-01-01", "2024-12-01"])})
    schema = [{"name": "date_range", "type": "date_range", "column": "contest_date"}]
    options = build_filter_options(df, schema)
    assert options["date_range"]["min"] == "2024-01-01"
    assert options["date_range"]["max"] == "2024-12-01"


def test_find_sample_uses_positional_index(monkeypatch: pytest.MonkeyPatch) -> None:
    df = pd.DataFrame(
        {
            "subject": ["math", "physics", "math"],
            "value": [1, 2, 3],
        },
        index=[5, 5, 7],
    )

    monkeypatch.setattr(
        "dataset_visualizer.api.service._load_context",
        lambda dataset_id, params: DatasetContext(df=df, extras={}),
    )
    result = find_sample("mmlu", "physics", {}, {})
    assert result["index"] == 1
    assert result["row"]["value"] == 2
