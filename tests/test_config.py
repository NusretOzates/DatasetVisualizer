"""Tests for configuration loading and validation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from dataset_visualizer.config import AppConfig, DatasetEntry, load_config


def test_load_config_reads_project_yaml() -> None:
    config = load_config()
    assert "knowledge" in config.categories
    assert any(ds.id == "mmlu" for ds in config.categories["knowledge"])


def test_dataset_entry_requires_core_fields() -> None:
    with pytest.raises(ValidationError):
        DatasetEntry.model_validate({"id": "", "label": "X", "loader": "x", "description": "Test."})


def test_dataset_entry_requires_description() -> None:
    with pytest.raises(ValidationError):
        DatasetEntry.model_validate({"id": "x", "label": "X", "loader": "x"})


def test_all_config_datasets_have_descriptions() -> None:
    config = load_config()
    for datasets in config.categories.values():
        for entry in datasets:
            assert entry.description.strip()


def test_dataset_entry_accepts_optional_row_count() -> None:
    entry = DatasetEntry.model_validate(
        {
            "id": "gpqa_diamond",
            "label": "GPQA Diamond",
            "loader": "gpqa",
            "description": "Graduate-level science MCQ benchmark.",
            "row_count": 198,
        }
    )
    assert entry.row_count == 198


def test_dataset_entry_rejects_negative_row_count() -> None:
    with pytest.raises(ValidationError):
        DatasetEntry.model_validate(
            {
                "id": "gpqa_diamond",
                "label": "GPQA Diamond",
                "loader": "gpqa",
                "description": "Graduate-level science MCQ benchmark.",
                "row_count": -1,
            }
        )


def test_dataset_entry_rejects_boolean_row_count() -> None:
    with pytest.raises(ValidationError):
        DatasetEntry.model_validate(
            {
                "id": "gpqa_diamond",
                "label": "GPQA Diamond",
                "loader": "gpqa",
                "description": "Graduate-level science MCQ benchmark.",
                "row_count": True,
            }
        )


def test_duplicate_dataset_ids_rejected(tmp_path: Path) -> None:
    data = {
        "categories": {
            "reasoning": [
                {"id": "dup", "label": "A", "loader": "a", "description": "First."},
                {"id": "dup", "label": "B", "loader": "b", "description": "Second."},
            ]
        }
    }
    path = tmp_path / "datasets.yaml"
    path.write_text(yaml.dump(data), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_config(path)


def test_empty_category_key_rejected() -> None:
    with pytest.raises(ValidationError):
        AppConfig.model_validate(
            {"categories": {"": [{"id": "x", "label": "X", "loader": "x", "description": "Test."}]}}
        )
