"""Tests for dataset source link resolution."""

from __future__ import annotations

from dataset_visualizer.config import DatasetEntry
from dataset_visualizer.source_links import resolve_source_link, source_link_payload


def _entry(**overrides: object) -> DatasetEntry:
    data = {
        "id": "example",
        "label": "Example",
        "loader": "hf_benchmark",
        "description": "Example dataset.",
    }
    data.update(overrides)
    return DatasetEntry.model_validate(data)


def test_resolve_source_link_prefers_hf_id() -> None:
    link = resolve_source_link(_entry(hf_id="cais/mmlu"))
    assert link is not None
    assert link.url == "https://huggingface.co/datasets/cais/mmlu"
    assert link.label == "cais/mmlu"
    assert link.kind == "huggingface"


def test_resolve_source_link_uses_hf_repo_when_hf_id_missing() -> None:
    link = resolve_source_link(
        _entry(
            id="livecodebench_v6",
            loader="livecodebench",
            hf_repo="livecodebench/code_generation_lite",
        )
    )
    assert link is not None
    assert link.url == "https://huggingface.co/datasets/livecodebench/code_generation_lite"


def test_resolve_source_link_uses_problems_hf_id_for_multi_repo_datasets() -> None:
    link = resolve_source_link(
        _entry(
            id="arxivmath_0526",
            loader="arxivmath",
            problems_hf_id="MathArena/arxivmath-0526",
            outputs_hf_id="MathArena/arxivmath-0526_outputs",
        )
    )
    assert link is not None
    assert link.label == "MathArena/arxivmath-0526"


def test_resolve_source_link_falls_back_to_github_for_tau3_bench() -> None:
    link = resolve_source_link(
        _entry(
            id="tau3_bench",
            loader="tau3_bench",
            docs="docs/datasets/tau3_bench.md",
        )
    )
    assert link is not None
    assert link.kind == "github"
    assert link.url == "https://github.com/sierra-research/tau2-bench"


def test_resolve_source_link_accepts_http_docs_url() -> None:
    link = resolve_source_link(
        _entry(
            loader="custom",
            docs="https://example.com/benchmark",
        )
    )
    assert link is not None
    assert link.kind == "web"
    assert link.url == "https://example.com/benchmark"


def test_source_link_payload_returns_none_when_unresolved() -> None:
    assert source_link_payload(_entry(loader="custom")) is None
