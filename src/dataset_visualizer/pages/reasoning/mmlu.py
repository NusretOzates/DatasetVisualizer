"""MMLU dataset exploration page."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from dataset_visualizer.components.charts import bar_chart, pie_chart
from dataset_visualizer.components.mcq_viewer import render_mcq
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.mmlu import load_mmlu

SPLIT_OPTIONS = ("test", "validation", "dev")


@st.cache_data(show_spinner=False)
def _load_split(split: str) -> pd.DataFrame:
    return load_mmlu(split=split)


def _render_overview(df: pd.DataFrame) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total rows", f"{len(df):,}")
    col2.metric("Subjects", df["subject"].nunique())
    split_name = df["split"].iloc[0] if "split" in df.columns and len(df) else "—"
    col3.metric("Split", split_name)

    bar_chart(df["subject"], "Rows per subject", x_label="Subject")
    pie_chart(df["answer_letter"], "Answer letter distribution")


def _render_sample(row: pd.Series) -> None:
    st.caption(f"Subject: **{row.get('subject', '—')}** · Split: **{row.get('split', '—')}**")
    render_mcq(row)
    with st.expander("Raw JSON"):
        st.json(json.loads(row.to_json()))


def _sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    subjects = sorted(df["subject"].unique())
    with st.sidebar:
        st.subheader("Filters")
        selected = st.multiselect("Subject", subjects, default=subjects, key="mmlu_subjects")

    if selected and len(selected) < len(subjects):
        return df[df["subject"].isin(selected)].reset_index(drop=True)
    return df.reset_index(drop=True)


with st.sidebar:
    split = st.selectbox("Split", SPLIT_OPTIONS, index=0, key="mmlu_split")

df = _load_split(split)

render_dataset_page(
    title="MMLU",
    df=df,
    id_column="subject",
    render_overview=_render_overview,
    render_sample=_render_sample,
    sidebar_filters=_sidebar_filters,
    key_prefix="mmlu",
)
