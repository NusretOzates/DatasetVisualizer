"""Tests for per-dataset upstream evaluation methodology metadata."""

from __future__ import annotations

import pytest

from dataset_visualizer.api.service import get_dataset_meta
from dataset_visualizer.config import (
    get_evaluation_for_dataset,
    load_config,
    load_evaluation_methods,
)


def _catalog_ids() -> list[str]:
    config = load_config()
    return [entry.id for datasets in config.categories.values() for entry in datasets]


def test_every_catalog_dataset_has_evaluation_methodology() -> None:
    data = load_evaluation_methods()
    methods = data.get("methods", {})
    datasets = data.get("datasets", {})

    assert methods
    for dataset_id in _catalog_ids():
        assert dataset_id in datasets, f"missing evaluation entry for {dataset_id}"
        entry = datasets[dataset_id]
        assert entry["method"] in methods, f"unknown method for {dataset_id}"
        assert len(entry["summary"].strip()) >= 40, f"summary too short for {dataset_id}"


def test_no_evaluation_entries_for_unknown_datasets() -> None:
    datasets = load_evaluation_methods().get("datasets", {})
    assert set(datasets) == set(_catalog_ids())


def test_get_evaluation_for_dataset_resolves_label() -> None:
    evaluation = get_evaluation_for_dataset("mmlu")
    assert evaluation is not None
    assert evaluation["method"] == "multiple_choice"
    assert evaluation["method_label"] == "Multiple-choice exact match"
    assert "accuracy" in evaluation["summary"]


def test_get_evaluation_for_unknown_dataset_returns_none() -> None:
    assert get_evaluation_for_dataset("does_not_exist") is None


def test_dataset_meta_exposes_evaluation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("dataset_visualizer.api.service.get_dataset_readme", lambda _dataset_id: "")
    meta = get_dataset_meta("swe_bench_verified")
    assert meta["evaluation"]["method"] == "code_execution"
    assert "FAIL_TO_PASS" in meta["evaluation"]["summary"]
