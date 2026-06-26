"""Generic overview payloads for catalog benchmarks."""

from __future__ import annotations

from typing import Any

import pandas as pd

from dataset_visualizer.api.overview import _nunique_str, _split_label

CATEGORY_COLUMNS = (
    "category",
    "subject",
    "domain",
    "competition",
    "sector",
    "occupation",
    "level",
    "difficulty",
    "problem_type",
    "event_type",
    "scenario_id",
)


def _category_column(df: pd.DataFrame) -> str | None:
    for column in CATEGORY_COLUMNS:
        if column in df.columns and df[column].nunique() > 1:
            return column
    return None


def overview_generic(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    """Build a benchmark-aware overview for catalog benchmarks."""
    metrics: list[dict[str, str]] = [
        {"label": "Total rows", "value": f"{len(df):,}"},
        {"label": "Split", "value": _split_label(df)},
    ]
    category_column = _category_column(df)
    if category_column:
        metrics.append({"label": "Groups", "value": _nunique_str(df, category_column)})

    return {"metrics": metrics, "tables": []}
