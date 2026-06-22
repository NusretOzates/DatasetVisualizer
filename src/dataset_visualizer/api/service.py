"""Dataset API service backing the Gradio server and React frontend."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from dataset_visualizer.api.chart_data import (
    histogram_data,
    pie_chart_data,
    scatter_chart_data,
    stacked_bar_chart,
    timeline_data,
    value_counts_chart,
)
from dataset_visualizer.api.serializers import serialize_row, serialize_rows, serialize_value
from dataset_visualizer.config import DatasetEntry, get_dataset_by_id, load_config
from dataset_visualizer.loaders.aime_2026 import load_aime_2026
from dataset_visualizer.loaders.arxivmath import load_outputs, load_problems
from dataset_visualizer.loaders.global_mmlu import (
    DEFAULT_LANGUAGE,
    list_global_mmlu_languages,
    load_global_mmlu,
)
from dataset_visualizer.loaders.gpqa import load_gpqa_diamond
from dataset_visualizer.loaders.hle import load_hle
from dataset_visualizer.loaders.livecodebench import decode_private_test_cases, load_livecodebench
from dataset_visualizer.loaders.mmlu import load_mmlu
from dataset_visualizer.loaders.mmlu_pro import load_mmlu_pro
from dataset_visualizer.loaders.mmmlu import DEFAULT_LOCALE, list_mmmlu_locales, load_mmmlu
from dataset_visualizer.loaders.swe_bench import (
    load_swe_bench_multilingual,
    load_swe_bench_pro,
    load_swe_bench_verified,
)
from dataset_visualizer.row_count import row_count
from dataset_visualizer.row_values import has_display_value

POPULAR_LANGUAGES = ("en", "es", "fr", "de", "zh", "ja", "ko", "pt", "ar", "hi")
POPULAR_LOCALES = (
    "DE_DE",
    "ES_LA",
    "FR_FR",
    "JA_JP",
    "KO_KR",
    "PT_BR",
    "ZH_CN",
    "AR_XY",
    "HI_IN",
)
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
SOLUTION_COLUMNS = ("solution", "working", "work", "explanation", "rationale")
RUN_TABLE_COLUMNS = [
    "model_name",
    "idx_answer",
    "correct",
    "parsed_answer",
    "gold_answer",
    "input_tokens",
    "output_tokens",
    "cost",
]


@dataclass
class DatasetContext:
    """Loaded dataset state for a single request."""

    entry: DatasetEntry
    df: pd.DataFrame
    extras: dict[str, Any] = field(default_factory=dict)


LoaderFn = Callable[..., pd.DataFrame]


def _hf_source(entry: DatasetEntry) -> str:
    for attr in ("hf_id", "hf_repo", "problems_hf_id"):
        value = getattr(entry, attr, None)
        if value:
            return str(value)
    return "—"


def get_catalog() -> dict[str, Any]:
    """Return navigation metadata and home-page rows."""
    config = load_config()
    categories: list[dict[str, Any]] = []
    home_rows: list[dict[str, str]] = []

    for category_key, datasets in config.categories.items():
        label = category_key.replace("_", " ").title()
        entries = []
        for entry in datasets:
            entries.append(
                {
                    "id": entry.id,
                    "label": entry.label,
                    "icon": entry.icon,
                    "archetype": entry.archetype,
                    "description": entry.description,
                    "hf_source": _hf_source(entry),
                    "row_count": row_count(entry),
                }
            )
            home_rows.append(
                {
                    "category": label,
                    "dataset": entry.label,
                    "hf_source": _hf_source(entry),
                    "archetype": entry.archetype or "—",
                    "rows": row_count(entry),
                }
            )
        categories.append({"key": category_key, "label": label, "datasets": entries})

    return {"categories": categories, "home_rows": home_rows}


def get_dataset_meta(dataset_id: str) -> dict[str, Any]:
    """Return dataset metadata and control definitions."""
    entry = _require_entry(dataset_id)
    return {
        "id": entry.id,
        "label": entry.label,
        "description": entry.description,
        "archetype": entry.archetype,
        "icon": entry.icon,
        "id_column": _id_column(dataset_id),
        "controls": _controls_for_dataset(dataset_id),
        "filters": _filter_schema(dataset_id),
    }


def get_filter_options(dataset_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return available filter option values for the loaded dataset."""
    context = _load_context(dataset_id, params or {})
    return _filter_options_from_df(dataset_id, context.df)


