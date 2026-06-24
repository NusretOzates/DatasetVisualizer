"""Build column glossary from Hugging Face READMEs and local docs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml
from huggingface_hub import hf_hub_download

from dataset_visualizer.config import DatasetEntry, load_config

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "config" / "column_glossary.yaml"
DOCS_DATASETS = ROOT / "docs" / "datasets"


def _hub_repo(entry: DatasetEntry) -> str | None:
    """Resolve the Hugging Face repo id for README fetch."""
    return entry.hf_id or entry.hf_repo or entry.problems_hf_id


def _fetch_readme(repo_id: str) -> str:
    """Download dataset README from the Hub."""
    try:
        path = hf_hub_download(repo_id, "README.md", repo_type="dataset")
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _parse_readme_table(readme: str) -> dict[str, str]:
    """Extract column descriptions from markdown tables in a README."""
    glossary: dict[str, str] = {}
    for line in readme.splitlines():
        if "|" not in line or line.strip().startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        key = cells[0].strip("`").strip()
        if not key or key.lower() in {"field", "column", "name", "feature"}:
            continue
        description = cells[1].strip()
        if description and not description.startswith("---"):
            glossary[key] = description
    return glossary


def _parse_readme_bullets(readme: str) -> dict[str, str]:
    """Extract `column`: description bullets from README prose."""
    glossary: dict[str, str] = {}
    for match in re.finditer(
        r"(?:^|\n)\s*[-*]?\s*`?([A-Za-z_][\w]*)`?\s*[:：]\s*(.+?)(?=\n\s*[-*]|\n\n|$)",
        readme,
        flags=re.MULTILINE,
    ):
        key, description = match.group(1), match.group(2).strip()
        if len(description) > 20:
            glossary[key] = description
    return glossary


def _load_local_docs(entry: DatasetEntry) -> dict[str, str]:
    """Load column hints from docs/datasets/<id>.md if present."""
    path = DOCS_DATASETS / f"{entry.id}.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    return _parse_readme_bullets(text)


def _profile_fallback(entry: DatasetEntry) -> dict[str, str]:
    """Minimal fallback descriptions from archetype/profile."""
    profile = entry.profile or entry.archetype or "generic"
    common: dict[str, dict[str, str]] = {
        "mcq": {
            "question": "Multiple-choice question text.",
            "choices": "Answer options for the question.",
            "answer_letter": "Correct option letter (A, B, C, …).",
            "subject": "Benchmark subject or category label.",
        },
        "code_eval": {
            "prompt": "Coding problem prompt or function signature.",
            "canonical_solution": "Reference implementation.",
            "test_code": "Unit tests for the solution.",
        },
        "math_competition": {
            "problem": "Math problem statement.",
            "answer": "Ground-truth answer.",
            "solution": "Worked solution when available.",
        },
        "agent_task": {
            "question": "Task or user query for the agent.",
            "answer": "Expected final answer.",
            "annotator_metadata": "Human annotator notes and tool hints.",
        },
        "instruction": {
            "prompt": "User instruction to evaluate.",
            "kwargs": "Structured constraint parameters for the instruction.",
        },
    }
    archetype = entry.archetype or ""
    if archetype in common:
        return common[archetype]
    if profile in common:
        return common[profile]
    return {
        "sample_id": "Stable row identifier within the loaded split.",
        "question": "Primary task text or prompt.",
        "answer": "Reference answer when available.",
    }


def build_glossary() -> dict[str, Any]:
    """Build the full column glossary keyed by dataset id."""
    config = load_config()
    glossary: dict[str, Any] = {}
    for datasets in config.categories.values():
        for entry in datasets:
            columns: dict[str, str] = {}
            repo = _hub_repo(entry)
            if repo:
                readme = _fetch_readme(repo)
                columns.update(_parse_readme_bullets(readme))
                columns.update(_parse_readme_table(readme))
            columns.update(_load_local_docs(entry))
            fallback = _profile_fallback(entry)
            for key, description in fallback.items():
                columns.setdefault(key, description)
            glossary[entry.id] = {
                "label": entry.label,
                "hf_id": repo,
                "columns": dict(sorted(columns.items())),
            }
    return glossary


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Output YAML path",
    )
    args = parser.parse_args()
    glossary = build_glossary()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.dump({"datasets": glossary}, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Wrote {args.output} ({len(glossary)} datasets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
