"""GPQA Diamond dataset loader."""

from __future__ import annotations

import hashlib
import random

import pandas as pd
from datasets import load_dataset

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache

GPQA_HF_ID = "Idavidrein/gpqa"
GPQA_CONFIG = "gpqa_diamond"
ANSWER_LETTERS = ("A", "B", "C", "D")
OPTION_COUNT = 4
REQUIRED_INCORRECT_COUNT = 3

QUESTION_COLUMNS = ("Question", "question", "problem")
CORRECT_COLUMNS = ("Correct Answer", "correct_answer", "answer")
INCORRECT_PREFIXES = (
    "Incorrect Answer",
    "incorrect_answer",
)


def _first_present(row: pd.Series, columns: tuple[str, ...]) -> str:
    """Return the first non-empty value from candidate column names."""
    for col in columns:
        if col in row.index and pd.notna(row[col]):
            text = str(row[col]).strip()
            if text:
                return text
    return ""


def _collect_incorrect_answers(row: pd.Series) -> list[str]:
    """Collect incorrect-answer columns from a GPQA CSV row."""
    incorrect: list[str] = []
    for col in row.index:
        name = str(col)
        if name.startswith("Incorrect Answer") or name.startswith("incorrect_answer"):
            value = row[col]
            if pd.notna(value):
                text = str(value).strip()
                if text:
                    incorrect.append(text)
    return incorrect[:3]


def _shuffle_choices(question: str, correct: str, incorrect: list[str]) -> tuple[list[str], str]:
    """Deterministically shuffle four options and return choices with the answer letter."""
    options = [correct, *incorrect[:REQUIRED_INCORRECT_COUNT]]
    while len(options) < OPTION_COUNT:
        options.append("")
    options = options[:OPTION_COUNT]

    seed = int(hashlib.sha256(question.encode("utf-8")).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    indexed = list(enumerate(options))
    rng.shuffle(indexed)

    choices: list[str] = []
    answer_letter = ""
    for letter_idx, (_, text) in enumerate(indexed):
        letter = ANSWER_LETTERS[letter_idx]
        choices.append(text)
        if text == correct:
            answer_letter = letter
    return choices, answer_letter


def _normalize_gpqa_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Build mcq_viewer-compatible columns from raw GPQA rows."""
    normalized = df.copy()

    if "choices" in normalized.columns and "answer_letter" in normalized.columns:
        normalized["split"] = GPQA_CONFIG
        return normalized

    choices_list: list[list[str]] = []
    answer_letters: list[str] = []

    for _, row in normalized.iterrows():
        question = _first_present(row, QUESTION_COLUMNS)
        correct = _first_present(row, CORRECT_COLUMNS)
        incorrect = _collect_incorrect_answers(row)

        if correct and len(incorrect) >= REQUIRED_INCORRECT_COUNT:
            choices, answer_letter = _shuffle_choices(question, correct, incorrect)
        elif "answer" in row.index and pd.notna(row["answer"]):
            answer_letter = str(row["answer"]).strip().upper()
            choices = [answer_letter]
        else:
            choices, answer_letter = [], ""

        choices_list.append(choices)
        answer_letters.append(answer_letter)

    if "question" not in normalized.columns:
        normalized["question"] = normalized.apply(
            lambda row: _first_present(row, QUESTION_COLUMNS),
            axis=1,
        )

    normalized["choices"] = choices_list
    normalized["answer_letter"] = answer_letters
    normalized["split"] = GPQA_CONFIG
    return normalized


@loader_cache(show_spinner="Downloading GPQA Diamond …")
def load_gpqa_diamond() -> pd.DataFrame:
    """Load and normalize the GPQA Diamond graduate-level MCQ benchmark.

    Returns:
        Normalized DataFrame with ``choices`` and ``answer_letter`` columns.

    Note:
        The upstream dataset is gated on Hugging Face; set ``HF_TOKEN`` in ``.env``.
    """
    cache_dir("gpqa")
    dataset = load_dataset(GPQA_HF_ID, GPQA_CONFIG, split="train")
    return _normalize_gpqa_frame(dataset.to_pandas())
