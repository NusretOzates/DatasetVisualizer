"""Per-dataset API descriptors (single registration point)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from dataset_visualizer.api.overview import (
    overview_aime,
    overview_arxivmath,
    overview_global_mmlu,
    overview_gpqa,
    overview_hle,
    overview_livecodebench,
    overview_mmlu,
    overview_mmlu_pro,
    overview_mmmlu,
    overview_swe_bench,
    overview_tau3_bench,
    sample_extras_aime,
    sample_extras_arxivmath,
)
from dataset_visualizer.loaders.aime_2026 import load_aime_2026
from dataset_visualizer.loaders.arxivmath import load_outputs, load_problems
from dataset_visualizer.loaders.global_mmlu import (
    DEFAULT_LANGUAGE,
    POPULAR_LANGUAGES,
    list_global_mmlu_languages,
    load_global_mmlu,
)
from dataset_visualizer.loaders.gpqa import load_gpqa_diamond
from dataset_visualizer.loaders.hle import load_hle
from dataset_visualizer.loaders.livecodebench import load_livecodebench
from dataset_visualizer.loaders.mmlu import load_mmlu
from dataset_visualizer.loaders.mmlu_pro import load_mmlu_pro
from dataset_visualizer.loaders.mmmlu import (
    DEFAULT_LOCALE,
    LOCALE_LABELS,
    POPULAR_LOCALES,
    list_mmmlu_locales,
    load_mmmlu,
)
from dataset_visualizer.loaders.swe_bench import (
    load_swe_bench_multilingual,
    load_swe_bench_pro,
    load_swe_bench_verified,
)
from dataset_visualizer.loaders.tau3_bench import load_tau3_bench
from dataset_visualizer.api.generic_overview import overview_generic
from dataset_visualizer.config import DatasetEntry, load_config
from dataset_visualizer.loaders.hf_benchmark import make_hf_benchmark_loader

LoaderFn = Callable[[dict[str, Any]], tuple[pd.DataFrame, dict[str, Any]]]
OverviewFn = Callable[[pd.DataFrame, dict[str, Any]], dict[str, Any]]
SampleExtrasFn = Callable[[pd.Series, dict[str, Any]], dict[str, Any]]
ControlsFn = Callable[[], list[dict[str, Any]]]


def _empty_controls() -> list[dict[str, Any]]:
    return []


@dataclass
class DatasetDescriptor:
    """API behaviour for one config dataset id."""

    id_column: str
    viewer: str
    loader: LoaderFn
    overview: OverviewFn
    controls: ControlsFn = _empty_controls
    filters: list[dict[str, Any]] = field(default_factory=list)
    sample_extras: SampleExtrasFn | None = None
    supports_private_tests: bool = False
    cache_key: str | None = None


def _language_options() -> list[str]:
    try:
        return list_global_mmlu_languages()
    except OSError:
        return list(POPULAR_LANGUAGES)


def _locale_options() -> list[str]:
    try:
        return list_mmmlu_locales()
    except OSError:
        return list(POPULAR_LOCALES)


def _format_locale(locale: str) -> str:
    label = LOCALE_LABELS.get(locale, locale)
    return f"{label} ({locale})"


def _controls_mmlu() -> list[dict[str, Any]]:
    return [
        {
            "name": "split",
            "label": "Split",
            "type": "select",
            "options": ["test", "validation", "dev"],
            "default": "test",
        }
    ]


def _controls_mmlu_pro() -> list[dict[str, Any]]:
    return [
        {
            "name": "split",
            "label": "Split",
            "type": "select",
            "options": ["test", "validation"],
            "default": "test",
        }
    ]


def _controls_global_mmlu() -> list[dict[str, Any]]:
    languages = _language_options()
    default = DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in languages else languages[0]
    return [
        {
            "name": "language",
            "label": "Language",
            "type": "select",
            "options": languages,
            "default": default,
        },
        {
            "name": "split",
            "label": "Split",
            "type": "select",
            "options": ["dev", "test"],
            "default": "dev",
        },
    ]


def _controls_mmmlu() -> list[dict[str, Any]]:
    locales = _locale_options()
    default = DEFAULT_LOCALE if DEFAULT_LOCALE in locales else locales[0]
    return [
        {
            "name": "locale",
            "label": "Locale",
            "type": "select",
            "options": locales,
            "labels": {loc: _format_locale(loc) for loc in locales},
            "default": default,
        }
    ]


def _controls_tau3_bench() -> list[dict[str, Any]]:
    return [
        {
            "name": "task_split",
            "label": "Task split",
            "type": "select",
            "options": ["base", "train", "test"],
            "default": "base",
        }
    ]


def _swe_bench_filters(*, include_difficulty: bool, include_language: bool) -> list[dict[str, Any]]:
    filters: list[dict[str, Any]] = [
        {"name": "repos", "label": "Repository", "type": "multiselect", "column": "repo"},
    ]
    if include_difficulty:
        filters.append(
            {"name": "difficulties", "label": "Difficulty", "type": "multiselect", "column": "difficulty"}
        )
    if include_language:
        filters.append(
            {"name": "languages", "label": "Language", "type": "multiselect", "column": "repo_language"}
        )
    return filters


def _descriptor_from_hf_entry(entry: DatasetEntry) -> DatasetDescriptor:
    viewer = entry.viewer or entry.archetype or "generic"
    id_column = entry.id_column or "sample_id"
    return DatasetDescriptor(
        id_column=id_column,
        viewer=viewer,
        loader=lambda params, entry=entry: (make_hf_benchmark_loader(entry)(params), {}),
        overview=overview_generic,
        cache_key=entry.id,
    )


_MANUAL_REGISTRY: dict[str, DatasetDescriptor] = {
    "mmlu": DatasetDescriptor(
        id_column="subject",
        viewer="mcq",
        loader=lambda p: (load_mmlu(split=p.get("split", "test")), {}),
        overview=overview_mmlu,
        controls=_controls_mmlu,
        filters=[{"name": "subjects", "label": "Subject", "type": "multiselect", "column": "subject"}],
    ),
    "mmlu_pro": DatasetDescriptor(
        id_column="question_id",
        viewer="mcq_cot",
        loader=lambda p: (load_mmlu_pro(split=p.get("split", "test")), {}),
        overview=overview_mmlu_pro,
        controls=_controls_mmlu_pro,
        filters=[
            {"name": "categories", "label": "Category", "type": "multiselect", "column": "category"},
            {"name": "src_prefix", "label": "Source prefix", "type": "text", "column": "src"},
        ],
    ),
    "gpqa_diamond": DatasetDescriptor(
        id_column="question",
        viewer="mcq",
        loader=lambda _p: (load_gpqa_diamond(), {}),
        overview=overview_gpqa,
    ),
    "global_mmlu": DatasetDescriptor(
        id_column="sample_id",
        viewer="mcq",
        loader=lambda p: (
            load_global_mmlu(
                language=p.get("language", DEFAULT_LANGUAGE),
                split=p.get("split", "dev"),
            ),
            {},
        ),
        overview=overview_global_mmlu,
        controls=_controls_global_mmlu,
        filters=[
            {"name": "subjects", "label": "Subject", "type": "multiselect", "column": "subject"},
            {
                "name": "cultural_sensitivity",
                "label": "Cultural sensitivity",
                "type": "multiselect",
                "column": "cultural_sensitivity_label",
            },
        ],
    ),
    "mmmlu": DatasetDescriptor(
        id_column="sample_id",
        viewer="mcq",
        loader=lambda p: (load_mmmlu(locale=p.get("locale", DEFAULT_LOCALE)), {}),
        overview=overview_mmmlu,
        controls=_controls_mmmlu,
        filters=[{"name": "subjects", "label": "Subject", "type": "multiselect", "column": "subject"}],
    ),
    "aime_2026": DatasetDescriptor(
        id_column="problem_idx",
        viewer="math_competition",
        loader=lambda _p: (load_aime_2026(), {}),
        overview=overview_aime,
        sample_extras=sample_extras_aime,
    ),
    "hle": DatasetDescriptor(
        id_column="id",
        viewer="academic_qa",
        loader=lambda _p: (load_hle(), {}),
        overview=overview_hle,
        filters=[
            {"name": "categories", "label": "Category", "type": "multiselect", "column": "category"},
            {"name": "subjects", "label": "Subject", "type": "multiselect", "column": "raw_subject"},
            {"name": "answer_types", "label": "Answer type", "type": "multiselect", "column": "answer_type"},
            {
                "name": "modality",
                "label": "Modality",
                "type": "radio",
                "options": ["All", "Text only", "Multimodal"],
                "default": "All",
                "column": "has_image",
                "value_map": {"Text only": False, "Multimodal": True},
            },
        ],
    ),
    "livecodebench_v6": DatasetDescriptor(
        id_column="question_id",
        viewer="code_problem",
        loader=lambda _p: (load_livecodebench(), {}),
        overview=overview_livecodebench,
        supports_private_tests=True,
        filters=[
            {"name": "platforms", "label": "Platform", "type": "multiselect", "column": "platform"},
            {"name": "difficulties", "label": "Difficulty", "type": "multiselect", "column": "difficulty"},
            {
                "name": "date_range",
                "label": "Contest date range",
                "type": "date_range",
                "column": "contest_date",
            },
        ],
    ),
    "swe_bench_verified": DatasetDescriptor(
        id_column="instance_id",
        viewer="issue_resolution",
        loader=lambda _p: (load_swe_bench_verified(), {}),
        overview=overview_swe_bench,
        cache_key="swe_bench",
        filters=_swe_bench_filters(include_difficulty=True, include_language=False),
    ),
    "swe_bench_multilingual": DatasetDescriptor(
        id_column="instance_id",
        viewer="issue_resolution",
        loader=lambda _p: (load_swe_bench_multilingual(), {}),
        overview=overview_swe_bench,
        cache_key="swe_bench",
        filters=_swe_bench_filters(include_difficulty=False, include_language=True),
    ),
    "swe_bench_pro": DatasetDescriptor(
        id_column="instance_id",
        viewer="issue_resolution",
        loader=lambda _p: (load_swe_bench_pro(), {}),
        overview=overview_swe_bench,
        cache_key="swe_bench",
        filters=_swe_bench_filters(include_difficulty=True, include_language=False),
    ),
    "tau3_bench": DatasetDescriptor(
        id_column="instance_id",
        viewer="agent_task",
        loader=lambda p: (load_tau3_bench(task_split=p.get("task_split", "base")), {}),
        overview=overview_tau3_bench,
        controls=_controls_tau3_bench,
        filters=[
            {"name": "domains", "label": "Domain", "type": "multiselect", "column": "domain"},
        ],
        cache_key="tau3_bench",
    ),
    "arxivmath_0526": DatasetDescriptor(
        id_column="problem_idx",
        viewer="arxiv_math",
        loader=lambda _p: (load_problems(), {"outputs": load_outputs()}),
        overview=overview_arxivmath,
        sample_extras=sample_extras_arxivmath,
        filters=[
            {"name": "problems", "label": "Problem", "type": "multiselect", "column": "problem_idx"},
        ],
    ),
}


def build_dataset_registry() -> dict[str, DatasetDescriptor]:
    """Merge hand-written descriptors with catalog entries from config."""
    registry = dict(_MANUAL_REGISTRY)
    config = load_config()
    for datasets in config.categories.values():
        for entry in datasets:
            if entry.loader != "hf_benchmark":
                continue
            if entry.id in registry:
                continue
            registry[entry.id] = _descriptor_from_hf_entry(entry)
    return registry


DATASET_REGISTRY: dict[str, DatasetDescriptor] = build_dataset_registry()


def get_descriptor(dataset_id: str) -> DatasetDescriptor:
    """Return the API descriptor for a dataset id."""
    descriptor = DATASET_REGISTRY.get(dataset_id)
    if descriptor is None:
        msg = f"No API descriptor registered for dataset id: {dataset_id}"
        raise ValueError(msg)
    return descriptor
