"""Tests for dataset README loading."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from dataset_visualizer.dataset_readme import (
    _fetch_hub_readme,
    _strip_yaml_frontmatter,
    get_dataset_readme,
)


def test_strip_yaml_frontmatter() -> None:
    raw = "---\nlicense: mit\ntags:\n  - qa\n---\n\n# Title\n\nBody text."
    assert _strip_yaml_frontmatter(raw) == "# Title\n\nBody text."


def test_get_dataset_readme_uses_hub_readme(tmp_path: Path, monkeypatch) -> None:
    _fetch_hub_readme.cache_clear()
    readme_path = tmp_path / "README.md"
    readme_path.write_text("# CommonsenseQA\n\nA benchmark.", encoding="utf-8")

    with patch(
        "dataset_visualizer.dataset_readme.hf_hub_download",
        return_value=str(readme_path),
    ):
        readme = get_dataset_readme("commonsenseqa")

    assert "# CommonsenseQA" in readme
    assert "A benchmark." in readme


def test_get_dataset_readme_falls_back_to_local_docs(tmp_path: Path, monkeypatch) -> None:
    _fetch_hub_readme.cache_clear()
    docs_dir = tmp_path / "datasets"
    docs_dir.mkdir()
    (docs_dir / "tau3_bench.md").write_text("# Tau3 Bench\n\nLocal docs.", encoding="utf-8")
    monkeypatch.setattr("dataset_visualizer.dataset_readme.DOCS_DATASETS", docs_dir)

    with patch(
        "dataset_visualizer.dataset_readme.hf_hub_download",
        side_effect=OSError("missing"),
    ):
        readme = get_dataset_readme("tau3_bench")

    assert readme == "# Tau3 Bench\n\nLocal docs."


def test_get_dataset_readme_unknown_dataset() -> None:
    assert get_dataset_readme("not_a_dataset") == ""
