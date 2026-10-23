"""Terminal-Bench 2.1 loader (harbor-framework/terminal-bench-2-1 on GitHub)."""

from __future__ import annotations

import io
import tomllib
import zipfile
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import urlopen

import pandas as pd

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache

TERMINAL_BENCH_GITHUB_REPO = "harbor-framework/terminal-bench-2-1"
TERMINAL_BENCH_BRANCH = "main"
TERMINAL_BENCH_ZIP_URL = (
    f"https://github.com/{TERMINAL_BENCH_GITHUB_REPO}/archive/refs/heads/"
    f"{TERMINAL_BENCH_BRANCH}.zip"
)
EXTRACTED_DIR_NAME = f"terminal-bench-2-1-{TERMINAL_BENCH_BRANCH}"

TERMINAL_BENCH_40_GITHUB_REPO = "harbor-framework/terminal-bench"
TERMINAL_BENCH_40_REF = "v4.0.0"
TERMINAL_BENCH_SCIENCE_GITHUB_REPO = "harbor-framework/terminal-bench-science"
TERMINAL_BENCH_SCIENCE_REF = "v0.1.0"


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _metadata_value(task_meta: dict[str, Any], key: str) -> str:
    metadata = task_meta.get("metadata")
    if not isinstance(metadata, dict):
        return ""
    value = metadata.get(key)
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def _metadata_hours_as_minutes(task_meta: dict[str, Any], key: str) -> float | None:
    """Convert an ``*_hours`` metadata estimate to minutes, when present."""
    text = _metadata_value(task_meta, key)
    if not text:
        return None
    try:
        return float(text) * 60
    except ValueError:
        return None


def _environment_value(task_meta: dict[str, Any], key: str) -> object:
    environment = task_meta.get("environment")
    if not isinstance(environment, dict):
        return None
    return environment.get(key)


def _parse_task_dir(
    task_dir: Path, tasks_root: Path | None = None, split: str = TERMINAL_BENCH_BRANCH
) -> dict[str, Any] | None:
    """Parse one Terminal-Bench task directory into a normalized row."""
    if not task_dir.is_dir():
        return None
    task_id = task_dir.name
    if task_id.startswith("."):
        return None

    toml_path = task_dir / "task.toml"
    if not toml_path.is_file():
        return None

    task_meta = tomllib.loads(toml_path.read_text(encoding="utf-8"))
    task_section = task_meta.get("task")
    task_name = ""
    description = ""
    if isinstance(task_section, dict):
        task_name = str(task_section.get("name") or "").strip()
        description = str(task_section.get("description") or "").strip()

    instruction = _read_text(task_dir / "instruction.md")
    readme = _read_text(task_dir / "README.md")
    preview_source = instruction or description or task_id

    expert_min = _metadata_value(task_meta, "expert_time_estimate_min")
    junior_min = _metadata_value(task_meta, "junior_time_estimate_min")
    expert_minutes = (
        float(expert_min)
        if expert_min
        else _metadata_hours_as_minutes(task_meta, "expert_time_estimate_hours")
    )
    junior_minutes = (
        float(junior_min)
        if junior_min
        else _metadata_hours_as_minutes(task_meta, "junior_time_estimate_hours")
    )

    allow_internet = _environment_value(task_meta, "allow_internet")
    if allow_internet is None:
        allow_internet = _environment_value(task_meta, "network_mode") == "public"

    task_path = ""
    if tasks_root is not None:
        task_path = task_dir.relative_to(tasks_root).as_posix()

    return {
        "task_id": task_id,
        "instance_id": task_id,
        "task_name": task_name,
        "description": description,
        "instruction": instruction,
        "instruction_preview": preview_source[:120],
        "task_readme": readme,
        "category": _metadata_value(task_meta, "category")
        or _metadata_value(task_meta, "domain"),
        "domain": _metadata_value(task_meta, "domain"),
        "field": _metadata_value(task_meta, "field"),
        "task_path": task_path,
        "difficulty": _metadata_value(task_meta, "difficulty"),
        "author_name": _metadata_value(task_meta, "author_name"),
        "docker_image": str(_environment_value(task_meta, "docker_image") or "").strip(),
        "allow_internet": bool(allow_internet),
        "cpus": _environment_value(task_meta, "cpus"),
        "memory_mb": _environment_value(task_meta, "memory_mb"),
        "expert_time_estimate_min": expert_minutes,
        "junior_time_estimate_min": junior_minutes,
        "split": split,
    }


def _tasks_root(cache_root: Path) -> Path:
    return cache_root / EXTRACTED_DIR_NAME / "tasks"


