"""Dataset loader registry and navigation builder."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import streamlit as st

from dataset_visualizer.config import AppConfig, DatasetEntry, get_dataset_by_id, load_config
from dataset_visualizer.loaders.aime_2026 import load_aime_2026
from dataset_visualizer.loaders.arxivmath import load_problems
from dataset_visualizer.loaders.global_mmlu import load_global_mmlu
from dataset_visualizer.loaders.gpqa import load_gpqa_diamond
from dataset_visualizer.loaders.livecodebench import load_livecodebench
from dataset_visualizer.loaders.mmlu import load_mmlu
from dataset_visualizer.loaders.mmlu_pro import load_mmlu_pro
from dataset_visualizer.loaders.swe_bench import (
    load_swe_bench_multilingual,
    load_swe_bench_pro,
    load_swe_bench_verified,
)

if TYPE_CHECKING:
    from streamlit.navigation.page import StreamlitPage

PAGES_ROOT = Path(__file__).resolve().parent / "pages"

LOADER_REGISTRY: dict[str, Callable[..., pd.DataFrame]] = {
    "aime_2026": load_aime_2026,
    "arxivmath": load_problems,
    "global_mmlu": load_global_mmlu,
    "gpqa": load_gpqa_diamond,
    "livecodebench": load_livecodebench,
    "mmlu": load_mmlu,
    "mmlu_pro": load_mmlu_pro,
    "swe_bench_multilingual": load_swe_bench_multilingual,
    "swe_bench_pro": load_swe_bench_pro,
    "swe_bench_verified": load_swe_bench_verified,
}


def build_navigation(config: AppConfig) -> dict[str, list[StreamlitPage]]:
    """Build st.navigation groups from config — one Page per dataset entry.

    Args:
        config: Validated application configuration.

    Returns:
        Mapping of sidebar section labels to Streamlit pages.
    """
    pages: dict[str, list[StreamlitPage]] = {}
    for category_key, datasets in config.categories.items():
        label = category_key.replace("_", " ").title()
        pages[label] = [
            st.Page(
                str(PAGES_ROOT / category_key / f"{ds.id}.py"),
                title=ds.label,
                icon=ds.icon,
            )
            for ds in datasets
        ]
    return pages


def get_dataset_meta(dataset_id: str, config: AppConfig | None = None) -> DatasetEntry | None:
    """Look up dataset metadata by id for the home page table."""
    app_config = config or load_config()
    return get_dataset_by_id(app_config, dataset_id)


def load_dataset_frame(loader_name: str, **kwargs: object) -> pd.DataFrame | None:
    """Invoke a registered loader by name, returning None if not registered."""
    loader = LOADER_REGISTRY.get(loader_name)
    if loader is None:
        return None
    return loader(**kwargs)
