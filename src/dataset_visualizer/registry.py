"""Dataset loader registry."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from dataset_visualizer.loaders.aime_2026 import load_aime_2026
from dataset_visualizer.loaders.arxivmath import load_problems
from dataset_visualizer.loaders.global_mmlu import load_global_mmlu
from dataset_visualizer.loaders.gpqa import load_gpqa_diamond
from dataset_visualizer.loaders.hle import load_hle
from dataset_visualizer.loaders.livecodebench import load_livecodebench
from dataset_visualizer.loaders.mmlu import load_mmlu
from dataset_visualizer.loaders.mmlu_pro import load_mmlu_pro
from dataset_visualizer.loaders.mmmlu import load_mmmlu
from dataset_visualizer.loaders.swe_bench import (
    load_swe_bench_multilingual,
    load_swe_bench_pro,
    load_swe_bench_verified,
)

LOADER_REGISTRY: dict[str, Callable[..., pd.DataFrame]] = {
    "aime_2026": load_aime_2026,
    "arxivmath": load_problems,
    "global_mmlu": load_global_mmlu,
    "gpqa": load_gpqa_diamond,
    "hle": load_hle,
    "livecodebench": load_livecodebench,
    "mmlu": load_mmlu,
    "mmlu_pro": load_mmlu_pro,
    "mmmlu": load_mmmlu,
    "swe_bench_multilingual": load_swe_bench_multilingual,
    "swe_bench_pro": load_swe_bench_pro,
    "swe_bench_verified": load_swe_bench_verified,
}


def load_dataset_frame(loader_name: str, **kwargs: object) -> pd.DataFrame | None:
    """Invoke a registered loader by name, returning None if not registered."""
    loader = LOADER_REGISTRY.get(loader_name)
    if loader is None:
        return None
    return loader(**kwargs)
