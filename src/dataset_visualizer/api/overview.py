"""Per-dataset overview payload builders."""

from __future__ import annotations

from typing import Any

import pandas as pd

from dataset_visualizer.api.chart_data import (
    bar_chart_data,
    histogram_data,
    pie_chart_data,
    scatter_chart_data,
    stacked_bar_chart,
    timeline_data,
    value_counts_chart,
)
from dataset_visualizer.api.serializers import serialize_rows, serialize_value
from dataset_visualizer.row_values import has_display_value

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


def _split_label(df: pd.DataFrame) -> str:
    if "split" in df.columns and len(df):
        return str(df["split"].iloc[0])
    return "—"


def _nunique_str(df: pd.DataFrame, column: str) -> str:
    if column not in df.columns or not len(df):
        return "0"
    return str(df[column].nunique())


def overview_mmlu(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    return {
        "metrics": [
            {"label": "Total rows", "value": f"{len(df):,}"},
            {"label": "Subjects", "value": _nunique_str(df, "subject")},
            {"label": "Split", "value": _split_label(df)},
        ],
        "charts": [
            value_counts_chart(df["subject"], title="Rows per subject", x_label="Subject"),
            pie_chart_data(df["answer_letter"], title="Answer letter distribution"),
        ],
        "tables": [],
    }


def overview_mmlu_pro(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    src_counts = df["src"].value_counts().head(20).reset_index()
    src_counts.columns = ["src", "count"]
    return {
        "metrics": [
            {"label": "Total rows", "value": f"{len(df):,}"},
            {"label": "Categories", "value": _nunique_str(df, "category")},
            {"label": "Split", "value": _split_label(df)},
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


def overview_gpqa(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    return {
        "metrics": [
            {"label": "Total questions", "value": f"{len(df):,}"},
            {"label": "Split", "value": _split_label(df)},
        ],
        "charts": [pie_chart_data(df["answer_letter"], title="Answer letter distribution")],
        "tables": [],
    }


def overview_global_mmlu(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    language = str(df["language"].iloc[0]) if "language" in df.columns and len(df) else "—"
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
            {"label": "Subjects", "value": _nunique_str(df, "subject")},
            {"label": "Language", "value": language},
            {"label": "Split", "value": _split_label(df)},
        ],
        "charts": charts,
        "tables": [],
    }


def overview_mmmlu(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    language = str(df["language"].iloc[0]) if "language" in df.columns and len(df) else "—"
    return {
        "metrics": [
            {"label": "Total rows", "value": f"{len(df):,}"},
            {"label": "Subjects", "value": _nunique_str(df, "subject")},
            {"label": "Locale", "value": language},
            {"label": "Split", "value": _split_label(df)},
        ],
        "charts": [
            value_counts_chart(df["subject"], title="Rows per subject", x_label="Subject"),
            pie_chart_data(df["answer_letter"], title="Answer letter distribution"),
        ],
        "tables": [],
    }


def overview_aime(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
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


def overview_hle(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
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
            {"label": "Categories", "value": _nunique_str(df, "category")},
            {"label": "Subjects", "value": _nunique_str(df, "raw_subject")},
            {"label": "Split", "value": _split_label(df)},
        ],
        "charts": charts,
        "tables": [],
    }


def overview_livecodebench(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
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
            {"label": "Platforms", "value": _nunique_str(df, "platform")},
            {
                "label": "Median public tests",
                "value": f"{median_tests:.0f}" if len(df) else "—",
            },
        ],
        "charts": charts,
        "tables": [],
    }


def overview_swe_bench(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    median_fail = df["fail_to_pass_count"].median() if len(df) else 0
    charts = [value_counts_chart(df["repo"], title="Issues per repository", x_label="Repository")]
    if "difficulty" in df.columns and df["difficulty"].notna().any():
        charts.append(pie_chart_data(df["difficulty"], title="Difficulty distribution"))
    return {
        "metrics": [
            {"label": "Total issues", "value": f"{len(df):,}"},
            {"label": "Repositories", "value": _nunique_str(df, "repo")},
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


def overview_arxivmath(df: pd.DataFrame, extras: dict[str, Any]) -> dict[str, Any]:
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
            bar_chart_data(
                categories=[str(name) for name in accuracy["model_name"].tolist()],
                values=[float(value) for value in accuracy["accuracy"].tolist()],
                title="Model accuracy (mean correct rate)",
                x_label="Model",
                y_label="Accuracy",
            )
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


def sample_extras_arxivmath(row: pd.Series, extras: dict[str, Any]) -> dict[str, Any]:
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


def sample_extras_aime(row: pd.Series, _extras: dict[str, Any]) -> dict[str, Any]:
    for field in SOLUTION_COLUMNS:
        if field in row.index and has_display_value(row[field]):
            return {"solution": str(row[field])}
    return {}
