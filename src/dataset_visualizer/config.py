"""Load and validate application configuration from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "datasets.yaml"
DEFAULT_GLOSSARY_PATH = Path(__file__).resolve().parents[2] / "config" / "column_glossary.yaml"


class DatasetEntry(BaseModel):
    """Metadata for a single dataset registered in the app."""

    id: str
    label: str
    loader: str
    description: str
    icon: str | None = None
    archetype: str | None = None
    hf_id: str | None = None
    hf_repo: str | None = None
    files: list[str] | None = None
    problems_hf_id: str | None = None
    outputs_hf_id: str | None = None
    license: str | None = None
    docs: str | None = None
    row_count: int | None = None
    hf_config: str | None = None
    split: str | None = None  # when set, load this Hub split; otherwise auto-pick smallest
    profile: str | None = None
    id_column: str | None = None
    viewer: str | None = None
    source_file: str | None = None
    multi_config: bool = False
    exclude_configs: list[str] = Field(default_factory=list)

    @field_validator("row_count", mode="before")
    @classmethod
    def _non_negative_row_count(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, bool):
            msg = "row_count must be a non-negative integer, not a boolean."
            raise ValueError(msg)
        if not isinstance(value, int):
            msg = "row_count must be a non-negative integer."
            raise ValueError(msg)
        if value < 0:
            msg = "row_count must be non-negative."
            raise ValueError(msg)
        return value

    @field_validator("id", "label", "loader", "description")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "Dataset entry fields id, label, loader, and description must be non-empty."
            raise ValueError(msg)
        return value


class AppConfig(BaseModel):
    """Top-level application configuration."""

    categories: dict[str, list[DatasetEntry]] = Field(default_factory=dict)

    @field_validator("categories")
    @classmethod
    def _validate_categories(
        cls, value: dict[str, list[DatasetEntry]]
    ) -> dict[str, list[DatasetEntry]]:
        seen_ids: set[str] = set()
        for category, datasets in value.items():
            if not category.strip():
                msg = "Category keys must be non-empty."
                raise ValueError(msg)
            for entry in datasets:
                if entry.id in seen_ids:
                    msg = f"Duplicate dataset id: {entry.id}"
                    raise ValueError(msg)
                seen_ids.add(entry.id)
        return value


def load_config(path: Path | None = None) -> AppConfig:
    """Load and validate datasets configuration from YAML.

    Args:
        path: Path to datasets.yaml. Defaults to the project config file.

    Returns:
        Validated AppConfig instance.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValidationError: If the YAML does not satisfy the schema.
    """
    config_path = path or DEFAULT_CONFIG_PATH
    if not config_path.exists():
        msg = f"Config file not found: {config_path}"
        raise FileNotFoundError(msg)

    raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return AppConfig.model_validate(raw)


def get_dataset_by_id(config: AppConfig, dataset_id: str) -> DatasetEntry | None:
    """Look up a dataset entry by its id across all categories."""
    for datasets in config.categories.values():
        for entry in datasets:
            if entry.id == dataset_id:
                return entry
    return None


def load_column_glossary(path: Path | None = None) -> dict[str, Any]:
    """Load the column glossary YAML keyed by dataset id.

    Returns:
        Mapping of dataset id to glossary entry with a ``columns`` dict.
        Empty dict when the glossary file is missing.
    """
    glossary_path = path or DEFAULT_GLOSSARY_PATH
    if not glossary_path.exists():
        return {}
    raw: dict[str, Any] = yaml.safe_load(glossary_path.read_text(encoding="utf-8"))
    datasets = raw.get("datasets", {})
    if not isinstance(datasets, dict):
        return {}
    return datasets


def get_column_glossary_for_dataset(dataset_id: str, path: Path | None = None) -> dict[str, str]:
    """Return column descriptions for one dataset id."""
    glossary = load_column_glossary(path)
    entry = glossary.get(dataset_id, {})
    columns = entry.get("columns", {}) if isinstance(entry, dict) else {}
    if not isinstance(columns, dict):
        return {}
    return {str(key): str(value) for key, value in columns.items()}
