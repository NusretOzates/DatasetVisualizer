"""Code-generation problem rendering helpers."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st


def _format_test_value(raw: str, testtype: str) -> tuple[str, str | None]:
    """Pretty-print a test value and pick a syntax-highlighting language."""
    stripped = raw.strip()
    if testtype == "functional":
        return stripped, "python"
    try:
        parsed = json.loads(stripped)
        return json.dumps(parsed, indent=2), "json"
    except json.JSONDecodeError:
        return raw, None


def render_test_cases(
    test_cases: list[dict[str, Any]] | None,
    *,
    title: str = "Test cases",
    limit: int | None = None,
) -> None:
    """Render test cases as expandable input/output code blocks.

    Args:
        test_cases: Parsed test-case dicts with input, output, and testtype.
        title: Section heading.
        limit: Optional cap on how many cases to show.
    """
    if not test_cases:
        st.info(f"No {title.lower()}.")
        return

    total = len(test_cases)
    visible = test_cases[:limit] if limit is not None else test_cases
    st.markdown(f"**{title}** ({total:,} total)")

    for index, case in enumerate(visible, start=1):
        testtype = str(case.get("testtype", "stdin"))
        with st.expander(f"Test {index} · {testtype}", expanded=index == 1):
            inp_text, inp_lang = _format_test_value(str(case.get("input", "")), testtype)
            out_text, out_lang = _format_test_value(str(case.get("output", "")), testtype)

            col_in, col_out = st.columns(2)
            with col_in:
                st.markdown("**Input**")
                st.code(inp_text, language=inp_lang)
            with col_out:
                st.markdown("**Expected output**")
                st.code(out_text, language=out_lang)

    if limit is not None and total > limit:
        st.caption(f"Showing first {limit} of {total:,} cases.")


def render_code_problem(row: pd.Series) -> None:
    """Render a LiveCodeBench-style code problem with public tests.

    Args:
        row: Dataset row with question content, starter code, tests, and metadata.
    """
    st.caption(
        f"ID: **{row.get('question_id', '—')}** · "
        f"Platform: **{row.get('platform', '—')}** · "
        f"Difficulty: **{row.get('difficulty', '—')}** · "
        f"Contest: **{row.get('contest_id', '—')}** · "
        f"Date: **{row.get('contest_date', '—')}**"
    )

    title = row.get("question_title")
    if title:
        st.subheader(str(title))

    st.markdown("**Problem**")
    st.markdown(str(row.get("question_content", "")))

    starter_code = row.get("starter_code")
    if starter_code and str(starter_code).strip():
        st.markdown("**Starter code**")
        st.code(str(starter_code), language="python")

    public_tests = row.get("public_test_cases")
    if not isinstance(public_tests, list):
        public_tests = []

    render_test_cases(public_tests, title="Public test cases")

    functional_cases = [case for case in public_tests if case.get("testtype") == "functional"]
    metadata = row.get("metadata")
    if functional_cases and isinstance(metadata, dict):
        func_name = metadata.get("func_name")
        if func_name:
            st.caption(f"Functional tests target `{func_name}`.")
