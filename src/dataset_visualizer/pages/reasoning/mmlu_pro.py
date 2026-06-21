"""MMLU-Pro dataset exploration page."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from dataset_visualizer.components.charts import bar_chart, histogram
from dataset_visualizer.components.mcq_viewer import render_mcq
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.mmlu_pro import load_mmlu_pro

SPLIT_OPTIONS = ("test", "validation")


@st.cache_data(show_spinner=False)
def _load_split(split: str) -> pd.DataFrame:
    return load_mmlu_pro(split=split)


def _render_overview(df: pd.DataFrame) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total rows", f"{len(df):,}")
    col2.metric("Categories", df["category"].nunique())
    split_name = df["split"].iloc[0] if "split" in df.columns and len(df) else "—"
    col3.metric("Split", split_name)

    bar_chart(df["category"], "Rows per category", x_label="Category")
    histogram(df["option_count"], "Option count distribution", x_label="Options per question")

    src_counts = df["src"].value_counts().head(20).reset_index()
    src_counts.columns = ["src", "count"]
    st.subheader("Top source provenance")
    st.dataframe(src_counts, width="stretch", hide_index=True)


def _render_sample(row: pd.Series) -> None:
    st.caption(
        f"**ID:** {row.get('question_id', '—')} · "
        f"**Category:** {row.get('category', '—')} · "
        f"**Source:** {row.get('src', '—')} · "
        f"**Split:** {row.get('split', '—')}"
    )
    render_mcq(
        row,
        question_col="question",
        choices_col="options",
        answer_col="answer",
    )
    cot = row.get("cot_content")
    if cot and pd.notna(cot) and str(cot).strip():
        with st.expander("Chain-of-thought"):
            st.text_area(
                "Chain-of-thought",
                value=str(cot),
                height=300,
                disabled=True,
                label_visibility="collapsed",
            )
    with st.expander("Raw JSON"):
        st.json(json.loads(row.to_json()))


def _sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    categories = sorted(df["category"].unique())
    with st.sidebar:
        st.subheader("Filters")
        selected_categories = st.multiselect(
            "Category",
            categories,
            default=categories,
            key="mmlu_pro_categories",
        )
        src_prefix = st.text_input("Source prefix", value="", key="mmlu_pro_src_prefix")

    filtered = df
    if selected_categories and len(selected_categories) < len(categories):
        filtered = filtered[filtered["category"].isin(selected_categories)]
    if src_prefix.strip():
        prefix = src_prefix.strip()
        filtered = filtered[filtered["src"].astype(str).str.startswith(prefix, na=False)]
    return filtered.reset_index(drop=True)


with st.sidebar:
    split = st.selectbox("Split", SPLIT_OPTIONS, index=0, key="mmlu_pro_split")

df = _load_split(split)

render_dataset_page(
    title="MMLU-Pro",
    df=df,
    id_column="question_id",
    render_overview=_render_overview,
    render_sample=_render_sample,
    sidebar_filters=_sidebar_filters,
    key_prefix="mmlu_pro",
)
