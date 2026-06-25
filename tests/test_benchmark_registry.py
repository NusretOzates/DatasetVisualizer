"""Registry tests for per-dataset dedicated viewers."""

from __future__ import annotations

from dataset_visualizer.api.dataset_registry import DATASET_REGISTRY, build_dataset_registry
from dataset_visualizer.config import load_config

FORBIDDEN_VIEWERS = {"generic", "agent_task", "mcq", "mcq_cot", "code_eval", "arc_grid"}


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


def test_every_dataset_has_dedicated_viewer() -> None:
    """Every catalog entry must expose viewer equal to its dataset id."""
    config = load_config()
    for datasets in config.categories.values():
        for entry in datasets:
            descriptor = DATASET_REGISTRY[entry.id]
            assert descriptor.viewer == entry.id, (
                f"{entry.id}: expected viewer={entry.id}, got {descriptor.viewer}"
            )
            assert descriptor.viewer not in FORBIDDEN_VIEWERS, (
                f"{entry.id} must not route to shared viewer key {descriptor.viewer}"
            )
            assert entry.viewer == entry.id, f"{entry.id} config viewer must equal dataset id"


def test_manual_and_hf_descriptors_use_dataset_id_viewer() -> None:
    for dataset_id, descriptor in DATASET_REGISTRY.items():
        assert descriptor.viewer == dataset_id, (
            f"{dataset_id}: registry viewer must equal dataset id"
        )
