"""Tests for the dataset API service."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from dataset_visualizer.api.filters import apply_filters
from dataset_visualizer.api.service import (
    DatasetContext,
    decode_private_tests_api,
    find_sample,
    get_catalog,
    get_dataset_meta,
    get_filter_options,
    get_overview,
    get_sample,
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
    assert meta["viewer"] == "mcq"
    assert meta["controls"][0]["name"] == "split"


def test_get_dataset_meta_unknown_id_raises() -> None:
    with pytest.raises(ValueError, match="Unknown dataset id"):
        get_dataset_meta("not_a_dataset")


def test_parse_json_param_accepts_dict_and_string() -> None:
    assert parse_json_param('{"split": "test"}') == {"split": "test"}
    assert parse_json_param({"split": "dev"}) == {"split": "dev"}
    assert parse_json_param(None) == {}


def test_parse_json_param_invalid_json_raises() -> None:
    with pytest.raises(ValueError, match="Invalid JSON parameter"):
        parse_json_param("{not-json")


def test_apply_filters_subject_multiselect() -> None:
    df = pd.DataFrame({"subject": ["math", "physics", "math"]})
    schema = [{"name": "subjects", "label": "Subject", "type": "multiselect", "column": "subject"}]
    filtered = apply_filters(df, schema, {"subjects": ["math"]})
    assert len(filtered) == 2
    assert set(filtered["subject"]) == {"math"}


def _mmlu_context() -> DatasetContext:
    return DatasetContext(
        df=pd.DataFrame(
            {
                "subject": ["math", "physics"],
                "answer_letter": ["A", "B"],
                "split": ["test", "test"],
            }
        ),
        extras={},
    )


def test_get_overview_mmlu_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "dataset_visualizer.api.service._load_context",
        lambda dataset_id, params: _mmlu_context(),
    )
    overview = get_overview("mmlu", {"split": "test"}, {})
    assert len(overview["metrics"]) == 3
    assert len(overview["charts"]) == 2


def test_get_filter_options_multiselect_and_radio(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "dataset_visualizer.api.service._load_context",
        lambda dataset_id, params: DatasetContext(
            df=pd.DataFrame({"has_image": [True, False]}),
            extras={},
        ),
    )
    options = get_filter_options("hle", {})
    assert options["modality"] == ["All", "Text only", "Multimodal"]


def test_get_sample_returns_row(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "dataset_visualizer.api.service._load_context",
        lambda dataset_id, params: _mmlu_context(),
    )
    sample = get_sample("mmlu", 1, {}, {})
    assert sample["total"] == 2
    assert sample["index"] == 1
    assert sample["row"]["subject"] == "physics"


def test_find_sample_by_id_column(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "dataset_visualizer.api.service._load_context",
        lambda dataset_id, params: _mmlu_context(),
    )
    result = find_sample("mmlu", "physics", {}, {})
    assert result["index"] == 1
    assert result["row"]["subject"] == "physics"


def test_decode_private_tests_api_empty() -> None:
    assert decode_private_tests_api("") == {"cases": []}


def test_decode_private_tests_api_returns_serialized_cases(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "dataset_visualizer.api.service.decode_private_test_cases",
        lambda _raw: [{"input": "1", "output": "2"}],
    )
    result = decode_private_tests_api("encoded")
    assert result == {"cases": [{"input": "1", "output": "2"}]}
