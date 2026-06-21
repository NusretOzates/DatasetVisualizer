"""Tests for configuration loading and validation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from dataset_visualizer.config import AppConfig, DatasetEntry, load_config


def test_load_config_reads_project_yaml() -> None:
    config = load_config()
    assert "reasoning" in config.categories
    assert any(ds.id == "mmlu" for ds in config.categories["reasoning"])


def test_dataset_entry_requires_core_fields() -> None:
    with pytest.raises(ValidationError):
        DatasetEntry.model_validate({"id": "", "label": "X", "loader": "x"})


def test_duplicate_dataset_ids_rejected(tmp_path: Path) -> None:
    data = {
        "categories": {
            "reasoning": [
                {"id": "dup", "label": "A", "loader": "a"},
                {"id": "dup", "label": "B", "loader": "b"},
            ]
        }
    }
    path = tmp_path / "datasets.yaml"
    path.write_text(yaml.dump(data), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_config(path)


def test_empty_category_key_rejected() -> None:
    with pytest.raises(ValidationError):
        AppConfig.model_validate({"categories": {"": [{"id": "x", "label": "X", "loader": "x"}]}})
