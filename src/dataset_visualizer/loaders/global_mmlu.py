"""Global-MMLU multilingual MCQ dataset loader."""

from __future__ import annotations

import ast

import pandas as pd
import streamlit as st
from datasets import get_dataset_config_names, load_dataset

from dataset_visualizer.loaders.base import cache_dir

GLOBAL_MMLU_HF_ID = "CohereLabs/Global-MMLU"
DEFAULT_LANGUAGE = "en"


def _parse_annotation_list(raw: object) -> list[str]:
    """Parse string-encoded annotation lists from Global-MMLU."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return []
    if isinstance(raw, list):
        return [str(item) for item in raw]
    if not isinstance(raw, str):
        return [str(raw)]

    text = raw.strip()
    if not text:
        return []
    try:
        value = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return [text]
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _normalize_global_mmlu_frame(df: pd.DataFrame, language: str, split: str) -> pd.DataFrame:
    """Build mcq_viewer-compatible columns from Global-MMLU rows."""
    normalized = df.copy()
    normalized["choices"] = normalized.apply(
        lambda row: [
            row["option_a"],
            row["option_b"],
            row["option_c"],
            row["option_d"],
        ],
        axis=1,
    )
    normalized["answer_letter"] = normalized["answer"].astype(str).str.upper()
    normalized["language"] = language
    normalized["split"] = split

    for col in ("required_knowledge", "reference", "culture", "region", "country"):
        if col in normalized.columns:
            normalized[col] = normalized[col].map(_parse_annotation_list)

    return normalized


def list_global_mmlu_languages() -> list[str]:
    """Return sorted language config names available on Hugging Face."""
    cache_dir("global_mmlu")
    return sorted(get_dataset_config_names(GLOBAL_MMLU_HF_ID))


@st.cache_data(show_spinner="Downloading Global-MMLU …")
def load_global_mmlu(language: str = DEFAULT_LANGUAGE, split: str = "dev") -> pd.DataFrame:
    """Load and normalize Global-MMLU for a single language config.

    Args:
        language: ISO language code config (e.g. ``en``, ``es``, ``fr``).
        split: Dataset split (``dev`` or ``test``).

    Returns:
        Normalized DataFrame with ``choices`` and ``answer_letter`` columns.
    """
    cache_dir("global_mmlu")
    dataset = load_dataset(GLOBAL_MMLU_HF_ID, language, split=split)
    return _normalize_global_mmlu_frame(dataset.to_pandas(), language=language, split=split)
