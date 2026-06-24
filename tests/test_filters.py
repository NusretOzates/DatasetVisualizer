"""Tests for schema-driven dataset filters."""

from __future__ import annotations

import pandas as pd

from dataset_visualizer.api.filters import apply_filters, build_filter_options


def test_apply_filters_noop_without_filters() -> None:
    df = pd.DataFrame({"subject": ["math", "physics"]})
    filtered = apply_filters(
        df, [{"name": "subjects", "type": "multiselect", "column": "subject"}], {}
    )
    assert filtered.equals(df.reset_index(drop=True))


def test_apply_filters_hle_modality_text_only() -> None:
    df = pd.DataFrame({"has_image": [True, False, False]})
    schema = [
        {
            "name": "modality",
            "label": "Modality",
            "type": "radio",
            "column": "has_image",
            "value_map": {"Text only": False, "Multimodal": True},
        }
    ]
    filtered = apply_filters(df, schema, {"modality": "Text only"})
    assert len(filtered) == 2


def test_apply_filters_text_prefix() -> None:
    df = pd.DataFrame({"src": ["foo_1", "bar_2", "foo_3"]})
    schema = [{"name": "src_prefix", "type": "text", "column": "src"}]
    filtered = apply_filters(df, schema, {"src_prefix": "foo"})
    assert len(filtered) == 2


def test_build_filter_options_radio() -> None:
    df = pd.DataFrame({"has_image": [True, False]})
    schema = [
        {
            "name": "modality",
            "type": "radio",
            "options": ["All", "Text only", "Multimodal"],
        }
    ]
    options = build_filter_options(df, schema)
    assert options["modality"] == ["All", "Text only", "Multimodal"]


def test_apply_filters_date_range() -> None:
    df = pd.DataFrame(
        {
            "contest_date": pd.to_datetime(["2024-01-01", "2024-06-01", "2024-12-01"]),
        }
    )
    schema = [{"name": "date_range", "type": "date_range", "column": "contest_date"}]
    filtered = apply_filters(
        df,
        schema,
        {"date_range": {"start": "2024-02-01", "end": "2024-10-01"}},
    )
    assert len(filtered) == 1