def _download_tasks_archive(cache_root: Path) -> Path:
    """Download and extract the upstream Terminal-Bench repository archive."""
    tasks_root = _tasks_root(cache_root)
    marker = cache_root / ".extracted"
    if marker.is_file() and tasks_root.is_dir():
        return tasks_root

    cache_root.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(TERMINAL_BENCH_ZIP_URL, timeout=180) as response:
            archive_bytes = response.read()
    except HTTPError as exc:
        msg = f"Failed to download Terminal-Bench archive: HTTP {exc.code}"
        raise RuntimeError(msg) from exc

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        archive.extractall(cache_root)

    if not tasks_root.is_dir():
        msg = f"Terminal-Bench archive missing tasks directory at {tasks_root}"
        raise RuntimeError(msg)

    marker.write_text("ok", encoding="utf-8")
    return tasks_root


def _load_rows_from_tasks_root(tasks_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_dir in sorted(tasks_root.iterdir()):
        if not task_dir.is_dir() or task_dir.name == "README.md":
            continue
        row = _parse_task_dir(task_dir)
        if row is not None:
            rows.append(row)
    return rows


def _github_tag_zip_url(repo: str, ref: str) -> str:
    return f"https://github.com/{repo}/archive/refs/tags/{ref}.zip"


def _extracted_dir_name_for_tag(repo: str, ref: str) -> str:
    repo_name = repo.rsplit("/", 1)[-1]
    return f"{repo_name}-{ref.removeprefix('v')}"


def _download_repo_tasks_archive(
    cache_root: Path, zip_url: str, extracted_dir_name: str
) -> Path:
    """Download and extract a Harbor-format GitHub repository archive."""
    tasks_root = cache_root / extracted_dir_name / "tasks"
    marker = cache_root / ".extracted"
    if marker.is_file() and tasks_root.is_dir():
        return tasks_root

    cache_root.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(zip_url, timeout=180) as response:
            archive_bytes = response.read()
    except HTTPError as exc:
        msg = f"Failed to download Terminal-Bench archive: HTTP {exc.code}"
        raise RuntimeError(msg) from exc

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        archive.extractall(cache_root)

    if not tasks_root.is_dir():
        msg = f"Terminal-Bench archive missing tasks directory at {tasks_root}"
        raise RuntimeError(msg)

    marker.write_text("ok", encoding="utf-8")
    return tasks_root


def _load_rows_recursive(tasks_root: Path, split: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for toml_path in sorted(tasks_root.rglob("task.toml")):
        row = _parse_task_dir(toml_path.parent, tasks_root=tasks_root, split=split)
        if row is not None:
            rows.append(row)
    return rows


def _load_terminal_bench_release(repo: str, ref: str, cache_key: str) -> pd.DataFrame:
    """Load a tagged Harbor Terminal-Bench-style release from GitHub."""
    cache_root = cache_dir(cache_key)
    tasks_root = _download_repo_tasks_archive(
        cache_root,
        _github_tag_zip_url(repo, ref),
        _extracted_dir_name_for_tag(repo, ref),
    )
    rows = _load_rows_recursive(tasks_root, split=ref)
    if not rows:
        msg = f"No Terminal-Bench tasks found for {repo}@{ref}"
        raise RuntimeError(msg)
    return _normalize_terminal_bench_frame(pd.DataFrame(rows))


def _normalize_terminal_bench_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Cast stable dtypes for overview filters and the sample viewer."""
    normalized = df.copy()
    for column in ("allow_internet",):
        if column in normalized.columns:
            normalized[column] = normalized[column].fillna(False).astype(bool)
    return normalized


@loader_cache(show_spinner="Downloading Terminal-Bench 4.0 from GitHub …")
def load_terminal_bench_40() -> pd.DataFrame:
    """Load Terminal-Bench 4.0 tasks from the upstream GitHub release.

    Returns:
        Normalized task DataFrame for the 66-task ``v4.0.0`` release.
    """
    return _load_terminal_bench_release(
        TERMINAL_BENCH_40_GITHUB_REPO, TERMINAL_BENCH_40_REF, "terminal_bench_40"
    )


@loader_cache(show_spinner="Downloading Terminal-Bench 2.1 from GitHub …")
def load_terminal_bench_21() -> pd.DataFrame:
    """Load Terminal-Bench 2.1 tasks from the upstream GitHub repository.

    Returns:
        Normalized task DataFrame with instructions and Harbor task metadata.
    """
    cache_root = cache_dir("terminal_bench_21")
    tasks_root = _download_tasks_archive(cache_root)
    rows = _load_rows_from_tasks_root(tasks_root)
    if not rows:
        msg = "No Terminal-Bench tasks found in the downloaded archive"
        raise RuntimeError(msg)
    return _normalize_terminal_bench_frame(pd.DataFrame(rows))
