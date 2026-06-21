"""SWE-bench issue and patch rendering helpers."""

from __future__ import annotations

import pandas as pd
import streamlit as st

TEST_LIST_PREVIEW_LIMIT = 50


def _render_test_list(tests: object, title: str) -> None:
    """Render a bullet list of test identifiers."""
    if tests is None or (isinstance(tests, float) and pd.isna(tests)):
        st.caption(f"{title}: none")
        return
    if not isinstance(tests, list):
        st.caption(f"{title}: {tests}")
        return
    if not tests:
        st.caption(f"{title}: none")
        return
    st.markdown(f"**{title}** ({len(tests)})")
    for test_name in tests[:TEST_LIST_PREVIEW_LIMIT]:
        st.write(f"- `{test_name}`")
    if len(tests) > TEST_LIST_PREVIEW_LIMIT:
        st.caption(f"… and {len(tests) - TEST_LIST_PREVIEW_LIMIT} more")


def render_issue(
    row: pd.Series,
    *,
    show_gold_patch: bool = True,
) -> None:
    """Render a SWE-bench issue with problem statement, hints, and patches."""
    instance_id = row.get("instance_id", "—")
    repo = row.get("repo", "—")
    base_commit = row.get("base_commit", "—")
    st.caption(f"**{instance_id}** · `{repo}` @ `{base_commit}`")

    if "repo_language" in row and pd.notna(row.get("repo_language")):
        st.caption(f"Language: **{row['repo_language']}**")

    if "difficulty" in row and pd.notna(row.get("difficulty")):
        st.caption(f"Difficulty: **{row['difficulty']}**")

    st.markdown("**Problem statement**")
    st.markdown(str(row.get("problem_statement", "")))

    hints = row.get("hints_text", "")
    if hints and str(hints).strip():
        with st.expander("Hints (issue comments)"):
            st.markdown(str(hints))

    if show_gold_patch:
        patch = row.get("patch", "")
        if patch and str(patch).strip():
            with st.expander("Gold patch"):
                st.code(str(patch), language="diff")

    test_patch = row.get("test_patch", "")
    if test_patch and str(test_patch).strip():
        with st.expander("Test patch"):
            st.code(str(test_patch), language="diff")

    col1, col2 = st.columns(2)
    with col1:
        _render_test_list(row.get("fail_to_pass"), "FAIL_TO_PASS")
    with col2:
        _render_test_list(row.get("pass_to_pass"), "PASS_TO_PASS")

    if "requirements" in row and pd.notna(row.get("requirements")):
        with st.expander("Requirements"):
            st.markdown(str(row["requirements"]))

    if "interface" in row and pd.notna(row.get("interface")):
        with st.expander("Interface"):
            st.code(str(row["interface"]), language="text")
