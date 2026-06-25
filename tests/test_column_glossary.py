"""Tests for column glossary loading."""

from __future__ import annotations

from pathlib import Path

import yaml

from dataset_visualizer.config import get_column_glossary_for_dataset, load_column_glossary


def test_load_column_glossary_missing_file(tmp_path: Path) -> None:
    assert load_column_glossary(tmp_path / "missing.yaml") == {}


def test_get_column_glossary_for_dataset(tmp_path: Path) -> None:
    glossary_path = tmp_path / "column_glossary.yaml"
    glossary_path.write_text(
        yaml.dump(
            {
                "datasets": {
                    "mmlu": {
                        "label": "MMLU",
                        "columns": {
                            "question": "Multiple-choice question text.",
                            "choices": "Answer options.",
                        },
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    columns = get_column_glossary_for_dataset("mmlu", glossary_path)
    assert columns["question"] == "Multiple-choice question text."
    assert get_column_glossary_for_dataset("missing", glossary_path) == {}
