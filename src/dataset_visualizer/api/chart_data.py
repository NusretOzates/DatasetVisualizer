"""Chart data builders for the React frontend (Plotly-compatible payloads)."""

from __future__ import annotations

from typing import Any

import pandas as pd


def value_counts_chart(
    series: pd.Series,
    *,
    title: str,
    x_label: str = "",
    y_label: str = "Count",
    top_n: int | None = None,
) -> dict[str, Any]:
    """Build a bar chart payload from a value-count series."""
    counts = series.value_counts()
    if top_n is not None:
        counts = counts.head(top_n)
    categories = [str(cat) for cat in counts.index.tolist()]
    values = [int(v) for v in counts.tolist()]
    return {
        "type": "bar",
        "title": title,
        "x_label": x_label,
        "y_label": y_label,
        "categories": categories,
        "values": values,
    }


def pie_chart_data(series: pd.Series, *, title: str) -> dict[str, Any]:
    """Build a pie chart payload from a categorical series."""
    counts = series.value_counts()
    return {
        "type": "pie",
        "title": title,
        "labels": [str(label) for label in counts.index.tolist()],
        "values": [int(v) for v in counts.tolist()],
    }


def histogram_data(series: pd.Series, *, title: str, x_label: str = "") -> dict[str, Any]:
    """Build a histogram payload from a numeric series."""
    clean = series.dropna()
    if clean.empty:
        return {"type": "histogram", "title": title, "x_label": x_label, "values": []}
    return {
        "type": "histogram",
        "title": title,
        "x_label": x_label,
        "values": [serialize_number(value) for value in clean.tolist()],
    }


def stacked_bar_chart(
    df: pd.DataFrame,
    *,
    x_col: str,
    color_col: str,
    title: str,
    x_label: str = "",
    y_label: str = "Count",
) -> dict[str, Any]:
    """Build a stacked bar chart payload grouped by two categorical columns."""
    if df.empty:
        return {
            "type": "stacked_bar",
            "title": title,
            "x_label": x_label,
            "y_label": y_label,
            "categories": [],
            "series": [],
        }
    counts = df.groupby([x_col, color_col], observed=True).size().reset_index(name="count")
    categories = sorted({str(value) for value in counts[x_col].tolist()})
    color_values = sorted({str(value) for value in counts[color_col].tolist()})
    series = []
    for color_value in color_values:
        subset = counts[counts[color_col].astype(str) == color_value]
        value_map = {str(row[x_col]): int(row["count"]) for _, row in subset.iterrows()}
        series.append(
            {
                "name": color_value,
                "values": [value_map.get(category, 0) for category in categories],
            }
        )
    return {
        "type": "stacked_bar",
        "title": title,
        "x_label": x_label,
        "y_label": y_label,
        "categories": categories,
        "series": series,
    }


def timeline_data(dates: pd.Series, *, title: str) -> dict[str, Any]:
    """Build a timeline histogram payload from datetime values."""
    iso_dates = [value.isoformat() for value in dates.dropna().tolist()]
    return {"type": "timeline", "title": title, "values": iso_dates}


def scatter_chart_data(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
) -> dict[str, Any]:
    """Build a scatter chart payload from numeric columns."""
    points: list[dict[str, object]] = []
    for _, row in df.iterrows():
        point: dict[str, object] = {
            "x": serialize_number(row.get(x)),
            "y": serialize_number(row.get(y)),
        }
        if color is not None:
            point["color"] = serialize_number(row.get(color))
        points.append(point)
    return {
        "type": "scatter",
        "title": title,
        "x_label": x.replace("_", " ").title(),
        "y_label": y.replace("_", " ").title(),
        "color_label": color.replace("_", " ").title() if color else None,
        "points": points,
    }


def serialize_number(value: object) -> float | int | str | None:
    """Normalize numeric values for chart payloads."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value
    return str(value)
