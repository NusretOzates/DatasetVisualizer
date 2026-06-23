"""Humanity's Last Exam (HLE) dataset loader."""

from __future__ import annotations

import pandas as pd
from datasets import load_dataset

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache

HLE_HF_ID = "cais/hle"
HLE_SPLIT = "test"
ANSWER_TYPE_EXACT_MATCH = "exactMatch"
ANSWER_TYPE_MULTIPLE_CHOICE = "multipleChoice"


def _has_image_value(value: object) -> bool:
    """Return whether an HLE image field contains displayable content."""
    if value is None:
        return False
    if isinstance(value, float) and pd.isna(value):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if hasattr(value, "shape") and hasattr(value, "size"):
        return value.size > 0
    return bool(pd.notna(value))


def _normalize_hle_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Add explorer-friendly columns to raw HLE rows."""
    normalized = df.copy()
    if "image" in normalized.columns:
        normalized["has_image"] = normalized["image"].map(_has_image_value)
    else:
        normalized["has_image"] = False
    normalized["split"] = HLE_SPLIT
    return normalized


@loader_cache(show_spinner="Downloading Humanity's Last Exam …")
def load_hle() -> pd.DataFrame:
    """Load and normalize the Humanity's Last Exam benchmark dataset.

    Returns:
        Normalized DataFrame with ``has_image`` and ``split`` metadata columns.

    Note:
        The upstream dataset is gated on Hugging Face; set ``HF_TOKEN`` in ``.env``
        and accept the dataset terms on the Hub.
    """
    cache_dir("hle")
    dataset = load_dataset(HLE_HF_ID, split=HLE_SPLIT)
    return _normalize_hle_frame(dataset.to_pandas())
