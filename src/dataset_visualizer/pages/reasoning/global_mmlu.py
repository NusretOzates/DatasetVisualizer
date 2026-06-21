"""Global-MMLU dataset exploration page."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from dataset_visualizer.components.charts import bar_chart, pie_chart
from dataset_visualizer.components.mcq_viewer import render_mcq
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.global_mmlu import (
    DEFAULT_LANGUAGE,
    list_global_mmlu_languages,
    load_global_mmlu,
)
from dataset_visualizer.row_values import has_display_value

SPLIT_OPTIONS = ("dev", "test")
POPULAR_LANGUAGES = ("en", "es", "fr", "de", "zh", "ja", "ko", "pt", "ar", "hi")


@st.cache_data(show_spinner=False)
def _load_split(language: str, split: str) -> pd.DataFrame:
    return load_global_mmlu(language=language, split=split)


def _language_options() -> list[str]:
    try:
        return list_global_mmlu_languages()
    except OSError:
        return list(POPULAR_LANGUAGES)


def _render_overview(df: pd.DataFrame) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total rows", f"{len(df):,}")
    col2.metric("Subjects", df["subject"].nunique() if len(df) else 0)
    language = df["language"].iloc[0] if "language" in df.columns and len(df) else "—"
    col3.metric("Language", language)
    split_name = df["split"].iloc[0] if "split" in df.columns and len(df) else "—"
    col4.metric("Split", split_name)

    bar_chart(df["subject"], "Rows per subject", x_label="Subject")
    if "subject_category" in df.columns:
        bar_chart(df["subject_category"], "Subject categories", x_label="Category")
    if "cultural_sensitivity_label" in df.columns:
        pie_chart(df["cultural_sensitivity_label"], "Cultural sensitivity (CS vs CA)")


def _render_sample(row: pd.Series) -> None:
    st.caption(
        f"Subject: **{row.get('subject', '—')}** · "
        f"Language: **{row.get('language', '—')}** · "
        f"CS label: **{row.get('cultural_sensitivity_label', '—')}**"
    )
    render_mcq(row)
    with st.expander("Annotations"):
        for field in ("required_knowledge", "culture", "region", "country", "time_sensitive"):
            if field in row.index and has_display_value(row[field]):
                st.write(f"**{field}:** {row[field]}")
    with st.expander("Raw JSON"):
        st.json(json.loads(row.to_json()))


def _sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    subjects = sorted(df["subject"].unique())
    with st.sidebar:
        st.subheader("Filters")
        selected = st.multiselect(
            "Subject",
            subjects,
            default=subjects,
            key="global_mmlu_subjects",
        )
        if "cultural_sensitivity_label" in df.columns:
            cs_labels = sorted(df["cultural_sensitivity_label"].dropna().unique())
            selected_cs = st.multiselect(
                "Cultural sensitivity",
                cs_labels,
                default=cs_labels,
                key="global_mmlu_cs",
            )
        else:
            selected_cs = []

    filtered = df.copy()
    if selected and len(selected) < len(subjects):
        filtered = filtered[filtered["subject"].isin(selected)]
    if selected_cs and "cultural_sensitivity_label" in filtered.columns:
        filtered = filtered[filtered["cultural_sensitivity_label"].isin(selected_cs)]

    return filtered.reset_index(drop=True)


with st.sidebar:
    languages = _language_options()
    default_lang = DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in languages else languages[0]
    language = st.selectbox(
        "Language",
        languages,
        index=languages.index(default_lang),
        key="global_mmlu_language",
    )
    split = st.selectbox("Split", SPLIT_OPTIONS, index=0, key="global_mmlu_split")

df = _load_split(language, split)

render_dataset_page(
    title="Global-MMLU",
    df=df,
    id_column="sample_id",
    render_overview=_render_overview,
    render_sample=_render_sample,
    sidebar_filters=_sidebar_filters,
    key_prefix="global_mmlu",
)
