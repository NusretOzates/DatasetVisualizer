"""Registry alignment tests for catalog benchmarks."""

from __future__ import annotations

from dataset_visualizer.api.dataset_registry import DATASET_REGISTRY, build_dataset_registry
from dataset_visualizer.config import load_config


def test_catalog_entries_registered() -> None:
    config = load_config()
    catalog_ids = {
        entry.id
        for datasets in config.categories.values()
        for entry in datasets
        if entry.loader == "hf_benchmark"
    }
    assert catalog_ids
    assert catalog_ids.issubset(DATASET_REGISTRY.keys())


def test_build_dataset_registry_is_idempotent() -> None:
    first = build_dataset_registry()
    second = build_dataset_registry()
    assert set(first.keys()) == set(second.keys())


def test_hf_benchmark_entries_get_reusable_filters() -> None:
    descriptor = DATASET_REGISTRY["mmlu_redux"]
    filter_names = {filter_spec["name"] for filter_spec in descriptor.filters}
    assert "subjects" in filter_names
    assert "categories" in filter_names


def test_arc_agi_uses_grid_viewer() -> None:
    assert DATASET_REGISTRY["arc_agi_2"].viewer == "arc_grid"
