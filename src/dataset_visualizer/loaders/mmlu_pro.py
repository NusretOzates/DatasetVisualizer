"""MMLU-Pro dataset loader."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
from datasets import load_dataset

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache
from dataset_visualizer.loaders.split_select import select_smallest_split

MMLU_PRO_HF_ID = "TIGER-Lab/MMLU-Pro"


def _filter_options(options: Sequence[str] | None) -> list[str]:
    """Remove empty and N/A placeholder options from MMLU-Pro option lists."""
    if options is None or len(options) == 0:
        return []
    filtered: list[str] = []
    for option in options:
        text = str(option).strip()
        if text and text.upper() != "N/A":
            filtered.append(text)
    return filtered


def _normalize_row_options(options: Sequence[str] | None) -> tuple[list[str], int]:
    """Filter options and return the cleaned list with its count."""
    filtered = _filter_options(options)
    return filtered, len(filtered)


@loader_cache(show_spinner="Downloading MMLU-Pro …")
def load_mmlu_pro() -> pd.DataFrame:
    """Load and normalize the MMLU-Pro benchmark dataset.

    Returns:
        Normalized DataFrame with filtered options, option_count, and split metadata.
    """
    cache_dir("mmlu_pro")
    split = select_smallest_split(MMLU_PRO_HF_ID)
    dataset = load_dataset(MMLU_PRO_HF_ID, split=split)
    df = dataset.to_pandas()

    normalized = df["options"].map(_normalize_row_options)
    df["options"] = normalized.map(lambda item: item[0])
    df["option_count"] = normalized.map(lambda item: item[1])
    df["split"] = split
    return df
