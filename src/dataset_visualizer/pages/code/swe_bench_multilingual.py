"""SWE-Bench Multilingual dataset exploration page."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from dataset_visualizer.components.charts import bar_chart
from dataset_visualizer.components.issue_viewer import render_issue
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.swe_bench import load_swe_bench_multilingual


@st.cache_data(show_spinner=False)
def _load_data() -> pd.DataFrame:
    return load_swe_bench_multilingual()


def _repo_language(df: pd.DataFrame) -> pd.Series:
    """Infer repository language from owner/repo naming patterns."""
    if "repo_language" in df.columns:
        return df["repo_language"].fillna("unknown")
    return df["repo"].astype(str).str.split("/").str[0]


def _render_overview(df: pd.DataFrame) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total issues", f"{len(df):,}")
    col2.metric("Repositories", df["repo"].nunique() if len(df) else 0)
    median_fail = df["fail_to_pass_count"].median() if len(df) else 0
    col3.metric("Median FAIL_TO_PASS", f"{median_fail:.0f}" if len(df) else "—")

    bar_chart(df["repo"], "Issues per repository", x_label="Repository")
    languages = _repo_language(df)
    if languages.nunique() > 1:
        bar_chart(languages, "Issues by repo prefix", x_label="Prefix")


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
            key="swe_ml_repos",
        )

    filtered = df.copy()
    if selected_repos and len(selected_repos) < len(repos):
        filtered = filtered[filtered["repo"].isin(selected_repos)]

    return filtered.reset_index(drop=True)


df = _load_data()

render_dataset_page(
    title="SWE-Bench Multilingual",
    df=df,
    id_column="instance_id",
    render_overview=_render_overview,
    render_sample=_render_sample,
    dataset_id="swe_bench_multilingual",
    sidebar_filters=_sidebar_filters,
    key_prefix="swe_ml",
)
