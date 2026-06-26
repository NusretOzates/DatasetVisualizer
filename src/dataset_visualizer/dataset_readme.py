"""Load Hugging Face dataset README content for overview pages."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from huggingface_hub import hf_hub_download

from dataset_visualizer.config import get_dataset_by_id, load_config

DOCS_DATASETS = Path(__file__).resolve().parents[2] / "docs" / "datasets"


def _strip_yaml_frontmatter(text: str) -> str:
    """Remove leading YAML metadata block from Hub README files."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + 5 :].lstrip("\n")


def _hub_repo_id(entry: object) -> str | None:
    """Resolve the Hugging Face repo id for README fetch."""
    return getattr(entry, "hf_id", None) or getattr(entry, "hf_repo", None) or getattr(
        entry, "problems_hf_id", None
    )


@lru_cache(maxsize=128)
def _fetch_hub_readme(repo_id: str) -> str:
    """Download and cache a dataset README from the Hub."""
    try:
        path = hf_hub_download(repo_id, "README.md", repo_type="dataset")
        return _strip_yaml_frontmatter(Path(path).read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return ""


def get_dataset_readme(dataset_id: str) -> str:
    """Return markdown README text for a catalog dataset id."""
    entry = get_dataset_by_id(load_config(), dataset_id)
    if entry is None:
        return ""

    repo = _hub_repo_id(entry)
    if repo:
        readme = _fetch_hub_readme(repo)
        if readme.strip():
            return readme

    local_path = DOCS_DATASETS / f"{dataset_id}.md"
    if local_path.exists():
        return local_path.read_text(encoding="utf-8", errors="replace")
    return ""
