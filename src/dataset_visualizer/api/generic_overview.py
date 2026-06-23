"""Generic overview payloads for catalog benchmarks."""

from __future__ import annotations

from typing import Any

import pandas as pd

from dataset_visualizer.api.chart_data import pie_chart_data, value_counts_chart
from dataset_visualizer.api.overview import _nunique_str, _split_label


def _category_column(df: pd.DataFrame) -> str | None:
    for column in (
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
    ):
        if column in df.columns and df[column].nunique() > 1:
            return column
    return None


def overview_generic(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    """Build a lightweight overview for catalog benchmarks."""
    metrics: list[dict[str, str]] = [
        {"label": "Total rows", "value": f"{len(df):,}"},
        {"label": "Split", "value": _split_label(df)},
    ]
    category_column = _category_column(df)
    if category_column:
        metrics.append({"label": "Groups", "value": _nunique_str(df, category_column)})

    charts: list[dict[str, Any]] = []
    if category_column:
        charts.append(
            value_counts_chart(
                df[category_column],
                title=f"Rows per {category_column.replace('_', ' ')}",
                x_label=category_column.replace("_", " ").title(),
            )
        )
    if "answer_letter" in df.columns:
        charts.append(pie_chart_data(df["answer_letter"], title="Answer letter distribution"))

    return {"metrics": metrics, "charts": charts, "tables": []}
