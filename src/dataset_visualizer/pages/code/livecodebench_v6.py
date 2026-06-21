"""LiveCodeBench v6 dataset exploration page."""

from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from dataset_visualizer.components.charts import timeline
from dataset_visualizer.components.code_problem_viewer import render_code_problem, render_test_cases
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.livecodebench import decode_private_test_cases, load_livecodebench

PRIVATE_TEST_PREVIEW_LIMIT = 20


@st.cache_data(show_spinner=False)
def _load_data() -> pd.DataFrame:
    return load_livecodebench()


def _stacked_difficulty_platform(df: pd.DataFrame) -> None:
    """Render a stacked bar chart of difficulty counts per platform."""
    if df.empty:
        st.info("No data for difficulty × platform chart.")
        return
    counts = df.groupby(["difficulty", "platform"], observed=True).size().reset_index(name="count")
    fig = px.bar(
        counts,
        x="difficulty",
        y="count",
        color="platform",
        barmode="stack",
        title="Problems by difficulty and platform",
        labels={"difficulty": "Difficulty", "count": "Count", "platform": "Platform"},
    )
    st.plotly_chart(fig, width="stretch")


def _render_overview(df: pd.DataFrame) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total problems", f"{len(df):,}")
    col2.metric("Platforms", df["platform"].nunique() if len(df) else 0)
    median_tests = df["public_test_count"].median() if len(df) else 0
    col3.metric("Median public tests", f"{median_tests:.0f}" if len(df) else "—")

    _stacked_difficulty_platform(df)
    if "contest_date" in df.columns and len(df):
        timeline(df["contest_date"], "Contest date distribution")


def _render_private_tests(raw: str) -> None:
    """Decode and preview private test cases on demand."""
    with st.expander("Private test cases"):
        if not raw or not str(raw).strip():
            st.info("No private test cases for this problem.")
            return
        try:
            cases = decode_private_test_cases(str(raw))
        except (json.JSONDecodeError, ValueError, OSError, TypeError) as exc:
            st.error(f"Failed to decode private tests: {exc}")
            return

        render_test_cases(cases, title="Private test cases", limit=PRIVATE_TEST_PREVIEW_LIMIT)


def _render_sample(row: pd.Series) -> None:
    render_code_problem(row)
    _render_private_tests(str(row.get("private_test_cases", "")))
    with st.expander("Raw JSON"):
        payload = row.to_dict()
        st.json(payload)


def _sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    platforms = sorted(filtered["platform"].dropna().unique())
    difficulties = sorted(filtered["difficulty"].dropna().unique())

    with st.sidebar:
        st.subheader("Filters")
        selected_platforms = st.multiselect(
            "Platform",
            platforms,
            default=platforms,
            key="lcb_platforms",
        )
        selected_difficulties = st.multiselect(
            "Difficulty",
            difficulties,
            default=difficulties,
            key="lcb_difficulties",
        )

        min_date = filtered["contest_date"].min()
        max_date = filtered["contest_date"].max()
        if pd.notna(min_date) and pd.notna(max_date):
            start, end = st.slider(
                "Contest date range",
                min_value=min_date.date(),
                max_value=max_date.date(),
                value=(min_date.date(), max_date.date()),
                key="lcb_date_range",
            )
            filtered = filtered[
                (filtered["contest_date"].dt.date >= start)
                & (filtered["contest_date"].dt.date <= end)
            ]

    if selected_platforms and len(selected_platforms) < len(platforms):
        filtered = filtered[filtered["platform"].isin(selected_platforms)]
    if selected_difficulties and len(selected_difficulties) < len(difficulties):
        filtered = filtered[filtered["difficulty"].isin(selected_difficulties)]

    return filtered.reset_index(drop=True)


df = _load_data()

render_dataset_page(
    title="LiveCodeBench v6",
    df=df,
    id_column="question_id",
    render_overview=_render_overview,
    render_sample=_render_sample,
    dataset_id="livecodebench_v6",
    sidebar_filters=_sidebar_filters,
    key_prefix="lcb",
)
