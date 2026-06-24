"""MMMLU multilingual MCQ dataset loader."""

from __future__ import annotations

import pandas as pd
from datasets import get_dataset_config_names, load_dataset

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache
from dataset_visualizer.loaders.split_select import select_smallest_split

MMMLU_HF_ID = "openai/MMMLU"
DEFAULT_LOCALE = "DE_DE"
LOCALE_LABELS: dict[str, str] = {
    "AR_XY": "Arabic",
    "BN_BD": "Bengali",
    "DE_DE": "German",
    "ES_LA": "Spanish",
    "FR_FR": "French",
    "HI_IN": "Hindi",
    "ID_ID": "Indonesian",
    "IT_IT": "Italian",
    "JA_JP": "Japanese",
    "KO_KR": "Korean",
    "PT_BR": "Portuguese (Brazil)",
    "SW_KE": "Swahili",
    "YO_NG": "Yoruba",
    "ZH_CN": "Chinese (Simplified)",
}
POPULAR_LOCALES = tuple(
    locale
    for locale in ("DE_DE", "ES_LA", "FR_FR", "JA_JP", "KO_KR", "PT_BR", "AR_XY", "HI_IN")
    if locale in LOCALE_LABELS
)


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


@loader_cache(show_spinner="Downloading MMMLU …")
def load_mmmlu(locale: str = DEFAULT_LOCALE) -> pd.DataFrame:
    """Load and normalize MMMLU for a single locale config.

    Args:
        locale: Locale config (e.g. ``DE_DE``, ``FR_FR``, ``JA_JP``).

    Returns:
        Normalized DataFrame with ``choices`` and ``answer_letter`` columns.
    """
    cache_dir("mmmlu")
    split = select_smallest_split(MMMLU_HF_ID, locale)
    dataset = load_dataset(MMMLU_HF_ID, locale, split=split)
    return _normalize_mmmlu_frame(dataset.to_pandas(), locale=locale, split=split)
