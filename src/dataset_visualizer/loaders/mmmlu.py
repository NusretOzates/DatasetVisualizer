"""MMMLU multilingual MCQ dataset loader."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from datasets import get_dataset_config_names, load_dataset

from dataset_visualizer.loaders.base import cache_dir

MMMLU_HF_ID = "openai/MMMLU"
DEFAULT_LOCALE = "DE_DE"
MMMLU_SPLIT = "test"


def _normalize_mmmlu_frame(df: pd.DataFrame, locale: str, split: str) -> pd.DataFrame:
    """Build mcq_viewer-compatible columns from MMMLU rows."""
    normalized = df.copy()
    normalized["question"] = normalized["Question"]
    normalized["choices"] = normalized.apply(
        lambda row: [row["A"], row["B"], row["C"], row["D"]],
        axis=1,
    )
    normalized["answer_letter"] = normalized["Answer"].astype(str).str.upper()
    normalized["subject"] = normalized["Subject"]
    normalized["sample_id"] = normalized["Unnamed: 0"].map(lambda idx: f"{locale}_{idx}")
    normalized["language"] = locale
    normalized["split"] = split
    return normalized


def list_mmmlu_locales() -> list[str]:
    """Return sorted locale config names available on Hugging Face (excludes ``default``)."""
    cache_dir("mmmlu")
    return sorted(name for name in get_dataset_config_names(MMMLU_HF_ID) if name != "default")


@st.cache_data(show_spinner="Downloading MMMLU …")
def load_mmmlu(locale: str = DEFAULT_LOCALE, split: str = MMMLU_SPLIT) -> pd.DataFrame:
    """Load and normalize MMMLU for a single locale config.

    Args:
        locale: Locale config (e.g. ``DE_DE``, ``FR_FR``, ``JA_JP``).
        split: Dataset split (only ``test`` is published).

    Returns:
        Normalized DataFrame with ``choices`` and ``answer_letter`` columns.
    """
    cache_dir("mmmlu")
    dataset = load_dataset(MMMLU_HF_ID, locale, split=split)
    return _normalize_mmmlu_frame(dataset.to_pandas(), locale=locale, split=split)
