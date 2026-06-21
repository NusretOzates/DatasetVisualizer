"""Sample navigation controls for the Sample Inspector tab."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def sample_navigator(
    df: pd.DataFrame,
    id_column: str | None = None,
    key_prefix: str = "sample",
) -> tuple[pd.Series, int, int]:
    """Render index slider, prev/next buttons, and optional ID search.

    Args:
        df: Filtered DataFrame to navigate.
        id_column: Optional column name for ID-based search.
        key_prefix: Streamlit widget key prefix to avoid collisions.

    Returns:
        Tuple of (selected row, zero-based index, total row count).
    """
    total = len(df)
    if total == 0:
        st.warning("No samples match the current filters.")
        return pd.Series(dtype=object), 0, 0

    st.caption(f"Showing {total:,} samples")
    navigable = df.reset_index(drop=True)

    if id_column and id_column in df.columns:
        search = st.text_input("Search by ID", key=f"{key_prefix}_search")
        if search:
            matches = navigable[navigable[id_column].astype(str) == search]
            if not matches.empty:
                idx = int(matches.index[0])
                return navigable.iloc[idx], idx, total
            st.info(f"No row found with {id_column}={search!r}")

    state_key = f"{key_prefix}_idx"
    if state_key not in st.session_state:
        st.session_state[state_key] = 0

    max_idx = max(0, total - 1)
    st.session_state[state_key] = min(st.session_state[state_key], max_idx)

    col_prev, col_slider, col_next = st.columns([1, 4, 1])

    with col_prev:
        if st.button(
            "◀ Prev",
            key=f"{key_prefix}_prev",
            disabled=st.session_state[state_key] <= 0,
        ):
            st.session_state[state_key] -= 1
            st.rerun()

    with col_next:
        if st.button(
            "Next ▶",
            key=f"{key_prefix}_next",
            disabled=st.session_state[state_key] >= max_idx,
        ):
            st.session_state[state_key] += 1
            st.rerun()

    with col_slider:
        st.session_state[state_key] = st.slider(
            "Sample index",
            min_value=0,
            max_value=max_idx,
            value=st.session_state[state_key],
        )

    idx = int(st.session_state[state_key])
    return navigable.iloc[idx], idx, total
