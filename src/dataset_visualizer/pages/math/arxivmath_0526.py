"""ArXiv Math 0526 dataset exploration page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from dataset_visualizer.components.charts import scatter_chart
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.arxivmath import load_outputs, load_problems

RUN_TABLE_COLUMNS = [
    "model_name",
    "idx_answer",
    "correct",
    "parsed_answer",
    "gold_answer",
    "input_tokens",
    "output_tokens",
    "cost",
]


@st.cache_data(show_spinner=False)
def _load_problems() -> pd.DataFrame:
    return load_problems()


@st.cache_data(show_spinner=False)
def _load_outputs() -> pd.DataFrame:
    return load_outputs()


def _author_count(authors: object) -> int:
    """Count authors from a comma-separated author string."""
    if authors is None or (isinstance(authors, float) and pd.isna(authors)):
        return 0
    return len([part for part in str(authors).split(",") if part.strip()])


def _outputs_for_problems(outputs: pd.DataFrame, problems: pd.DataFrame) -> pd.DataFrame:
    """Restrict outputs to the problem indices present in the filtered problems frame."""
    problem_ids = set(problems["problem_idx"].astype(str))
    return outputs[outputs["problem_idx"].isin(problem_ids)]


def _render_overview(problems: pd.DataFrame, outputs: pd.DataFrame) -> None:
    """Render dataset-level metrics and charts."""
    scoped_outputs = _outputs_for_problems(outputs, problems)

    col1, col2, col3 = st.columns(3)
    col1.metric("Problems", f"{len(problems):,}")
    col2.metric("Model runs", f"{len(scoped_outputs):,}")
    col3.metric("Models", scoped_outputs["model_name"].nunique() if len(scoped_outputs) else 0)

    overview = problems.copy()
    overview["author_count"] = overview["authors"].map(_author_count)
    st.subheader("All problems")
    st.dataframe(
        overview[["problem_idx", "title", "source", "author_count"]],
        width="stretch",
        hide_index=True,
    )

    if scoped_outputs.empty:
        st.info("No model outputs available for the selected problems.")
        return

    accuracy = (
        scoped_outputs.groupby("model_name", as_index=False)["correct"]
        .mean()
        .rename(columns={"correct": "accuracy"})
        .sort_values("accuracy", ascending=False)
    )
    accuracy_fig = px.bar(
        accuracy,
        x="model_name",
        y="accuracy",
        title="Model accuracy (mean correct rate)",
        labels={"model_name": "Model", "accuracy": "Accuracy"},
    )
    accuracy_fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(accuracy_fig, width="stretch")

    scatter_chart(
        scoped_outputs,
        x="input_tokens",
        y="output_tokens",
        color="correct",
        title="Token usage by attempt",
    )


def _render_model_runs(problem_idx: str, outputs: pd.DataFrame) -> None:
    """Render model-run table and per-attempt inspection for one problem."""
    problem_runs = outputs[outputs["problem_idx"] == problem_idx].copy()
    if problem_runs.empty:
        st.info("No model runs for this problem.")
        return

    models = sorted(problem_runs["model_name"].unique())
    model_filter = st.multiselect(
        "Filter by model",
        models,
        default=models,
        key=f"arxivmath_models_{problem_idx}",
    )

    if model_filter and len(model_filter) < len(models):
        problem_runs = problem_runs[problem_runs["model_name"].isin(model_filter)]

    st.subheader("Model runs")
    display_cols = [col for col in RUN_TABLE_COLUMNS if col in problem_runs.columns]
    sorted_runs = (
        problem_runs[display_cols].sort_values(["model_name", "idx_answer"]).reset_index(drop=True)
    )
    st.dataframe(sorted_runs, width="stretch", hide_index=True)

    if sorted_runs.empty:
        return

    attempt_labels = [
        f"{row['model_name']} · attempt {row['idx_answer']}" for _, row in sorted_runs.iterrows()
    ]
    selected_idx = st.selectbox(
        "Inspect attempt",
        range(len(attempt_labels)),
        format_func=lambda idx: attempt_labels[idx],
        key=f"arxivmath_attempt_{problem_idx}",
    )
    selected_row = sorted_runs.iloc[selected_idx]

    parsed_col, gold_col = st.columns(2)
    with parsed_col:
        st.markdown("**Parsed answer**")
        st.code(str(selected_row.get("parsed_answer", "")))
    with gold_col:
        st.markdown("**Gold answer**")
        st.code(str(selected_row.get("gold_answer", "")))

    full_run = problem_runs[
        (problem_runs["model_name"] == selected_row["model_name"])
        & (problem_runs["idx_answer"] == selected_row["idx_answer"])
    ].iloc[0]

    with st.expander("Full model response"):
        st.text_area(
            "Model response",
            value=str(full_run.get("answer", "")),
            height=300,
            disabled=True,
            label_visibility="collapsed",
        )

    with st.expander("User message"):
        st.text_area(
            "User message",
            value=str(full_run.get("user_message", "")),
            height=200,
            disabled=True,
            label_visibility="collapsed",
        )


def _render_sample(row: pd.Series, outputs: pd.DataFrame) -> None:
    """Render a single problem with paper metadata and model runs."""
    problem_idx = str(row.get("problem_idx", ""))
    reveal_key = f"arxivmath_reveal_{problem_idx}"

    st.caption(f"**Problem:** {problem_idx} · **arXiv:** {row.get('source', '—')}")

    left, right = st.columns(2)

    with left:
        st.subheader("Problem")
        st.markdown(str(row.get("problem", "")))
        if st.button("Reveal gold answer", key=reveal_key):
            st.session_state[reveal_key] = True
        if st.session_state.get(reveal_key):
            st.success(str(row.get("answer", "")))

    with right:
        st.subheader("Paper")
        st.markdown(f"**{row.get('title', '—')}**")
        st.write(row.get("authors", "—"))
        source = str(row.get("source", "")).strip()
        if source:
            st.link_button("View on arXiv", f"https://arxiv.org/abs/{source}")

        _render_model_runs(problem_idx, outputs)


def _sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Filter problems by ``problem_idx`` from the sidebar."""
    problem_ids = sorted(
        df["problem_idx"].unique(),
        key=lambda value: int(value) if str(value).isdigit() else value,
    )
    with st.sidebar:
        st.subheader("Filters")
        selected = st.multiselect(
            "Problem",
            problem_ids,
            default=problem_ids,
            key="arxivmath_problems",
        )

    if selected and len(selected) < len(problem_ids):
        return df[df["problem_idx"].isin(selected)].reset_index(drop=True)
    return df.reset_index(drop=True)


problems_df = _load_problems()
outputs_df = _load_outputs()


def _overview_callback(df: pd.DataFrame) -> None:
    _render_overview(df, outputs_df)


def _sample_callback(row: pd.Series) -> None:
    _render_sample(row, outputs_df)


render_dataset_page(
    title="ArXiv Math 0526",
    df=problems_df,
    id_column="problem_idx",
    render_overview=_overview_callback,
    render_sample=_sample_callback,
    sidebar_filters=_sidebar_filters,
    key_prefix="arxivmath",
)
