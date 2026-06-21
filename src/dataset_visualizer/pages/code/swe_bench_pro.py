"""SWE-Bench PRO dataset exploration page."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from dataset_visualizer.components.charts import bar_chart, pie_chart
from dataset_visualizer.components.issue_viewer import render_issue
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.swe_bench import load_swe_bench_pro


@st.cache_data(show_spinner=False)
def _load_data() -> pd.DataFrame:
    return load_swe_bench_pro()


def _render_overview(df: pd.DataFrame) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total issues", f"{len(df):,}")
    col2.metric("Repositories", df["repo"].nunique() if len(df) else 0)
    col3.metric("Languages", df["repo_language"].nunique() if "repo_language" in df.columns else 0)

    if "repo_language" in df.columns:
        bar_chart(df["repo_language"], "Issues by language", x_label="Language")
    bar_chart(df["repo"], "Issues per repository", x_label="Repository")
    if "issue_specificity" in df.columns and df["issue_specificity"].notna().any():
        pie_chart(df["issue_specificity"], "Issue specificity")


def _render_sample(row: pd.Series) -> None:
    render_issue(row)
    with st.expander("Raw JSON"):
        st.json(json.loads(row.to_json()))


def _sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    repos = sorted(filtered["repo"].dropna().unique())

    with st.sidebar:
        st.subheader("Filters")
        selected_repos = st.multiselect(
            "Repository",
            repos,
            default=repos,
            key="swe_pro_repos",
        )
        if "repo_language" in filtered.columns:
            languages = sorted(filtered["repo_language"].dropna().unique())
            selected_langs = st.multiselect(
                "Language",
                languages,
                default=languages,
                key="swe_pro_langs",
            )
        else:
            selected_langs = []

    if selected_repos and len(selected_repos) < len(repos):
        filtered = filtered[filtered["repo"].isin(selected_repos)]
    if selected_langs and "repo_language" in filtered.columns:
        filtered = filtered[filtered["repo_language"].isin(selected_langs)]

    return filtered.reset_index(drop=True)


df = _load_data()

render_dataset_page(
    title="SWE-Bench PRO",
    df=df,
    id_column="instance_id",
    render_overview=_render_overview,
    render_sample=_render_sample,
    sidebar_filters=_sidebar_filters,
    key_prefix="swe_pro",
)
