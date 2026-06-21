"""SWE-Bench Verified dataset exploration page."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from dataset_visualizer.components.charts import bar_chart, pie_chart
from dataset_visualizer.components.issue_viewer import render_issue
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.swe_bench import load_swe_bench_verified


@st.cache_data(show_spinner=False)
def _load_data() -> pd.DataFrame:
    return load_swe_bench_verified()


def _render_overview(df: pd.DataFrame) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total issues", f"{len(df):,}")
    col2.metric("Repositories", df["repo"].nunique() if len(df) else 0)
    median_fail = df["fail_to_pass_count"].median() if len(df) else 0
    col3.metric("Median FAIL_TO_PASS", f"{median_fail:.0f}" if len(df) else "—")

    bar_chart(df["repo"], "Issues per repository", x_label="Repository")
    if "difficulty" in df.columns and df["difficulty"].notna().any():
        pie_chart(df["difficulty"], "Difficulty distribution")


def _render_sample(row: pd.Series) -> None:
    render_issue(row)
    with st.expander("Raw JSON"):
        st.json(json.loads(row.to_json()))


def _sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    repos = sorted(df["repo"].dropna().unique())
    with st.sidebar:
        st.subheader("Filters")
        selected_repos = st.multiselect(
            "Repository",
            repos,
            default=repos,
            key="swe_verified_repos",
        )
        if "difficulty" in df.columns:
            difficulties = sorted(df["difficulty"].dropna().unique())
            if difficulties:
                selected_diff = st.multiselect(
                    "Difficulty",
                    difficulties,
                    default=difficulties,
                    key="swe_verified_difficulty",
                )
            else:
                selected_diff = []
        else:
            selected_diff = []

    filtered = df.copy()
    if selected_repos and len(selected_repos) < len(repos):
        filtered = filtered[filtered["repo"].isin(selected_repos)]
    if selected_diff and "difficulty" in filtered.columns:
        filtered = filtered[filtered["difficulty"].isin(selected_diff)]

    return filtered.reset_index(drop=True)


df = _load_data()

render_dataset_page(
    title="SWE-Bench Verified",
    df=df,
    id_column="instance_id",
    render_overview=_render_overview,
    render_sample=_render_sample,
    sidebar_filters=_sidebar_filters,
    key_prefix="swe_verified",
)
