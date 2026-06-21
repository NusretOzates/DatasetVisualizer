"""AIME 2026 dataset exploration page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dataset_visualizer.components.charts import histogram
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.aime_2026 import load_aime_2026
from dataset_visualizer.row_values import has_display_value

SOLUTION_COLUMNS = ("solution", "working", "work", "explanation", "rationale")


@st.cache_data(show_spinner=False)
def _load_data() -> pd.DataFrame:
    return load_aime_2026()


def _solution_text(row: pd.Series) -> str | None:
    """Return the first present solution-style field, if any."""
    for field in SOLUTION_COLUMNS:
        if field in row.index and has_display_value(row[field]):
            return str(row[field])
    return None


def _render_overview(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)
    col1.metric("Problems", f"{len(df):,}")
    col2.metric("Split", "train")

    overview = df.copy()
    overview["problem_preview"] = overview["problem"].astype(str).str.slice(0, 120)
    st.subheader("All problems")
    st.dataframe(
        overview[["problem_idx", "problem_preview"]],
        width="stretch",
        hide_index=True,
    )

    if "answer" in df.columns and len(df):
        histogram(df["answer"], "Gold answer distribution")


def _render_sample(row: pd.Series) -> None:
    problem_idx = str(row.get("problem_idx", ""))
    reveal_key = f"aime_2026_reveal_{problem_idx}"

    st.caption(f"**Problem:** {problem_idx}")

    st.subheader("Problem")
    st.markdown(str(row.get("problem", "")))

    if st.button("Reveal gold answer", key=reveal_key):
        st.session_state[reveal_key] = True
    if st.session_state.get(reveal_key):
        st.success(str(row.get("answer", "")))

    solution = _solution_text(row)
    if solution is not None:
        with st.expander("Solution / working"):
            st.markdown(solution)


df = _load_data()

render_dataset_page(
    title="AIME 2026",
    df=df,
    id_column="problem_idx",
    render_overview=_render_overview,
    render_sample=_render_sample,
    key_prefix="aime_2026",
)
