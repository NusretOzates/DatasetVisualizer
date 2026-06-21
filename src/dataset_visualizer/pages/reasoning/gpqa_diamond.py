"""GPQA Diamond dataset exploration page."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from dataset_visualizer.components.charts import pie_chart
from dataset_visualizer.components.mcq_viewer import render_mcq
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.gpqa import load_gpqa_diamond


@st.cache_data(show_spinner=False)
def _load_data() -> pd.DataFrame:
    return load_gpqa_diamond()


def _render_overview(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)
    col1.metric("Total questions", f"{len(df):,}")
    col2.metric("Split", df["split"].iloc[0] if len(df) else "—")
    pie_chart(df["answer_letter"], "Answer letter distribution")


def _render_sample(row: pd.Series) -> None:
    st.caption(f"Split: **{row.get('split', '—')}**")
    render_mcq(row)
    with st.expander("Raw JSON"):
        st.json(json.loads(row.to_json()))


df = _load_data()

render_dataset_page(
    title="GPQA Diamond",
    df=df,
    id_column="question",
    render_overview=_render_overview,
    render_sample=_render_sample,
    key_prefix="gpqa",
)
