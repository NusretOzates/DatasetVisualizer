"""MCQ rendering helpers."""

from __future__ import annotations

import pandas as pd

ANSWER_LETTERS = tuple(chr(ord("A") + i) for i in range(26))


def _letter_from_answer_value(answer: object) -> str:
    """Map a letter, numeric index, or raw answer cell to a display letter."""
    if answer is None or (isinstance(answer, float) and pd.isna(answer)):
        return ""
    if isinstance(answer, int):
        idx = answer
        if 0 <= idx < len(ANSWER_LETTERS):
            return ANSWER_LETTERS[idx]
        return str(answer)
    raw = str(answer).strip().upper()
    if len(raw) == 1 and raw in ANSWER_LETTERS:
        return raw
    if raw.isdigit():
        idx = int(raw)
        if 0 <= idx < len(ANSWER_LETTERS):
            return ANSWER_LETTERS[idx]
    return raw


def resolve_correct_letter(row: pd.Series, answer_col: str = "answer_letter") -> str:
    """Extract the correct answer letter from a normalized or raw row."""
    if answer_col in row and pd.notna(row[answer_col]):
        return _letter_from_answer_value(row[answer_col])
    if "answer" in row and pd.notna(row["answer"]):
        return _letter_from_answer_value(row["answer"])
    if "answer_index" in row and pd.notna(row["answer_index"]):
        return _letter_from_answer_value(row["answer_index"])
    return ""


def _coerce_choices(choices: object) -> list[object]:
    """Normalize HF choices (list, ndarray, scalar) into a plain Python list."""
    if choices is None:
        return []
    if isinstance(choices, str):
        return [choices]
    if hasattr(choices, "tolist"):
        choices = choices.tolist()
    try:
        if len(choices) == 0:
            return []
    except TypeError:
        return [choices]
    return list(choices)


def format_options(choices: object) -> list[tuple[str, str]]:
    """Pair letter labels with choice text, filtering empty entries."""
    coerced = _coerce_choices(choices)
    options: list[tuple[str, str]] = []
    letter_idx = 0
    for text in coerced:
        label = str(text).strip()
        if not label or label.upper() == "N/A":
            continue
        options.append((ANSWER_LETTERS[letter_idx], label))
        letter_idx += 1
    return options
