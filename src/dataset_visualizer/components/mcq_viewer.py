"""MCQ rendering helpers."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import streamlit as st

ANSWER_LETTERS = tuple(chr(ord("A") + i) for i in range(26))


def resolve_correct_letter(row: pd.Series, answer_col: str = "answer_letter") -> str:
    """Extract the correct answer letter from a normalized or raw row."""
    if answer_col in row and pd.notna(row[answer_col]):
        return str(row[answer_col]).upper()

    if "answer" in row and pd.notna(row["answer"]):
        answer = row["answer"]
        try:
            idx = int(answer)
        except (TypeError, ValueError):
            return str(answer).upper()
        if 0 <= idx < len(ANSWER_LETTERS):
            return ANSWER_LETTERS[idx]
        return str(answer).upper()

    if "answer_index" in row and pd.notna(row["answer_index"]):
        idx = int(row["answer_index"])
        if 0 <= idx < len(ANSWER_LETTERS):
            return ANSWER_LETTERS[idx]

    return ""


def format_options(choices: Sequence[str] | None) -> list[tuple[str, str]]:
    """Pair letter labels with choice text, filtering empty entries."""
    if not choices:
        return []
    options: list[tuple[str, str]] = []
    letter_idx = 0
    for text in choices:
        if not text or not str(text).strip() or str(text).strip().upper() == "N/A":
            continue
        options.append((ANSWER_LETTERS[letter_idx], str(text)))
        letter_idx += 1
    return options


def render_mcq(
    row: pd.Series,
    *,
    question_col: str = "question",
    choices_col: str = "choices",
    answer_col: str = "answer_letter",
) -> None:
    """Render a multiple-choice question with the correct answer highlighted."""
    question = row.get(question_col, "")
    st.markdown("**Question**")
    st.write(question)

    choices = row.get(choices_col)
    if isinstance(choices, str):
        choices = [choices]

    correct = resolve_correct_letter(row, answer_col=answer_col)
    options = format_options(choices)

    if not options:
        st.warning("No options available for this sample.")
        return

    for letter, text in options:
        if letter == correct:
            st.success(f"**{letter}.** {text}")
        else:
            st.write(f"{letter}. {text}")

    if correct:
        st.caption(f"Correct answer: **{correct}**")
