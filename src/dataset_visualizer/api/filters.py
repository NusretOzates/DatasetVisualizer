"""Schema-driven dataset filtering for API handlers."""

from __future__ import annotations

from typing import Any

import pandas as pd


def apply_filters(
    df: pd.DataFrame,
    schema: list[dict[str, Any]],
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

        elif ftype == "radio" and name == "modality":
            modality = filters.get(name, "All")
            if modality == "Text only" and "has_image" in filtered.columns:
                filtered = filtered[~filtered["has_image"]]
            elif modality == "Multimodal" and "has_image" in filtered.columns:
                filtered = filtered[filtered["has_image"]]

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
