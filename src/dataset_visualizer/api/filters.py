"""Schema-driven dataset filtering and filter-option discovery."""

from __future__ import annotations

from typing import Any

import pandas as pd

from dataset_visualizer.api.serializers import serialize_value

FilterSchema = list[dict[str, Any]]


def build_filter_options(df: pd.DataFrame, schema: FilterSchema) -> dict[str, Any]:
    """Return UI option payloads for each filter in a dataset schema."""
    options: dict[str, Any] = {}
    for spec in schema:
        name = spec["name"]
        ftype = spec["type"]
        column = spec.get("column")

        if ftype == "multiselect" and column and column in df.columns:
            values = sorted(df[column].dropna().unique(), key=lambda v: str(v))
            options[name] = [serialize_value(value) for value in values]
        elif ftype == "radio":
            options[name] = spec.get("options", [])
        elif ftype == "date_range" and column and column in df.columns:
            min_date = df[column].min()
            max_date = df[column].max()
            if pd.notna(min_date) and pd.notna(max_date):
                options[name] = {
                    "min": min_date.date().isoformat(),
                    "max": max_date.date().isoformat(),
                }
    return options


def apply_filters(
    df: pd.DataFrame,
    schema: FilterSchema,
    filters: dict[str, Any],
) -> pd.DataFrame:
    """Apply filter controls described by a dataset filter schema."""
    if not filters:
        return df.reset_index(drop=True)

    filtered = df
    for spec in schema:
        name = spec["name"]
        ftype = spec["type"]
        column = spec.get("column")

        if ftype == "multiselect" and column and column in filtered.columns:
            selected = filters.get(name)
            if not selected:
                continue
            all_values = sorted(filtered[column].dropna().unique(), key=lambda v: str(v))
            if len(selected) < len(all_values):
                filtered = filtered[
                    filtered[column].astype(str).isin([str(value) for value in selected])
                ]

        elif ftype == "text" and column and column in filtered.columns:
            prefix = str(filters.get(name, "")).strip()
            if prefix:
                filtered = filtered[
                    filtered[column].astype(str).str.startswith(prefix, na=False)
                ]

        elif ftype == "radio" and column and column in filtered.columns:
            selected = filters.get(name, spec.get("default", "All"))
            value_map = spec.get("value_map")
            if value_map and selected in value_map:
                target = value_map[selected]
                filtered = filtered[filtered[column] == target]

        elif ftype == "date_range" and column and column in filtered.columns:
            date_range = filters.get(name)
            if not date_range:
                continue
            start = date_range.get("start")
            end = date_range.get("end")
            if start and end:
                filtered = filtered[
                    (filtered[column].dt.date >= pd.to_datetime(start).date())
                    & (filtered[column].dt.date <= pd.to_datetime(end).date())
                ]

    return filtered.reset_index(drop=True)
