"""Tests for schema-driven dataset filters."""

from __future__ import annotations

import pandas as pd

from dataset_visualizer.api.filters import apply_filters


def test_apply_filters_noop_without_filters() -> None:
    df = pd.DataFrame({"subject": ["math", "physics"]})
    filtered = apply_filters(df, [{"name": "subjects", "type": "multiselect", "column": "subject"}], {})
    assert filtered.equals(df.reset_index(drop=True))


def test_apply_filters_hle_modality_text_only() -> None:
    df = pd.DataFrame({"has_image": [True, False, False]})
    schema = [{"name": "modality", "label": "Modality", "type": "radio"}]
    filtered = apply_filters(df, schema, {"modality": "Text only"})
    assert len(filtered) == 2
