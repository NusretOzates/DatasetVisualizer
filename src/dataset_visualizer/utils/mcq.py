"""MCQ rendering helpers."""

from __future__ import annotations

import pandas as pd

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
