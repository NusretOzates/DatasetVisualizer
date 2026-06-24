"""Dataset API service backing the Gradio server and React frontend."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from dataset_visualizer.api.dataset_registry import DatasetDescriptor, get_descriptor
from dataset_visualizer.api.filters import apply_filters, build_filter_options
from dataset_visualizer.api.serializers import serialize_row, serialize_value
from dataset_visualizer.config import DatasetEntry, get_dataset_by_id, load_config
from dataset_visualizer.loaders.livecodebench import decode_private_test_cases
from dataset_visualizer.row_count import row_count
from dataset_visualizer.source_links import resolve_source_link, source_link_payload


@dataclass
class DatasetContext:
    """Loaded dataset state for a single request."""

    df: pd.DataFrame
    extras: dict[str, Any] = field(default_factory=dict)


def _hf_source(entry: DatasetEntry) -> str:
    link = resolve_source_link(entry)
    if link is not None:
        return link.label
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
            count_label = row_count(entry)
            entries.append(
                {
                    "id": entry.id,
                    "label": entry.label,
                    "icon": entry.icon,
                    "archetype": entry.archetype,
                    "description": entry.description,
                    "hf_source": _hf_source(entry),
                    "source_link": source_link_payload(entry),
                    "row_count": count_label,
                }
            )
            home_rows.append(
                {
                    "category": label,
                    "dataset": entry.label,
                    "hf_source": _hf_source(entry),
                    "source_link": source_link_payload(entry),
                    "archetype": entry.archetype or "—",
                    "rows": count_label,
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
        "source_link": source_link_payload(entry),
        "controls": descriptor.controls(),
        "filters": descriptor.filters,
    }


def get_filter_options(dataset_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return column names and available filter option values for the loaded dataset."""
    context = _load_context(dataset_id, params or {})
    return {
        "columns": [str(column) for column in context.df.columns],
        "options": build_filter_options(context.df, get_descriptor(dataset_id).filters),
    }


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

    position = int(matches.index[0])
    row = filtered.iloc[position]
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
    try:
        df, extras = descriptor.loader(params)
    except Exception as exc:
        msg = _loader_error_message(dataset_id, exc)
        raise ValueError(msg) from exc
    return DatasetContext(df=df, extras=extras)


def _loader_error_message(dataset_id: str, exc: Exception) -> str:
    """Turn loader failures into actionable API errors for the UI."""
    detail = str(exc).strip()
    lowered = detail.lower()
    if "gated" in lowered or "authenticated" in lowered:
        entry = get_dataset_by_id(load_config(), dataset_id)
        hf_id = entry.hf_id if entry and entry.hf_id else "the Hugging Face dataset"
        return (
            f"Cannot load {dataset_id}: access to {hf_id} is gated on Hugging Face. "
            "Accept the dataset terms on the Hub and set HF_TOKEN in your environment."
        )
    if detail:
        return f"Failed to load dataset {dataset_id}: {detail}"
    return f"Failed to load dataset {dataset_id}"


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
