"""Home page listing registered datasets."""

from __future__ import annotations

import streamlit as st

from dataset_visualizer.config import load_config
from dataset_visualizer.registry import LOADER_REGISTRY, load_dataset_frame


def _hf_source(entry: object) -> str:
    """Return the primary Hugging Face identifier for display."""
    for attr in ("hf_id", "hf_repo", "problems_hf_id"):
        value = getattr(entry, attr, None)
        if value:
            return str(value)
    return "—"


def _row_count(loader_name: str) -> str:
    """Return row count from loader if registered, otherwise a placeholder."""
    if loader_name not in LOADER_REGISTRY:
        return "—"
    try:
        df = load_dataset_frame(loader_name)
        if df is not None:
            return f"{len(df):,}"
    except Exception:
        return "error"
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
                "Rows": _row_count(entry.loader),
            }
        )

st.dataframe(rows, use_container_width=True, hide_index=True)
