"""MMMLU dataset exploration page."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from dataset_visualizer.components.charts import bar_chart, pie_chart
from dataset_visualizer.components.mcq_viewer import render_mcq
from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.mmmlu import (
    DEFAULT_LOCALE,
    list_mmmlu_locales,
    load_mmmlu,
)
from dataset_visualizer.row_values import has_display_value

LOCALE_LABELS: dict[str, str] = {
    "AR_XY": "Arabic",
    "BN_BD": "Bengali",
    "DE_DE": "German",
    "ES_LA": "Spanish",
    "FR_FR": "French",
    "HI_IN": "Hindi",
    "ID_ID": "Indonesian",
    "IT_IT": "Italian",
    "JA_JP": "Japanese",
    "KO_KR": "Korean",
    "PT_BR": "Portuguese (Brazil)",
    "SW_KE": "Swahili",
    "YO_NG": "Yoruba",
    "ZH_CN": "Chinese (Simplified)",
}
POPULAR_LOCALES = (
    "DE_DE",
    "ES_LA",
    "FR_FR",
    "JA_JP",
    "KO_KR",
    "PT_BR",
    "ZH_CN",
    "AR_XY",
    "HI_IN",
)


@st.cache_data(show_spinner=False)
def _load_locale(locale: str) -> pd.DataFrame:
    return load_mmmlu(locale=locale)


def _locale_options() -> list[str]:
    try:
        return list_mmmlu_locales()
    except OSError:
        return list(POPULAR_LOCALES)


def _format_locale(locale: str) -> str:
    label = LOCALE_LABELS.get(locale, locale)
    return f"{label} ({locale})"


def _render_overview(df: pd.DataFrame) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total rows", f"{len(df):,}")
    col2.metric("Subjects", df["subject"].nunique() if len(df) else 0)
    language = df["language"].iloc[0] if "language" in df.columns and len(df) else "—"
    col3.metric("Locale", language)
    split_name = df["split"].iloc[0] if "split" in df.columns and len(df) else "—"
    col4.metric("Split", split_name)

    bar_chart(df["subject"], "Rows per subject", x_label="Subject")
    pie_chart(df["answer_letter"], "Answer letter distribution")


def _render_sample(row: pd.Series) -> None:
    st.caption(
        f"Subject: **{row.get('subject', '—')}** · "
        f"Locale: **{row.get('language', '—')}** · "
        f"Sample ID: **{row.get('sample_id', '—')}**"
    )
    render_mcq(row)
    with st.expander("Metadata"):
        for field in ("sample_id", "language", "split", "subject"):
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
            key="mmmlu_subjects",
        )

    if selected and len(selected) < len(subjects):
        return df[df["subject"].isin(selected)].reset_index(drop=True)
    return df.reset_index(drop=True)


with st.sidebar:
    locales = _locale_options()
    default_locale = DEFAULT_LOCALE if DEFAULT_LOCALE in locales else locales[0]
    locale = st.selectbox(
        "Locale",
        locales,
        index=locales.index(default_locale),
        format_func=_format_locale,
        key="mmmlu_locale",
    )

df = _load_locale(locale)

render_dataset_page(
    title="MMMLU",
    df=df,
    id_column="sample_id",
    render_overview=_render_overview,
    render_sample=_render_sample,
    sidebar_filters=_sidebar_filters,
    key_prefix="mmmlu",
)
