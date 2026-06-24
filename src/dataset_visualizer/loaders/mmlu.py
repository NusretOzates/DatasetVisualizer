"""MMLU dataset loader."""

from __future__ import annotations

import pandas as pd
from datasets import load_dataset

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache
from dataset_visualizer.loaders.split_select import select_smallest_split

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


@loader_cache(show_spinner="Downloading MMLU …")
def load_mmlu(config: str = MMLU_CONFIG) -> pd.DataFrame:
    """Load and normalize the MMLU benchmark dataset.

    Args:
        config: MMLU config name (default ``all`` combines all subjects).

    Returns:
        Normalized DataFrame with answer_letter column and split metadata.
    """
    cache_dir("mmlu")
    split = select_smallest_split(MMLU_HF_ID, config)
    dataset = load_dataset(MMLU_HF_ID, config, split=split)
    df = dataset.to_pandas()
    df["answer_letter"] = df["answer"].map(_normalize_answer)
    df["split"] = split
    return df
