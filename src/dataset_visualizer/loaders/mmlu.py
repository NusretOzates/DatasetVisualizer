"""MMLU dataset loader."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from datasets import load_dataset

from dataset_visualizer.loaders.base import cache_dir

MMLU_HF_ID = "cais/mmlu"
MMLU_CONFIG = "all"
ANSWER_LETTERS = ("A", "B", "C", "D")


def _normalize_answer(answer: int | str) -> str:
    """Convert MMLU ClassLabel int answers to letter labels."""
    if isinstance(answer, str):
        return answer.upper()
    if 0 <= answer < len(ANSWER_LETTERS):
        return ANSWER_LETTERS[answer]
    return str(answer)


@st.cache_data(show_spinner="Downloading MMLU …")
def load_mmlu(split: str = "test", config: str = MMLU_CONFIG) -> pd.DataFrame:
    """Load and normalize the MMLU benchmark dataset.

    Args:
        split: Dataset split to load (test, validation, or dev).
        config: MMLU config name (default ``all`` combines all subjects).

    Returns:
        Normalized DataFrame with answer_letter column and split metadata.
    """
    cache_dir("mmlu")
    dataset = load_dataset(MMLU_HF_ID, config, split=split)
    df = dataset.to_pandas()
    df["answer_letter"] = df["answer"].map(_normalize_answer)
    df["split"] = split
    return df
