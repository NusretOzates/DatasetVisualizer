"""Consistent two-tab layout for dataset pages."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import streamlit as st

from dataset_visualizer.components.sample_navigator import sample_navigator


def render_dataset_page(
    title: str,
    df: pd.DataFrame,
    id_column: str,
    render_overview: Callable[[pd.DataFrame], None],
    render_sample: Callable[[pd.Series], None],
    sidebar_filters: Callable[[pd.DataFrame], pd.DataFrame] | None = None,
    key_prefix: str = "page",
) -> None:
    """Render Overview and Sample Inspector tabs with optional sidebar filters.

    Args:
        title: Page heading.
        df: Full dataset DataFrame.
        id_column: Column used for sample ID search.
        render_overview: Callback for the Overview tab content.
        render_sample: Callback for a single sample row.
        sidebar_filters: Optional callback that returns a filtered DataFrame.
        key_prefix: Widget key prefix passed to the sample navigator.
    """
    st.title(title)

    filtered = sidebar_filters(df) if sidebar_filters else df

    tab_overview, tab_sample = st.tabs(["Overview", "Sample Inspector"])

    with tab_overview:
        render_overview(filtered)

    with tab_sample:
        row, _idx, _total = sample_navigator(filtered, id_column=id_column, key_prefix=key_prefix)
        if not row.empty:
            render_sample(row)
