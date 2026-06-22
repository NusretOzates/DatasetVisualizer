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
    sample_extras_aime,
    sample_extras_arxivmath,
)
from dataset_visualizer.loaders.aime_2026 import load_aime_2026
from dataset_visualizer.loaders.arxivmath import load_outputs, load_problems
from dataset_visualizer.loaders.global_mmlu import (
    DEFAULT_LANGUAGE,
    list_global_mmlu_languages,
    load_global_mmlu,
)
from dataset_visualizer.loaders.gpqa import load_gpqa_diamond
from dataset_visualizer.loaders.hle import load_hle
from dataset_visualizer.loaders.livecodebench import load_livecodebench
from dataset_visualizer.loaders.mmlu import load_mmlu
from dataset_visualizer.loaders.mmlu_pro import load_mmlu_pro
from dataset_visualizer.loaders.mmmlu import DEFAULT_LOCALE, list_mmmlu_locales, load_mmmlu
from dataset_visualizer.loaders.swe_bench import (
    load_swe_bench_multilingual,
    load_swe_bench_pro,
    load_swe_bench_verified,
)

POPULAR_LANGUAGES = ("en", "es", "fr", "de", "zh", "ja", "ko", "pt", "ar", "hi")
LOCALE_LABELS: dict[str, str] = {
    "AR_XY": "Arabic",
    "BN_BD": "Bengali",
    "DE_DE": "German",
    "ES_LA": "Spanish",
    "FR_FR": "French",
    "HI_IN": "Hindi",
    "ID_ID": "Indonesian",
    "IT_IT": "Italian",
    "JA_JP": "Japanese",
    "KO_KR": "Korean",
    "PT_BR": "Portuguese (Brazil)",
    "SW_KE": "Swahili",
    "YO_NG": "Yoruba",
    "ZH_CN": "Chinese (Simplified)",
}
POPULAR_LOCALES = tuple(
    locale for locale in ("DE_DE", "ES_LA", "FR_FR", "JA_JP", "KO_KR", "PT_BR", "AR_XY", "HI_IN")
    if locale in LOCALE_LABELS
)

LoaderFn = Callable[[dict[str, Any]], tuple[pd.DataFrame, dict[str, Any]]]
OverviewFn = Callable[[pd.DataFrame, dict[str, Any]], dict[str, Any]]
SampleExtrasFn = Callable[[pd.Series, dict[str, Any]], dict[str, Any]]
ControlsFn = Callable[[], list[dict[str, Any]]]


@dataclass
class DatasetDescriptor:
    """API behaviour for one config dataset id."""

    id_column: str
    viewer: str
    loader: LoaderFn
    overview: OverviewFn
    controls: ControlsFn | list[dict[str, Any]] = field(default_factory=list)
    filters: list[dict[str, Any]] = field(default_factory=list)
    sample_extras: SampleExtrasFn | None = None
    supports_private_tests: bool = False


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


DATASET_REGISTRY: dict[str, DatasetDescriptor] = {
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
        viewer="mcq_multilingual",
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
        viewer="mcq_multilingual",
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
        filters=[
            {"name": "repos", "label": "Repository", "type": "multiselect", "column": "repo"},
            {"name": "difficulties", "label": "Difficulty", "type": "multiselect", "column": "difficulty"},
        ],
    ),
    "swe_bench_multilingual": DatasetDescriptor(
        id_column="instance_id",
        viewer="issue_resolution",
        loader=lambda _p: (load_swe_bench_multilingual(), {}),
        overview=overview_swe_bench,
        filters=[
            {"name": "repos", "label": "Repository", "type": "multiselect", "column": "repo"},
            {"name": "languages", "label": "Language", "type": "multiselect", "column": "repo_language"},
        ],
    ),
    "swe_bench_pro": DatasetDescriptor(
        id_column="instance_id",
        viewer="issue_resolution",
        loader=lambda _p: (load_swe_bench_pro(), {}),
        overview=overview_swe_bench,
        filters=[
            {"name": "repos", "label": "Repository", "type": "multiselect", "column": "repo"},
            {"name": "difficulties", "label": "Difficulty", "type": "multiselect", "column": "difficulty"},
        ],
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


def get_descriptor(dataset_id: str) -> DatasetDescriptor:
    """Return the API descriptor for a dataset id."""
    descriptor = DATASET_REGISTRY.get(dataset_id)
    if descriptor is None:
        msg = f"No API descriptor registered for dataset id: {dataset_id}"
        raise ValueError(msg)
    return descriptor


def resolve_controls(descriptor: DatasetDescriptor) -> list[dict[str, Any]]:
    """Return control definitions, evaluating callables when needed."""
    if callable(descriptor.controls):
        return descriptor.controls()
    return descriptor.controls
