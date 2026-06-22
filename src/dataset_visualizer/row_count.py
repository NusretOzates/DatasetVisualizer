"""Helpers for resolving and formatting dataset row counts on the home page."""

from __future__ import annotations

from dataset_visualizer.api.dataset_registry import get_descriptor
from dataset_visualizer.config import DatasetEntry


def format_row_count(count: int, entry: DatasetEntry) -> str:
    """Format a row count for the home page table."""
    formatted = f"{count:,}"
    if entry.archetype == "math_competition":
        return f"{formatted} problems"
    return formatted


def row_count(entry: DatasetEntry) -> str:
    """Return row count from config when set, otherwise from the dataset loader."""
    if entry.row_count is not None:
        return format_row_count(entry.row_count, entry)
    try:
        descriptor = get_descriptor(entry.id)
        df, _extras = descriptor.loader({})
        return format_row_count(len(df), entry)
    except Exception:
        return "error"
