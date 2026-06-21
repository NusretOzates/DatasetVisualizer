"""ArXiv Math 0526 dataset loaders."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from datasets import load_dataset

from dataset_visualizer.loaders.base import cache_dir

PROBLEMS_HF_ID = "MathArena/arxivmath-0526"
OUTPUTS_HF_ID = "MathArena/arxivmath-0526_outputs"


@st.cache_data(show_spinner="Downloading ArXiv Math problems …")
def load_problems(split: str = "train") -> pd.DataFrame:
    """Load and normalize the ArXiv Math 0526 problems dataset.

    Args:
        split: Dataset split to load (default ``train``).

    Returns:
        Normalized DataFrame with ``problem_idx`` cast to string for joins.
    """
    cache_dir("arxivmath")
    dataset = load_dataset(PROBLEMS_HF_ID, split=split)
    df = dataset.to_pandas()
    df["problem_idx"] = df["problem_idx"].astype(str)
    return df


@st.cache_data(show_spinner="Downloading ArXiv Math model outputs …")
def load_outputs(split: str = "train") -> pd.DataFrame:
    """Load and normalize the ArXiv Math 0526 model outputs dataset.

    Args:
        split: Dataset split to load (default ``train``).

    Returns:
        Normalized DataFrame with ``problem_idx`` cast to string for joins.
    """
    cache_dir("arxivmath_outputs")
    dataset = load_dataset(OUTPUTS_HF_ID, split=split)
    df = dataset.to_pandas()
    df["problem_idx"] = df["problem_idx"].astype(str)
    return df
