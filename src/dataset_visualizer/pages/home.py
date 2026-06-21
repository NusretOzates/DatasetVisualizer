"""Home page listing registered datasets."""

from __future__ import annotations

import streamlit as st

from dataset_visualizer.config import load_config
from dataset_visualizer.row_count import row_count


def _hf_source(entry: object) -> str:
    """Return the primary Hugging Face identifier for display."""
    for attr in ("hf_id", "hf_repo", "problems_hf_id"):
        value = getattr(entry, attr, None)
        if value:
            return str(value)
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
                "Rows": row_count(entry),
            }
        )

st.dataframe(rows, width="stretch", hide_index=True)
