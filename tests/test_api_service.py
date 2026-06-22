"""Tests for the dataset API service."""

from __future__ import annotations

import pandas as pd
import pytest

from dataset_visualizer.api.service import (
    _apply_filters,
    get_catalog,
    get_dataset_meta,
    get_overview,
    parse_json_param,
)


def test_get_catalog_includes_registered_datasets() -> None:
    catalog = get_catalog()
    dataset_ids = {
        dataset["id"] for category in catalog["categories"] for dataset in category["datasets"]
    }
    assert "mmlu" in dataset_ids
    assert "arxivmath_0526" in dataset_ids
    assert len(catalog["home_rows"]) >= 12


def test_get_dataset_meta_for_mmlu() -> None:
    meta = get_dataset_meta("mmlu")
    assert meta["id"] == "mmlu"
    assert meta["id_column"] == "subject"
    assert meta["controls"][0]["name"] == "split"


def test_parse_json_param_accepts_dict_and_string() -> None:
    assert parse_json_param('{"split": "test"}') == {"split": "test"}
    assert parse_json_param({"split": "dev"}) == {"split": "dev"}
    assert parse_json_param(None) == {}


def test_apply_filters_subject_multiselect(monkeypatch: pytest.MonkeyPatch) -> None:
    df = pd.DataFrame({"subject": ["math", "physics", "math"]})
    filtered = _apply_filters("mmlu", df, {"subjects": ["math"]})
    assert len(filtered) == 2
    assert set(filtered["subject"]) == {"math"}


def test_get_overview_mmlu_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    sample = pd.DataFrame(
        {
            "subject": ["math", "physics"],
            "answer_letter": ["A", "B"],
            "split": ["test", "test"],
        }
    )
    monkeypatch.setattr(
        "dataset_visualizer.api.service.load_mmlu",
        lambda **kwargs: sample,
    )
    overview = get_overview("mmlu", {"split": "test"}, {})
    assert len(overview["metrics"]) == 3
    assert len(overview["charts"]) == 2
