"""Home page listing registered datasets."""

from __future__ import annotations

import streamlit as st

from dataset_visualizer.config import DatasetEntry, load_config
from dataset_visualizer.registry import LOADER_REGISTRY, load_dataset_frame


def _hf_source(entry: object) -> str:
    """Return the primary Hugging Face identifier for display."""
    for attr in ("hf_id", "hf_repo", "problems_hf_id"):
        value = getattr(entry, attr, None)
        if value:
            return str(value)
    return "—"


def _format_row_count(count: int, loader_name: str) -> str:
    """Format a row count for the home page table."""
    formatted = f"{count:,}"
    if loader_name == "arxivmath":
        return f"{formatted} problems"
    return formatted


def _row_count(entry: DatasetEntry) -> str:
    """Return row count from loader, falling back to config when loading fails."""
    loader_name = entry.loader
    if loader_name in LOADER_REGISTRY:
        try:
            df = load_dataset_frame(loader_name)
            if df is not None:
                return _format_row_count(len(df), loader_name)
        except Exception:
            if entry.row_count is not None:
                return _format_row_count(entry.row_count, loader_name)
            return "error"
    if entry.row_count is not None:
        return _format_row_count(entry.row_count, loader_name)
    return "—"


st.title("Dataset Visualizer")
st.markdown(
    "Explore Hugging Face benchmark datasets with interactive overviews and per-sample inspection."
)

config = load_config()
rows: list[dict[str, str]] = []

for category, datasets in config.categories.items():
    for entry in datasets:
        rows.append(
            {
                "Category": category.replace("_", " ").title(),
                "Dataset": entry.label,
                "HF Source": _hf_source(entry),
                "Archetype": entry.archetype or "—",
                "Rows": _row_count(entry),
            }
        )

st.dataframe(rows, width="stretch", hide_index=True)
