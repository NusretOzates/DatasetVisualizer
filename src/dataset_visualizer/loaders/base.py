"""Shared loader utilities."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def cache_dir(dataset_id: str) -> Path:
    """Return the on-disk cache directory for a dataset, creating it if needed."""
    path = PROJECT_ROOT / "data" / "cache" / dataset_id
    path.mkdir(parents=True, exist_ok=True)
    return path
