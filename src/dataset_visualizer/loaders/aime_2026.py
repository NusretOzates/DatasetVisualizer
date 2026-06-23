"""AIME 2026 dataset loader."""

from __future__ import annotations

import pandas as pd
from datasets import load_dataset

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache

AIME_2026_HF_ID = "MathArena/aime_2026"


@loader_cache(show_spinner="Downloading AIME 2026 …")
def load_aime_2026(split: str = "train") -> pd.DataFrame:
    """Load and normalize the AIME 2026 math competition benchmark.

    Args:
        split: Dataset split to load (default ``train``).

    Returns:
        Normalized DataFrame with ``problem_idx`` cast to string for navigation.
    """
    cache_dir("aime_2026")
    dataset = load_dataset(AIME_2026_HF_ID, split=split)
    df = dataset.to_pandas()
    df["problem_idx"] = df["problem_idx"].astype(str)
    return df
