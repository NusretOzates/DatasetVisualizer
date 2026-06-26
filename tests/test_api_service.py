"""Tests for the dataset API service."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from dataset_visualizer.api.filters import apply_filters
from dataset_visualizer.api.service import (
    DatasetContext,
    clear_filtered_context_cache,
    decode_private_tests_api,
    find_sample,
    get_catalog,
    get_dataset_meta,
    get_filter_options,
    get_overview,
    get_sample,
    parse_json_param,
)


@pytest.fixture(autouse=True)
def _clear_filtered_context_cache() -> None:
    clear_filtered_context_cache()
    yield
    clear_filtered_context_cache()


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
    assert meta["viewer"] == "mmlu"
    assert meta["controls"] == []
    assert meta["source_link"] == {
        "url": "https://huggingface.co/datasets/cais/mmlu",
        "label": "cais/mmlu",
        "kind": "huggingface",
    }


def test_get_dataset_meta_for_tau3_bench_uses_github_source() -> None:
    meta = get_dataset_meta("tau3_bench")
    assert meta["source_link"]["kind"] == "github"
    assert meta["source_link"]["url"] == "https://github.com/sierra-research/tau2-bench"


def test_get_catalog_home_rows_include_source_links() -> None:
    catalog = get_catalog()
    mmlu_row = next(row for row in catalog["home_rows"] if row["dataset"] == "MMLU")
    assert mmlu_row["source_link"]["label"] == "cais/mmlu"


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
    overview = get_overview("mmlu", {}, {})
    assert len(overview["metrics"]) == 3
    assert overview["tables"] == []


def test_get_filter_options_multiselect_and_radio(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "dataset_visualizer.api.service._load_context",
        lambda dataset_id, params: DatasetContext(
            df=pd.DataFrame({"has_image": [True, False]}),
            extras={},
        ),
    )
    result = get_filter_options("hle", {})
    assert result["options"]["modality"] == ["All", "Text only", "Multimodal"]
    assert result["columns"] == ["has_image"]


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


def test_decode_private_tests_api_serializes_decoded_json() -> None:
    """Regression: decode path must import serialize_value (LiveCodeBench sample tab)."""
    cases = [{"input": "1", "output": "2", "testtype": "stdin"}]
    result = decode_private_tests_api(json.dumps(cases))
    assert result == {"cases": cases}


def test_load_context_gated_dataset_raises_actionable_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeDescriptor:
        def loader(self, _params: dict[str, object]) -> tuple[pd.DataFrame, dict[str, object]]:
            msg = "Dataset 'Idavidrein/gpqa' is a gated dataset on the Hub."
            raise RuntimeError(msg)

    monkeypatch.setattr(
        "dataset_visualizer.api.service.get_descriptor",
        lambda _dataset_id: FakeDescriptor(),
    )

    with pytest.raises(ValueError, match="gated on Hugging Face") as exc_info:
        get_filter_options("gpqa_diamond", {})

    assert "HF_TOKEN" in str(exc_info.value)
