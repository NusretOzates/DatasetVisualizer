"""Generic Hugging Face benchmark loader driven by config metadata."""

from __future__ import annotations

import pandas as pd
from datasets import get_dataset_config_names, load_dataset
from huggingface_hub import hf_hub_download

from dataset_visualizer.config import DatasetEntry
from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.benchmark_normalize import normalize_benchmark
from dataset_visualizer.loaders.cache import loader_cache
from dataset_visualizer.loaders.split_select import select_smallest_split


def _load_jsonl(hf_id: str, source_file: str) -> pd.DataFrame:
    path = hf_hub_download(repo_id=hf_id, filename=source_file, repo_type="dataset")
    return pd.read_json(path, lines=True)


def _load_single(
    hf_id: str,
    hf_config: str | None,
    split: str,
) -> pd.DataFrame:
    if hf_config:
        dataset = load_dataset(hf_id, hf_config, split=split)
    else:
        dataset = load_dataset(hf_id, split=split)
    return dataset.to_pandas()


def _config_names(hf_id: str, exclude_configs: list[str]) -> list[str]:
    """Return loadable Hub config names for a multi-config dataset."""
    return [name for name in get_dataset_config_names(hf_id) if name not in exclude_configs]


def _load_multi_config(
    hf_id: str,
    split: str,
    exclude_configs: list[str],
) -> pd.DataFrame:
    configs = _config_names(hf_id, exclude_configs)
    frames: list[pd.DataFrame] = []
    for config_name in configs:
        frame = _load_single(hf_id, config_name, split)
        frame["subject"] = config_name
        frames.append(frame)
    if not frames:
        msg = f"No configs available for dataset {hf_id}"
        raise ValueError(msg)
    return pd.concat(frames, ignore_index=True)


def _resolve_split(entry: DatasetEntry) -> str:
    """Pick the Hub split to load for inspection."""
    if entry.split:
        return entry.split
    hf_config = entry.hf_config
    if entry.multi_config:
        configs = _config_names(entry.hf_id, entry.exclude_configs)
        if not configs:
            msg = f"No configs available for dataset {entry.hf_id}"
            raise ValueError(msg)
        hf_config = configs[0]
    return select_smallest_split(entry.hf_id, hf_config)


def _load_frame(entry: DatasetEntry) -> pd.DataFrame:
    if not entry.hf_id:
        msg = f"Dataset {entry.id} is missing hf_id"
        raise ValueError(msg)
    if entry.source_file:
        return _load_jsonl(entry.hf_id, entry.source_file)
    split = _resolve_split(entry)
    if entry.multi_config:
        return _load_multi_config(entry.hf_id, split, entry.exclude_configs)
    frame = _load_single(entry.hf_id, entry.hf_config, split)
    if "split" not in frame.columns:
        frame = frame.copy()
        frame["split"] = split
    return frame


def load_hf_benchmark_entry(entry: DatasetEntry) -> pd.DataFrame:
    """Load and normalize a catalog benchmark from its config entry."""
    cache_dir(entry.id)
    raw = _load_frame(entry)
    id_column = entry.id_column or "sample_id"
    profile = entry.profile or "generic"
    return normalize_benchmark(raw, profile, id_column)


def make_hf_benchmark_loader(entry: DatasetEntry):
    """Return a cached loader function for a config entry."""
    label = entry.label

    @loader_cache(show_spinner=f"Downloading {label} …")
    def _loader(_params: dict) -> pd.DataFrame:
        return load_hf_benchmark_entry(entry)

    return _loader
