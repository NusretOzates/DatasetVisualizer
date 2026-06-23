"""Generic overview payloads for catalog benchmarks."""

from __future__ import annotations

from typing import Any

import pandas as pd

from dataset_visualizer.api.chart_data import (
    histogram_data,
    pie_chart_data,
    timeline_data,
    value_counts_chart,
)
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
TEXT_COLUMNS = (
    "question",
    "problem",
    "prompt",
    "question_content",
    "context",
    "input",
    "instruction",
)
DATE_COLUMNS = (
    "date",
    "created_at",
    "resolution_date",
    "forecast_date",
    "contest_date",
)


def _category_column(df: pd.DataFrame) -> str | None:
    for column in CATEGORY_COLUMNS:
        if column in df.columns and df[column].nunique() > 1:
            return column
    return None


def _category_columns(df: pd.DataFrame) -> list[str]:
    return [
        column for column in CATEGORY_COLUMNS if column in df.columns and df[column].nunique() > 1
    ]


def _text_length_chart(df: pd.DataFrame) -> dict[str, Any] | None:
    for column in TEXT_COLUMNS:
        if column not in df.columns:
            continue
        lengths = df[column].dropna().astype(str).str.len()
        if not lengths.empty and lengths.max() > 0:
            label = column.replace("_", " ").title()
            return histogram_data(lengths, title=f"{label} length", x_label="Characters")
    return None


def _list_length_chart(
    df: pd.DataFrame, column: str, title: str, x_label: str
) -> dict[str, Any] | None:
    if column not in df.columns:
        return None
    lengths = df[column].map(lambda value: len(value) if isinstance(value, list) else None).dropna()
    if lengths.empty:
        return None
    return histogram_data(lengths, title=title, x_label=x_label)


def _timeline_chart(df: pd.DataFrame) -> dict[str, Any] | None:
    for column in DATE_COLUMNS:
        if column not in df.columns:
            continue
        dates = pd.to_datetime(df[column], errors="coerce").dropna()
        if not dates.empty:
            label = column.replace("_", " ").title()
            return timeline_data(dates, title=f"{label} distribution")
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

    charts: list[dict[str, Any]] = []
    for column in _category_columns(df)[:2]:
        charts.append(
            value_counts_chart(
                df[column],
                title=f"Rows per {column.replace('_', ' ')}",
                x_label=column.replace("_", " ").title(),
                top_n=20,
            )
        )
    if "answer_letter" in df.columns:
        charts.append(pie_chart_data(df["answer_letter"], title="Answer letter distribution"))
    for chart in (
        _list_length_chart(df, "choices", "Choice count distribution", "Choices"),
        _list_length_chart(df, "public_test_cases", "Public test count distribution", "Tests"),
        _text_length_chart(df),
        _timeline_chart(df),
    ):
        if chart is not None:
            charts.append(chart)

    return {"metrics": metrics, "charts": charts, "tables": []}
