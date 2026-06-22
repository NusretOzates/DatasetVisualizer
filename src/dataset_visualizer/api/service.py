"""Dataset API service backing the Gradio server and React frontend."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from dataset_visualizer.api.dataset_registry import DatasetDescriptor, get_descriptor
from dataset_visualizer.api.filters import apply_filters
from dataset_visualizer.api.serializers import serialize_row, serialize_value
from dataset_visualizer.config import DatasetEntry, get_dataset_by_id, load_config
from dataset_visualizer.loaders.livecodebench import decode_private_test_cases
from dataset_visualizer.row_count import row_count


@dataclass
class DatasetContext:
    """Loaded dataset state for a single request."""

    df: pd.DataFrame
    extras: dict[str, Any] = field(default_factory=dict)


def _hf_source(entry: DatasetEntry) -> str:
    for attr in ("hf_id", "hf_repo", "problems_hf_id"):
        value = getattr(entry, attr, None)
        if value:
            return str(value)
    return "—"


def get_catalog() -> dict[str, Any]:
    """Return navigation metadata and home-page rows."""
    config = load_config()
    categories: list[dict[str, Any]] = []
    home_rows: list[dict[str, str]] = []

    for category_key, datasets in config.categories.items():
        label = category_key.replace("_", " ").title()
        entries = []
        for entry in datasets:
            entries.append(
                {
                    "id": entry.id,
                    "label": entry.label,
                    "icon": entry.icon,
                    "archetype": entry.archetype,
                    "description": entry.description,
                    "hf_source": _hf_source(entry),
                    "row_count": row_count(entry),
                }
            )
            home_rows.append(
                {
                    "category": label,
                    "dataset": entry.label,
                    "hf_source": _hf_source(entry),
                    "archetype": entry.archetype or "—",
                    "rows": row_count(entry),
                }
            )
        categories.append({"key": category_key, "label": label, "datasets": entries})

    return {"categories": categories, "home_rows": home_rows}


def get_dataset_meta(dataset_id: str) -> dict[str, Any]:
    """Return dataset metadata and control definitions."""
    entry = _require_entry(dataset_id)
    descriptor = get_descriptor(dataset_id)
    return {
        "id": entry.id,
        "label": entry.label,
        "description": entry.description,
        "archetype": entry.archetype,
        "icon": entry.icon,
        "viewer": descriptor.viewer,
        "supports_private_tests": descriptor.supports_private_tests,
        "id_column": descriptor.id_column,
        "controls": descriptor.controls(),
        "filters": descriptor.filters,
    }


def get_filter_options(dataset_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return available filter option values for the loaded dataset."""
    context = _load_context(dataset_id, params or {})
    return _filter_options_from_df(context.df, get_descriptor(dataset_id).filters)


def get_overview(
    dataset_id: str,
    params: dict[str, Any] | None = None,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return overview metrics, tables, and chart payloads."""
    descriptor = get_descriptor(dataset_id)
    context = _load_context(dataset_id, params or {})
    filtered = apply_filters(context.df, descriptor.filters, filters or {})
    return descriptor.overview(filtered, context.extras)


def get_sample(
    dataset_id: str,
    index: int,
    params: dict[str, Any] | None = None,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a single sample row and any dataset-specific extras."""
    descriptor = get_descriptor(dataset_id)
    context = _load_context(dataset_id, params or {})
    filtered = apply_filters(context.df, descriptor.filters, filters or {})
    if filtered.empty:
        return {"total": 0, "index": 0, "row": None, "extras": {}}
    bounded_index = max(0, min(index, len(filtered) - 1))
    row = filtered.iloc[bounded_index]
    return {
        "total": len(filtered),
        "index": bounded_index,
        "row": serialize_row(row),
        "extras": _sample_extras(descriptor, row, context.extras),
    }


def find_sample(
    dataset_id: str,
    id_value: str,
    params: dict[str, Any] | None = None,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Find a sample by its id column value."""
    descriptor = get_descriptor(dataset_id)
    context = _load_context(dataset_id, params or {})
    filtered = apply_filters(context.df, descriptor.filters, filters or {})
    id_column = descriptor.id_column
    if id_column not in filtered.columns:
        return {"total": len(filtered), "index": -1, "row": None, "extras": {}}

    matches = filtered[filtered[id_column].astype(str) == str(id_value)]
    if matches.empty:
        return {"total": len(filtered), "index": -1, "row": None, "extras": {}}

    index = int(matches.index[0])
    position = int(filtered.index.get_loc(index))
    row = filtered.loc[index]
    return {
        "total": len(filtered),
        "index": position,
        "row": serialize_row(row),
        "extras": _sample_extras(descriptor, row, context.extras),
    }


def decode_private_tests_api(raw: str) -> dict[str, Any]:
    """Decode LiveCodeBench private test cases for the sample inspector."""
    if not raw or not str(raw).strip():
        return {"cases": []}
    cases = decode_private_test_cases(str(raw))
    return {"cases": serialize_value(cases)}


def _require_entry(dataset_id: str) -> DatasetEntry:
    entry = get_dataset_by_id(load_config(), dataset_id)
    if entry is None:
        msg = f"Unknown dataset id: {dataset_id}"
        raise ValueError(msg)
    return entry


def _load_context(dataset_id: str, params: dict[str, Any]) -> DatasetContext:
    descriptor = get_descriptor(dataset_id)
    df, extras = descriptor.loader(params)
    return DatasetContext(df=df, extras=extras)


def _filter_options_from_df(df: pd.DataFrame, schema: list[dict[str, Any]]) -> dict[str, Any]:
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


def _sample_extras(
    descriptor: DatasetDescriptor,
    row: pd.Series,
    extras: dict[str, Any],
) -> dict[str, Any]:
    if descriptor.sample_extras is None:
        return {}
    return descriptor.sample_extras(row, extras)


def parse_json_param(raw: str | dict[str, Any] | None) -> dict[str, Any]:
    """Parse a JSON string parameter from Gradio API calls."""
    if raw is None or raw == "":
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        msg = f"Invalid JSON parameter: {exc}"
        raise ValueError(msg) from exc
