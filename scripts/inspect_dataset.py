"""CLI to inspect a registered dataset's schema, dtypes, and sample row."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import pandas as pd

from dataset_visualizer.api.dataset_registry import get_descriptor
from dataset_visualizer.config import get_dataset_by_id, load_config
from dataset_visualizer.loaders.base import cache_dir

MAX_VALUE_LEN = 200

LOADER_CACHE_KEYS: dict[str, str] = {
    "aime_2026": "aime_2026",
    "mmlu": "mmlu",
    "mmlu_pro": "mmlu_pro",
    "gpqa": "gpqa",
    "global_mmlu": "global_mmlu",
    "mmmlu": "mmmlu",
    "hle": "hle",
    "livecodebench": "livecodebench",
    "arxivmath": "arxivmath",
    "swe_bench_verified": "swe_bench",
    "swe_bench_multilingual": "swe_bench",
    "swe_bench_pro": "swe_bench",
}


def _all_dataset_ids() -> list[str]:
    """Return sorted config dataset ids for usage messages."""
    config = load_config()
    ids: list[str] = []
    for datasets in config.categories.values():
        ids.extend(entry.id for entry in datasets)
    return sorted(ids)


def _truncate_value(value: Any, max_len: int = MAX_VALUE_LEN) -> Any:
    """Truncate large scalar values for terminal display."""
    if isinstance(value, str):
        if len(value) <= max_len:
            return value
        return f"{value[:max_len]}... [{len(value)} chars]"
    if isinstance(value, (list, tuple)):
        text = json.dumps(value, default=str)
        if len(text) <= max_len:
            return value
        return f"{type(value).__name__} len={len(value)} preview={text[:max_len]}..."
    if isinstance(value, dict):
        text = json.dumps(value, default=str)
        if len(text) <= max_len:
            return value
        keys_preview = list(value.keys())[:5]
        return f"dict keys={keys_preview}... [{len(value)} keys]"
    text = str(value)
    if len(text) <= max_len:
        return value
    return f"{text[:max_len]}... [{len(text)} chars]"


def _format_sample_row(row: pd.Series) -> dict[str, Any]:
    """Build a display-friendly dict for one DataFrame row."""
    return {col: _truncate_value(row[col]) for col in row.index}


def inspect_dataset(dataset_id: str) -> int:
    """Load a dataset and print schema summary to stdout.

    Args:
        dataset_id: Config entry id (e.g. ``mmlu``, ``livecodebench_v6``).

    Returns:
        Process exit code (0 on success, 1 on error).
    """
    config = load_config()
    entry = get_dataset_by_id(config, dataset_id)
    if entry is None:
        valid = ", ".join(_all_dataset_ids())
        print(f"Unknown dataset_id: {dataset_id}", file=sys.stderr)
        print(f"Valid ids: {valid}", file=sys.stderr)
        return 1

    try:
        descriptor = get_descriptor(dataset_id)
    except ValueError:
        print(f"No API descriptor registered for '{dataset_id}'", file=sys.stderr)
        return 1

    df, _extras = descriptor.loader({})
    cache_key = LOADER_CACHE_KEYS.get(entry.loader, entry.loader)
    path = cache_dir(cache_key)

    print(f"Dataset: {entry.label} ({dataset_id})")
    print(f"Loader: {entry.loader}")
    print(f"Rows: {len(df):,}")
    print(f"Columns ({len(df.columns)}): {list(df.columns)}")
    print("\nDtypes:")
    for col, dtype in df.dtypes.items():
        print(f"  {col}: {dtype}")
    print(f"\nCache path: {path}")
    if len(df) > 0:
        print("\nSample row (index 0, truncated):")
        for key, val in _format_sample_row(df.iloc[0]).items():
            print(f"  {key}: {val}")
    else:
        print("\nSample row: (empty DataFrame)")
    return 0


def main() -> None:
    """Parse CLI args and run dataset inspection."""
    parser = argparse.ArgumentParser(
        description="Inspect columns, dtypes, row count, and a sample row for a dataset."
    )
    parser.add_argument(
        "dataset_id",
        help="Dataset id from config/datasets.yaml (e.g. mmlu, livecodebench_v6)",
    )
    args = parser.parse_args()
    raise SystemExit(inspect_dataset(args.dataset_id))


if __name__ == "__main__":
    main()
