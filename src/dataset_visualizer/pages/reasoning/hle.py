"""Humanity's Last Exam (HLE) dataset exploration page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dataset_visualizer.components.charts import bar_chart, pie_chart
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.hle import (
    ANSWER_TYPE_EXACT_MATCH,
    ANSWER_TYPE_MULTIPLE_CHOICE,
    load_hle,
)
from dataset_visualizer.row_values import has_display_value


@st.cache_data(show_spinner=False)
def _load_data() -> pd.DataFrame:
    return load_hle()


def _render_overview(df: pd.DataFrame) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total questions", f"{len(df):,}")
    col2.metric("Categories", df["category"].nunique() if "category" in df.columns else 0)
    col3.metric("Subjects", df["raw_subject"].nunique() if "raw_subject" in df.columns else 0)
    split_name = df["split"].iloc[0] if "split" in df.columns and len(df) else "—"
    col4.metric("Split", split_name)

    if "category" in df.columns:
        bar_chart(df["category"], "Rows per category", x_label="Category")
    if "raw_subject" in df.columns:
        bar_chart(df["raw_subject"], "Rows per subject", x_label="Subject")
    if "answer_type" in df.columns:
        pie_chart(df["answer_type"], "Answer type distribution")
    if "has_image" in df.columns:
        image_counts = df["has_image"].map({True: "Multimodal", False: "Text only"})
        pie_chart(image_counts, "Modality")


def _render_image(row: pd.Series) -> None:
    """Render an HLE question image from a data URI or preview column."""
    image = row.get("image")
    if has_display_value(image) and isinstance(image, str) and image.strip():
        st.image(image, caption="Question image")
        return

    preview = row.get("image_preview")
    if has_display_value(preview):
        st.image(preview, caption="Question image")


def _render_sample(row: pd.Series) -> None:
    answer_type = row.get("answer_type", "—")
    modality = "Multimodal" if row.get("has_image") else "Text only"
    st.caption(
        f"**ID:** {row.get('id', '—')} · "
        f"**Category:** {row.get('category', '—')} · "
        f"**Subject:** {row.get('raw_subject', '—')} · "
        f"**Type:** {answer_type} · "
        f"**Modality:** {modality}"
    )

    st.markdown("**Question**")
    st.write(row.get("question", ""))
    if row.get("has_image"):
        _render_image(row)

    answer = row.get("answer")
    if has_display_value(answer):
        label = (
            "Correct answer"
            if answer_type == ANSWER_TYPE_MULTIPLE_CHOICE
            else "Exact answer"
        )
        st.success(f"**{label}:** {answer}")
    elif answer_type == ANSWER_TYPE_EXACT_MATCH:
        st.info("No exact answer recorded for this sample.")

    author = row.get("author_name")
    if has_display_value(author):
        st.caption(f"Contributor: {author}")

    rationale = row.get("rationale")
    if has_display_value(rationale):
        with st.expander("Rationale"):
            st.write(rationale)
            rationale_image = row.get("rationale_image")
            if has_display_value(rationale_image):
                st.image(rationale_image, caption="Rationale image")

    with st.expander("Raw JSON"):
        st.json(row.to_dict())


def _sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    with st.sidebar:
        st.subheader("Filters")
        if "category" in filtered.columns:
            categories = sorted(filtered["category"].dropna().unique())
            selected_categories = st.multiselect(
                "Category",
                categories,
                default=categories,
                key="hle_categories",
            )
            if selected_categories and len(selected_categories) < len(categories):
                filtered = filtered[filtered["category"].isin(selected_categories)]

        if "raw_subject" in filtered.columns:
            subjects = sorted(filtered["raw_subject"].dropna().unique())
            selected_subjects = st.multiselect(
                "Subject",
                subjects,
                default=subjects,
                key="hle_subjects",
            )
            if selected_subjects and len(selected_subjects) < len(subjects):
                filtered = filtered[filtered["raw_subject"].isin(selected_subjects)]

        if "answer_type" in filtered.columns:
            answer_types = sorted(filtered["answer_type"].dropna().unique())
            selected_types = st.multiselect(
                "Answer type",
                answer_types,
                default=answer_types,
                key="hle_answer_types",
            )
            if selected_types and len(selected_types) < len(answer_types):
                filtered = filtered[filtered["answer_type"].isin(selected_types)]

        if "has_image" in filtered.columns:
            modality = st.radio(
                "Modality",
                ("All", "Text only", "Multimodal"),
                index=0,
                key="hle_modality",
            )
            if modality == "Text only":
                filtered = filtered[~filtered["has_image"]]
            elif modality == "Multimodal":
                filtered = filtered[filtered["has_image"]]

    return filtered.reset_index(drop=True)


df = _load_data()

render_dataset_page(
    title="Humanity's Last Exam",
    df=df,
    id_column="id",
    render_overview=_render_overview,
    render_sample=_render_sample,
    dataset_id="hle",
    sidebar_filters=_sidebar_filters,
    key_prefix="hle",
)