def get_overview(
    dataset_id: str,
    params: dict[str, Any] | None = None,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return overview metrics, tables, and chart payloads."""
    context = _load_context(dataset_id, params or {})
    filtered = _apply_filters(dataset_id, context.df, filters or {})
    return _build_overview(dataset_id, filtered, context.extras)


def get_sample(
    dataset_id: str,
    index: int,
    params: dict[str, Any] | None = None,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a single sample row and any dataset-specific extras."""
    context = _load_context(dataset_id, params or {})
    filtered = _apply_filters(dataset_id, context.df, filters or {})
    if filtered.empty:
        return {"total": 0, "index": 0, "row": None, "extras": {}}
    bounded_index = max(0, min(index, len(filtered) - 1))
    row = filtered.iloc[bounded_index]
    return {
        "total": len(filtered),
        "index": bounded_index,
        "row": serialize_row(row),
        "extras": _sample_extras(dataset_id, row, context.extras),
    }


def find_sample(
    dataset_id: str,
    id_value: str,
    params: dict[str, Any] | None = None,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Find a sample by its id column value."""
    context = _load_context(dataset_id, params or {})
    filtered = _apply_filters(dataset_id, context.df, filters or {})
    id_column = _id_column(dataset_id)
    if id_column not in filtered.columns:
        return {"total": len(filtered), "index": -1, "row": None, "extras": {}}

    matches = filtered[filtered[id_column].astype(str) == str(id_value)]
    if matches.empty:
        return {"total": len(filtered), "index": -1, "row": None, "extras": {}}

    index = int(matches.index[0])
    position = int(filtered.index.get_loc(index))
    row = filtered.loc[index]
    return {
        "total": len(filtered),
        "index": position,
        "row": serialize_row(row),
        "extras": _sample_extras(dataset_id, row, context.extras),
    }


def decode_private_tests_api(raw: str) -> dict[str, Any]:
    """Decode LiveCodeBench private test cases for the sample inspector."""
    if not raw or not str(raw).strip():
        return {"cases": []}
    cases = decode_private_test_cases(str(raw))
    return {"cases": serialize_value(cases)}


def _require_entry(dataset_id: str) -> DatasetEntry:
    entry = get_dataset_by_id(load_config(), dataset_id)
    if entry is None:
        msg = f"Unknown dataset id: {dataset_id}"
        raise ValueError(msg)
    return entry


def _id_column(dataset_id: str) -> str:
    mapping = {
        "mmlu": "subject",
        "mmlu_pro": "question_id",
        "gpqa_diamond": "question",
        "global_mmlu": "sample_id",
        "mmmlu": "sample_id",
        "aime_2026": "problem_idx",
        "hle": "id",
        "livecodebench_v6": "question_id",
        "swe_bench_verified": "instance_id",
        "swe_bench_multilingual": "instance_id",
        "swe_bench_pro": "instance_id",
        "arxivmath_0526": "problem_idx",
    }
    return mapping[dataset_id]


def _controls_for_dataset(dataset_id: str) -> list[dict[str, Any]]:
    if dataset_id == "mmlu":
        return [
            {
                "name": "split",
                "label": "Split",
                "type": "select",
                "options": ["test", "validation", "dev"],
                "default": "test",
            }
        ]
    if dataset_id == "mmlu_pro":
        return [
            {
                "name": "split",
                "label": "Split",
                "type": "select",
                "options": ["test", "validation"],
                "default": "test",
            }
        ]
    if dataset_id == "global_mmlu":
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
    if dataset_id == "mmmlu":
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
    return []


def _filter_schema(dataset_id: str) -> list[dict[str, Any]]:
    schemas: dict[str, list[dict[str, Any]]] = {
        "mmlu": [
            {"name": "subjects", "label": "Subject", "type": "multiselect", "column": "subject"}
        ],
        "mmlu_pro": [
            {
                "name": "categories",
                "label": "Category",
                "type": "multiselect",
                "column": "category",
            },
            {"name": "src_prefix", "label": "Source prefix", "type": "text", "column": "src"},
        ],
        "global_mmlu": [
            {"name": "subjects", "label": "Subject", "type": "multiselect", "column": "subject"},
            {
                "name": "cultural_sensitivity",
                "label": "Cultural sensitivity",
                "type": "multiselect",
                "column": "cultural_sensitivity_label",
            },
        ],
        "mmmlu": [
            {"name": "subjects", "label": "Subject", "type": "multiselect", "column": "subject"}
        ],
        "hle": [
            {
                "name": "categories",
                "label": "Category",
                "type": "multiselect",
                "column": "category",
            },
            {
                "name": "subjects",
                "label": "Subject",
                "type": "multiselect",
                "column": "raw_subject",
            },
            {
                "name": "answer_types",
                "label": "Answer type",
                "type": "multiselect",
                "column": "answer_type",
            },
            {
                "name": "modality",
                "label": "Modality",
                "type": "radio",
                "options": ["All", "Text only", "Multimodal"],
                "default": "All",
            },
        ],
        "livecodebench_v6": [
            {"name": "platforms", "label": "Platform", "type": "multiselect", "column": "platform"},
            {
                "name": "difficulties",
                "label": "Difficulty",
                "type": "multiselect",
                "column": "difficulty",
            },
            {
                "name": "date_range",
                "label": "Contest date range",
                "type": "date_range",
                "column": "contest_date",
            },
        ],
        "swe_bench_verified": [
            {"name": "repos", "label": "Repository", "type": "multiselect", "column": "repo"},
            {
                "name": "difficulties",
                "label": "Difficulty",
                "type": "multiselect",
                "column": "difficulty",
            },
        ],
        "swe_bench_multilingual": [
            {"name": "repos", "label": "Repository", "type": "multiselect", "column": "repo"},
            {
                "name": "languages",
                "label": "Language",
                "type": "multiselect",
                "column": "repo_language",
            },
        ],
        "swe_bench_pro": [
            {"name": "repos", "label": "Repository", "type": "multiselect", "column": "repo"},
            {
                "name": "difficulties",
                "label": "Difficulty",
                "type": "multiselect",
                "column": "difficulty",
            },
        ],
        "arxivmath_0526": [
            {
                "name": "problems",
                "label": "Problem",
                "type": "multiselect",
                "column": "problem_idx",
            },
        ],
    }
    return schemas.get(dataset_id, [])


def _load_context(dataset_id: str, params: dict[str, Any]) -> DatasetContext:
    entry = _require_entry(dataset_id)
    loaders: dict[str, Callable[[dict[str, Any]], tuple[pd.DataFrame, dict[str, Any]]]] = {
        "mmlu": lambda p: (load_mmlu(split=p.get("split", "test")), {}),
        "mmlu_pro": lambda p: (load_mmlu_pro(split=p.get("split", "test")), {}),
        "gpqa_diamond": lambda _p: (load_gpqa_diamond(), {}),
        "global_mmlu": lambda p: (
            load_global_mmlu(
                language=p.get("language", DEFAULT_LANGUAGE), split=p.get("split", "dev")
            ),
            {},
        ),
        "mmmlu": lambda p: (load_mmmlu(locale=p.get("locale", DEFAULT_LOCALE)), {}),
        "aime_2026": lambda _p: (load_aime_2026(), {}),
        "hle": lambda _p: (load_hle(), {}),
        "livecodebench_v6": lambda _p: (load_livecodebench(), {}),
        "swe_bench_verified": lambda _p: (load_swe_bench_verified(), {}),
        "swe_bench_multilingual": lambda _p: (load_swe_bench_multilingual(), {}),
        "swe_bench_pro": lambda _p: (load_swe_bench_pro(), {}),
        "arxivmath_0526": lambda _p: (load_problems(), {"outputs": load_outputs()}),
    }
    loader = loaders.get(dataset_id)
    if loader is None:
        msg = f"No loader registered for dataset id: {dataset_id}"
        raise ValueError(msg)
    df, extras = loader(params)
    return DatasetContext(entry=entry, df=df, extras=extras)


def _filter_options_from_df(dataset_id: str, df: pd.DataFrame) -> dict[str, Any]:
    options: dict[str, Any] = {}
    for spec in _filter_schema(dataset_id):
        column = spec.get("column")
        if column and column in df.columns:
            values = sorted(df[column].dropna().unique(), key=lambda v: str(v))
            options[spec["name"]] = [serialize_value(value) for value in values]
        elif spec["type"] == "radio":
            options[spec["name"]] = spec.get("options", [])
        if spec["type"] == "date_range" and column in df.columns:
            min_date = df[column].min()
            max_date = df[column].max()
            if pd.notna(min_date) and pd.notna(max_date):
                options[spec["name"]] = {
                    "min": min_date.date().isoformat(),
                    "max": max_date.date().isoformat(),
                }
    return options


def _apply_filters(dataset_id: str, df: pd.DataFrame, filters: dict[str, Any]) -> pd.DataFrame:
    filtered = df.copy()

    def _multiselect(name: str, column: str) -> None:
        nonlocal filtered
        selected = filters.get(name)
        if not selected:
            return
        all_values = sorted(filtered[column].dropna().unique(), key=lambda v: str(v))
        if len(selected) < len(all_values):
            filtered = filtered[filtered[column].astype(str).isin([str(v) for v in selected])]

    if dataset_id in {"mmlu", "global_mmlu", "mmmlu"}:
        _multiselect("subjects", "subject")
    if dataset_id == "global_mmlu" and "cultural_sensitivity_label" in filtered.columns:
        _multiselect("cultural_sensitivity", "cultural_sensitivity_label")
    if dataset_id == "mmlu_pro":
        _multiselect("categories", "category")
        prefix = str(filters.get("src_prefix", "")).strip()
        if prefix:
            filtered = filtered[filtered["src"].astype(str).str.startswith(prefix, na=False)]
    if dataset_id == "hle":
        _multiselect("categories", "category")
        _multiselect("subjects", "raw_subject")
        _multiselect("answer_types", "answer_type")
        modality = filters.get("modality", "All")
        if modality == "Text only" and "has_image" in filtered.columns:
            filtered = filtered[~filtered["has_image"]]
        elif modality == "Multimodal" and "has_image" in filtered.columns:
            filtered = filtered[filtered["has_image"]]
    if dataset_id == "livecodebench_v6":
        _multiselect("platforms", "platform")
        _multiselect("difficulties", "difficulty")
        date_range = filters.get("date_range")
        if date_range and "contest_date" in filtered.columns:
            start = date_range.get("start")
            end = date_range.get("end")
            if start and end:
                filtered = filtered[
                    (filtered["contest_date"].dt.date >= pd.to_datetime(start).date())
                    & (filtered["contest_date"].dt.date <= pd.to_datetime(end).date())
                ]
    if dataset_id in {"swe_bench_verified", "swe_bench_multilingual", "swe_bench_pro"}:
        _multiselect("repos", "repo")
        if dataset_id in {"swe_bench_verified", "swe_bench_pro"}:
            _multiselect("difficulties", "difficulty")
        if dataset_id == "swe_bench_multilingual":
            _multiselect("languages", "repo_language")
    if dataset_id == "arxivmath_0526":
        _multiselect("problems", "problem_idx")

    return filtered.reset_index(drop=True)


def _build_overview(
    dataset_id: str,
    df: pd.DataFrame,
    extras: dict[str, Any],
) -> dict[str, Any]:
    builders: dict[str, Callable[[pd.DataFrame, dict[str, Any]], dict[str, Any]]] = {
        "mmlu": _overview_mmlu,
        "mmlu_pro": _overview_mmlu_pro,
        "gpqa_diamond": _overview_gpqa,
        "global_mmlu": _overview_global_mmlu,
        "mmmlu": _overview_mmmlu,
        "aime_2026": _overview_aime,
        "hle": _overview_hle,
        "livecodebench_v6": _overview_livecodebench,
        "swe_bench_verified": _overview_swe_bench,
        "swe_bench_multilingual": _overview_swe_bench,
        "swe_bench_pro": _overview_swe_bench,
        "arxivmath_0526": _overview_arxivmath,
    }
    builder = builders.get(dataset_id)
    if builder is None:
        return {"metrics": [], "charts": [], "tables": []}
    return builder(df, extras)


def _overview_mmlu(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    split_name = str(df["split"].iloc[0]) if "split" in df.columns and len(df) else "—"
    return {
        "metrics": [
            {"label": "Total rows", "value": f"{len(df):,}"},
            {"label": "Subjects", "value": str(df["subject"].nunique())},
            {"label": "Split", "value": split_name},
        ],
        "charts": [
            value_counts_chart(df["subject"], title="Rows per subject", x_label="Subject"),
            pie_chart_data(df["answer_letter"], title="Answer letter distribution"),
        ],
        "tables": [],
    }


def _overview_mmlu_pro(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    split_name = str(df["split"].iloc[0]) if "split" in df.columns and len(df) else "—"
    src_counts = df["src"].value_counts().head(20).reset_index()
    src_counts.columns = ["src", "count"]
    return {
        "metrics": [
            {"label": "Total rows", "value": f"{len(df):,}"},
            {"label": "Categories", "value": str(df["category"].nunique())},
            {"label": "Split", "value": split_name},
        ],
        "charts": [
            value_counts_chart(df["category"], title="Rows per category", x_label="Category"),
            histogram_data(
                df["option_count"], title="Option count distribution", x_label="Options"
            ),
        ],
        "tables": [
            {
                "title": "Top source provenance",
                "columns": ["src", "count"],
                "rows": serialize_rows(src_counts),
            }
        ],
    }


def _overview_gpqa(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    split_name = str(df["split"].iloc[0]) if len(df) else "—"
    return {
        "metrics": [
            {"label": "Total questions", "value": f"{len(df):,}"},
            {"label": "Split", "value": split_name},
        ],
        "charts": [pie_chart_data(df["answer_letter"], title="Answer letter distribution")],
        "tables": [],
    }


def _overview_global_mmlu(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    language = str(df["language"].iloc[0]) if "language" in df.columns and len(df) else "—"
    split_name = str(df["split"].iloc[0]) if "split" in df.columns and len(df) else "—"
    charts = [
        value_counts_chart(df["subject"], title="Rows per subject", x_label="Subject"),
    ]
    if "subject_category" in df.columns:
        charts.append(
            value_counts_chart(
                df["subject_category"],
                title="Subject categories",
                x_label="Category",
            )
        )
    if "cultural_sensitivity_label" in df.columns:
        charts.append(
            pie_chart_data(
                df["cultural_sensitivity_label"], title="Cultural sensitivity (CS vs CA)"
            )
        )
    return {
        "metrics": [
            {"label": "Total rows", "value": f"{len(df):,}"},
            {"label": "Subjects", "value": str(df["subject"].nunique() if len(df) else 0)},
            {"label": "Language", "value": language},
            {"label": "Split", "value": split_name},
        ],
        "charts": charts,
        "tables": [],
    }


def _overview_mmmlu(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    language = str(df["language"].iloc[0]) if "language" in df.columns and len(df) else "—"
    split_name = str(df["split"].iloc[0]) if "split" in df.columns and len(df) else "—"
    return {
        "metrics": [
            {"label": "Total rows", "value": f"{len(df):,}"},
            {"label": "Subjects", "value": str(df["subject"].nunique() if len(df) else 0)},
            {"label": "Locale", "value": language},
            {"label": "Split", "value": split_name},
        ],
        "charts": [
            value_counts_chart(df["subject"], title="Rows per subject", x_label="Subject"),
            pie_chart_data(df["answer_letter"], title="Answer letter distribution"),
        ],
        "tables": [],
    }


def _overview_aime(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    overview = df.copy()
    overview["problem_preview"] = overview["problem"].astype(str).str.slice(0, 120)
    charts = []
    if "answer" in df.columns and len(df):
        charts.append(histogram_data(df["answer"], title="Gold answer distribution"))
    return {
        "metrics": [
            {"label": "Problems", "value": f"{len(df):,}"},
            {"label": "Split", "value": "train"},
        ],
        "charts": charts,
        "tables": [
            {
                "title": "All problems",
                "columns": ["problem_idx", "problem_preview"],
                "rows": serialize_rows(overview[["problem_idx", "problem_preview"]]),
            }
        ],
    }


def _overview_hle(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    split_name = str(df["split"].iloc[0]) if "split" in df.columns and len(df) else "—"
    charts = []
    if "category" in df.columns:
        charts.append(
            value_counts_chart(df["category"], title="Rows per category", x_label="Category")
        )
    if "raw_subject" in df.columns:
        charts.append(
            value_counts_chart(df["raw_subject"], title="Rows per subject", x_label="Subject")
        )
    if "answer_type" in df.columns:
        charts.append(pie_chart_data(df["answer_type"], title="Answer type distribution"))
    if "has_image" in df.columns:
        image_counts = df["has_image"].map({True: "Multimodal", False: "Text only"})
        charts.append(pie_chart_data(image_counts, title="Modality"))
    return {
        "metrics": [
            {"label": "Total questions", "value": f"{len(df):,}"},
            {
                "label": "Categories",
                "value": str(df["category"].nunique() if "category" in df.columns else 0),
            },
            {
                "label": "Subjects",
                "value": str(df["raw_subject"].nunique() if "raw_subject" in df.columns else 0),
            },
            {"label": "Split", "value": split_name},
        ],
        "charts": charts,
        "tables": [],
    }


def _overview_livecodebench(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    median_tests = df["public_test_count"].median() if len(df) else 0
    charts = [
        stacked_bar_chart(
            df,
            x_col="difficulty",
            color_col="platform",
            title="Problems by difficulty and platform",
            x_label="Difficulty",
        )
    ]
    if "contest_date" in df.columns and len(df):
        charts.append(timeline_data(df["contest_date"], title="Contest date distribution"))
    return {
        "metrics": [
            {"label": "Total problems", "value": f"{len(df):,}"},
            {"label": "Platforms", "value": str(df["platform"].nunique() if len(df) else 0)},
            {
                "label": "Median public tests",
                "value": f"{median_tests:.0f}" if len(df) else "—",
            },
        ],
        "charts": charts,
        "tables": [],
    }


def _overview_swe_bench(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    median_fail = df["fail_to_pass_count"].median() if len(df) else 0
    charts = [value_counts_chart(df["repo"], title="Issues per repository", x_label="Repository")]
    if "difficulty" in df.columns and df["difficulty"].notna().any():
        charts.append(pie_chart_data(df["difficulty"], title="Difficulty distribution"))
    return {
        "metrics": [
            {"label": "Total issues", "value": f"{len(df):,}"},
            {"label": "Repositories", "value": str(df["repo"].nunique() if len(df) else 0)},
            {
                "label": "Median FAIL_TO_PASS",
                "value": f"{median_fail:.0f}" if len(df) else "—",
            },
        ],
        "charts": charts,
        "tables": [],
    }


def _author_count(authors: object) -> int:
    if authors is None or (isinstance(authors, float) and pd.isna(authors)):
        return 0
    return len([part for part in str(authors).split(",") if part.strip()])


def _overview_arxivmath(df: pd.DataFrame, extras: dict[str, Any]) -> dict[str, Any]:
    outputs = extras.get("outputs", pd.DataFrame())
    problem_ids = set(df["problem_idx"].astype(str))
    scoped_outputs = outputs[outputs["problem_idx"].isin(problem_ids)] if len(outputs) else outputs

    overview = df.copy()
    overview["author_count"] = overview["authors"].map(_author_count)

    charts: list[dict[str, Any]] = []
    tables = [
        {
            "title": "All problems",
            "columns": ["problem_idx", "title", "source", "author_count"],
            "rows": serialize_rows(overview[["problem_idx", "title", "source", "author_count"]]),
        }
    ]

    if not scoped_outputs.empty:
        accuracy = (
            scoped_outputs.groupby("model_name", as_index=False)["correct"]
            .mean()
            .rename(columns={"correct": "accuracy"})
            .sort_values("accuracy", ascending=False)
        )
        charts.append(
            {
                "type": "bar",
                "title": "Model accuracy (mean correct rate)",
                "x_label": "Model",
                "y_label": "Accuracy",
                "categories": [str(name) for name in accuracy["model_name"].tolist()],
                "values": [float(value) for value in accuracy["accuracy"].tolist()],
            }
        )
        charts.append(
            scatter_chart_data(
                scoped_outputs,
                x="input_tokens",
                y="output_tokens",
                color="correct",
                title="Token usage by attempt",
            )
        )

    return {
        "metrics": [
            {"label": "Problems", "value": f"{len(df):,}"},
            {"label": "Model runs", "value": f"{len(scoped_outputs):,}"},
            {
                "label": "Models",
                "value": str(scoped_outputs["model_name"].nunique() if len(scoped_outputs) else 0),
            },
        ],
        "charts": charts,
        "tables": tables,
    }


def _sample_extras(
    dataset_id: str,
    row: pd.Series,
    extras: dict[str, Any],
) -> dict[str, Any]:
    if dataset_id == "arxivmath_0526":
        outputs = extras.get("outputs", pd.DataFrame())
        problem_idx = str(row.get("problem_idx", ""))
        problem_runs = outputs[outputs["problem_idx"] == problem_idx] if len(outputs) else outputs
        display_cols = [col for col in RUN_TABLE_COLUMNS if col in problem_runs.columns]
        runs = (
            problem_runs[display_cols]
            .sort_values(["model_name", "idx_answer"])
            .reset_index(drop=True)
        )
        return {
            "model_runs": serialize_rows(runs),
            "full_runs": serialize_rows(problem_runs),
        }
    if dataset_id == "aime_2026":
        for field in SOLUTION_COLUMNS:
            if field in row.index and has_display_value(row[field]):
                return {"solution": str(row[field])}
        return {}
    return {}


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


def parse_json_param(raw: str | dict[str, Any] | None) -> dict[str, Any]:
    """Parse a JSON string parameter from Gradio API calls."""
    if raw is None or raw == "":
        return {}
    if isinstance(raw, dict):
        return raw
    return json.loads(raw)
