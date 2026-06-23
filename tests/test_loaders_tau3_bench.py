"""Tests for τ³-Bench GitHub loader."""

from __future__ import annotations

import pandas as pd
import pytest

from dataset_visualizer.loaders import tau3_bench as tau3_module
from dataset_visualizer.loaders.tau3_bench import (
    _evaluation_action_count,
    _normalize_tau3_bench_frame,
    _scenario_fields,
    _task_description_text,
    load_tau3_bench,
)

SAMPLE_AIRLINE_TASK = {
    "id": "0",
    "description": {
        "purpose": "Test cancellation policy enforcement.",
        "relevant_policies": None,
        "notes": None,
    },
    "user_scenario": {
        "persona": "Frustrated traveler",
        "instructions": {
            "domain": "airline",
            "reason_for_call": "Cancel reservation EHGLP3.",
            "known_info": "Booked yesterday.",
            "unknown_info": None,
            "task_instructions": "Insist on a refund.",
        },
    },
    "initial_state": None,
    "evaluation_criteria": {
        "actions": [{"name": "lookup_reservation"}, {"name": "deny_cancel"}],
    },
}

SAMPLE_BANKING_TASK = {
    "id": "task_001",
    "description": {
        "purpose": "Pick the best cash-back card.",
        "relevant_policies": None,
        "notes": None,
    },
    "user_scenario": "You want the highest cash-back card with no annual fee.",
    "evaluation_criteria": {"actions": []},
}


def test_task_description_text_reads_purpose() -> None:
    assert _task_description_text(SAMPLE_AIRLINE_TASK["description"]) == (
        "Test cancellation policy enforcement."
    )


def test_scenario_fields_supports_nested_and_string_payloads() -> None:
    nested = _scenario_fields(SAMPLE_AIRLINE_TASK["user_scenario"])
    assert nested["reason_for_call"] == "Cancel reservation EHGLP3."
    assert nested["task_instructions"] == "Insist on a refund."

    flat = _scenario_fields(SAMPLE_BANKING_TASK["user_scenario"])
    assert "cash-back" in flat["task_instructions"]


def test_evaluation_action_count() -> None:
    assert _evaluation_action_count(SAMPLE_AIRLINE_TASK["evaluation_criteria"]) == 2
    assert _evaluation_action_count(None) == 0


def test_normalize_tau3_bench_frame_casts_counts() -> None:
    raw = pd.DataFrame(
        [
            {
                "evaluation_action_count": None,
                "has_ticket": None,
            }
        ]
    )
    df = _normalize_tau3_bench_frame(raw)
    assert df.loc[0, "evaluation_action_count"] == 0
    assert bool(df.loc[0, "has_ticket"]) is False


def test_load_tau3_bench_uses_github_payloads(monkeypatch: pytest.MonkeyPatch) -> None:
    payloads = {
        "airline/tasks.json": [SAMPLE_AIRLINE_TASK],
        "airline/split_tasks.json": {"base": ["0"], "train": [], "test": []},
        "retail/tasks.json": [],
        "retail/split_tasks.json": {"base": [], "train": [], "test": []},
        "telecom/tasks.json": [],
        "telecom/split_tasks.json": {"base": [], "train": [], "test": []},
        "banking_knowledge/tasks.json": [SAMPLE_BANKING_TASK],
    }

    def _mock_fetch(relative_path: str) -> object:
        return payloads[relative_path]

    monkeypatch.setattr(tau3_module, "_fetch_json", _mock_fetch)
    load_tau3_bench.clear()

    df = load_tau3_bench(task_split="base")
    assert len(df) == 2
    assert set(df["domain"]) == {"airline", "banking_knowledge"}
    assert df.loc[df["domain"] == "airline", "instance_id"].iloc[0] == "airline-0"
    assert df.loc[df["domain"] == "airline", "evaluation_action_count"].iloc[0] == 2
