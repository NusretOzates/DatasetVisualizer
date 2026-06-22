"""Helpers for resolving and formatting dataset row counts on the home page."""

from __future__ import annotations

from dataset_visualizer.config import DatasetEntry
from dataset_visualizer.registry import load_dataset_frame


def format_row_count(count: int, entry: DatasetEntry) -> str:
    """Format a row count for the home page table."""
    formatted = f"{count:,}"
    if entry.archetype == "math_competition" or entry.id == "arxivmath_0526":
        return f"{formatted} problems"
    return formatted


def row_count(entry: DatasetEntry) -> str:
    """Return row count from loader, falling back to config when loading fails."""
    loader_name = entry.loader
    try:
        df = load_dataset_frame(loader_name)
        if df is not None:
            return format_row_count(len(df), entry)
    except Exception:
        if entry.row_count is not None:
            return format_row_count(entry.row_count, entry)
        return "error"
    if entry.row_count is not None:
        return format_row_count(entry.row_count, entry)
    return "—"
