"""τ³-Bench task loader (sierra-research/tau2-bench on GitHub)."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError
from urllib.request import urlopen

import pandas as pd

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache

TAU3_BENCH_GITHUB_REPO = "sierra-research/tau2-bench"
TAU3_BENCH_BRANCH = "main"
TAU3_BENCH_RAW_BASE = (
    f"https://raw.githubusercontent.com/{TAU3_BENCH_GITHUB_REPO}/{TAU3_BENCH_BRANCH}"
    "/data/tau2/domains"
)
TAU3_DOMAINS = ("airline", "retail", "telecom", "banking_knowledge")
DEFAULT_TASK_SPLIT = "base"


def _fetch_json(relative_path: str) -> Any:
    """Download and cache a JSON file from the upstream τ³-bench repository."""
    cache_root = cache_dir("tau3_bench")
    cache_path = cache_root / relative_path.replace("/", "__")
    if cache_path.is_file():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    url = f"{TAU3_BENCH_RAW_BASE}/{relative_path}"
    try:
        with urlopen(url, timeout=60) as response:
            payload = json.load(response)
    except HTTPError as exc:
        msg = f"Failed to download τ³-Bench file {relative_path}: HTTP {exc.code}"
        raise RuntimeError(msg) from exc

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def _task_description_text(description: object) -> str:
    """Extract human-readable purpose text from a task description object."""
    if isinstance(description, dict):
        purpose = description.get("purpose")
        if purpose:
            return str(purpose).strip()
        notes = description.get("notes")
        if notes:
            return str(notes).strip()
        return ""
    if description is None:
        return ""
    return str(description).strip()


def _scenario_fields(user_scenario: object) -> dict[str, str]:
    """Flatten nested user-scenario payloads into string columns."""
    empty = {
        "persona": "",
        "reason_for_call": "",
        "task_instructions": "",
        "known_info": "",
        "unknown_info": "",
    }
    if user_scenario is None:
        return empty
    if isinstance(user_scenario, str):
        return {**empty, "task_instructions": user_scenario.strip()}
    if not isinstance(user_scenario, dict):
        return empty

    persona = str(user_scenario.get("persona") or "").strip()
    instructions = user_scenario.get("instructions")
    if isinstance(instructions, str):
        return {**empty, "persona": persona, "task_instructions": instructions.strip()}
    if not isinstance(instructions, dict):
        return {**empty, "persona": persona}

    return {
        "persona": persona,
        "reason_for_call": str(instructions.get("reason_for_call") or "").strip(),
        "task_instructions": str(instructions.get("task_instructions") or "").strip(),
        "known_info": str(instructions.get("known_info") or "").strip(),
        "unknown_info": str(instructions.get("unknown_info") or "").strip(),
    }


def _evaluation_action_count(evaluation_criteria: object) -> int:
    """Count expected actions in evaluation criteria when present."""
    if not isinstance(evaluation_criteria, dict):
        return 0
    actions = evaluation_criteria.get("actions")
    if not isinstance(actions, list):
        return 0
    return len(actions)


def _domain_task_ids(domain: str, task_split: str) -> list[str] | None:
    """Return task ids for a domain split, or None when the domain uses all tasks."""
    if domain == "banking_knowledge":
        return None
    relative = f"{domain}/split_tasks.json"
    splits = _fetch_json(relative)
    if not isinstance(splits, dict):
        msg = f"Unexpected split_tasks payload for {domain}"
        raise RuntimeError(msg)
    task_ids = splits.get(task_split)
    if task_ids is None:
        available = ", ".join(sorted(splits))
        msg = f"Unknown task split {task_split!r} for {domain}; available: {available}"
        raise ValueError(msg)
    return [str(task_id) for task_id in task_ids]


def _load_domain_tasks(domain: str, task_split: str) -> list[dict[str, Any]]:
    """Load and filter tasks for one τ³-bench domain."""
    tasks = _fetch_json(f"{domain}/tasks.json")
    if not isinstance(tasks, list):
        msg = f"Unexpected tasks.json payload for {domain}"
        raise RuntimeError(msg)

    by_id = {str(task.get("id")): task for task in tasks if isinstance(task, dict)}
    selected_ids = _domain_task_ids(domain, task_split)
    if selected_ids is None:
        selected_ids = list(by_id)

    rows: list[dict[str, Any]] = []
    for task_id in selected_ids:
        task = by_id.get(task_id)
        if task is None:
            continue
        scenario = _scenario_fields(task.get("user_scenario"))
        purpose = _task_description_text(task.get("description"))
        rows.append(
            {
                "task_id": task_id,
                "instance_id": f"{domain}-{task_id}",
                "domain": domain,
                "task_split": task_split,
                "purpose": purpose,
                "reason_for_call": scenario["reason_for_call"],
                "task_instructions": scenario["task_instructions"],
                "known_info": scenario["known_info"],
                "unknown_info": scenario["unknown_info"],
                "persona": scenario["persona"],
                "purpose_preview": (purpose or scenario["reason_for_call"] or task_id)[:120],
                "evaluation_action_count": _evaluation_action_count(
                    task.get("evaluation_criteria")
                ),
                "has_ticket": bool(task.get("ticket")),
                "evaluation_criteria": task.get("evaluation_criteria"),
                "initial_state": task.get("initial_state"),
                "ticket": task.get("ticket"),
                "annotations": task.get("annotations"),
            }
        )
    return rows


def _normalize_tau3_bench_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure stable dtypes for overview filters and the sample viewer."""
    normalized = df.copy()
    normalized["evaluation_action_count"] = (
        normalized["evaluation_action_count"].fillna(0).astype(int)
    )
    normalized["has_ticket"] = normalized["has_ticket"].fillna(False).astype(bool)
    return normalized


@loader_cache(show_spinner="Downloading τ³-Bench tasks from GitHub …")
def load_tau3_bench(task_split: str = DEFAULT_TASK_SPLIT) -> pd.DataFrame:
    """Load τ³-bench customer-service agent tasks from the upstream GitHub repo.

    Args:
        task_split: Task subset name from ``split_tasks.json`` (``base``, ``train``, or
            ``test``). Banking knowledge always loads all tasks.

    Returns:
        Normalized task DataFrame across airline, retail, telecom, and banking domains.
    """
    cache_dir("tau3_bench")
    rows: list[dict[str, Any]] = []
    for domain in TAU3_DOMAINS:
        rows.extend(_load_domain_tasks(domain, task_split))
    if not rows:
        msg = f"No τ³-Bench tasks found for split {task_split!r}"
        raise RuntimeError(msg)
    return _normalize_tau3_bench_frame(pd.DataFrame(rows))
