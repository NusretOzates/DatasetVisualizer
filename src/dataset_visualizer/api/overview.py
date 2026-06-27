"""Per-dataset overview payload builders."""

from __future__ import annotations

from typing import Any

import pandas as pd

from dataset_visualizer.api.serializers import serialize_rows
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


def _count_table(df: pd.DataFrame, column: str, count_column: str = "count") -> pd.DataFrame:
    """Return value counts for one column as a small summary frame."""
    if column not in df.columns or not len(df):
        return pd.DataFrame(columns=[column, count_column])
    counts = df[column].value_counts().reset_index()
    counts.columns = [column, count_column]
    return counts


def overview_mmlu(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    return {
        "metrics": [
            {"label": "Total rows", "value": f"{len(df):,}"},
            {"label": "Subjects", "value": _nunique_str(df, "subject")},
            {"label": "Split", "value": _split_label(df)},
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
        "tables": [],
    }


def overview_global_mmlu(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    language = str(df["language"].iloc[0]) if "language" in df.columns and len(df) else "—"
    return {
        "metrics": [
            {"label": "Total rows", "value": f"{len(df):,}"},
            {"label": "Subjects", "value": _nunique_str(df, "subject")},
            {"label": "Language", "value": language},
            {"label": "Split", "value": _split_label(df)},
        ],
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
        "tables": [],
    }


def overview_aime(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    return {
        "metrics": [
            {"label": "Problems", "value": f"{len(df):,}"},
            {"label": "Split", "value": "train"},
        ],
        "tables": [],
    }


def overview_hle(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    return {
        "metrics": [
            {"label": "Total questions", "value": f"{len(df):,}"},
            {"label": "Categories", "value": _nunique_str(df, "category")},
            {"label": "Subjects", "value": _nunique_str(df, "raw_subject")},
            {"label": "Split", "value": _split_label(df)},
        ],
        "tables": [],
    }


def overview_livecodebench(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    median_tests = df["public_test_count"].median() if len(df) else 0
    return {
        "metrics": [
            {"label": "Total problems", "value": f"{len(df):,}"},
            {"label": "Platforms", "value": _nunique_str(df, "platform")},
            {
                "label": "Median public tests",
                "value": f"{median_tests:.0f}" if len(df) else "—",
            },
        ],
        "tables": [],
    }


def overview_swe_bench(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    median_fail = df["fail_to_pass_count"].median() if len(df) else 0
    return {
        "metrics": [
            {"label": "Total issues", "value": f"{len(df):,}"},
            {"label": "Repositories", "value": _nunique_str(df, "repo")},
            {
                "label": "Median FAIL_TO_PASS",
                "value": f"{median_fail:.0f}" if len(df) else "—",
            },
        ],
        "tables": [],
    }


def overview_tau3_bench(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    """Build overview metrics for τ³-Bench agent tasks."""
    domain_counts = _count_table(df, "domain", "task_count")
    return {
        "metrics": [
            {"label": "Tasks", "value": f"{len(df):,}"},
            {"label": "Domains", "value": _nunique_str(df, "domain")},
            {"label": "Split", "value": _split_label(df)},
        ],
        "tables": [
            {
                "title": "Tasks by domain",
                "columns": ["domain", "task_count"],
                "rows": serialize_rows(domain_counts),
            }
        ],
    }


def overview_terminal_bench(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    """Build overview metrics for Terminal-Bench 2.1 tasks."""
    category_counts = _count_table(df, "category", "task_count")
    return {
        "metrics": [
            {"label": "Tasks", "value": f"{len(df):,}"},
            {"label": "Categories", "value": _nunique_str(df, "category")},
            {"label": "Split", "value": _split_label(df)},
        ],
        "tables": [
            {
                "title": "Tasks by category",
                "columns": ["category", "task_count"],
                "rows": serialize_rows(category_counts),
            }
        ],
    }


def overview_nocha(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    """Build overview metrics for the public NoCha sample claims."""
    pair_count = df[["book_title", "pair_index"]].drop_duplicates().shape[0]
    book_counts = _count_table(df, "book_title", "claim_count")
    return {
        "metrics": [
            {"label": "Claims", "value": f"{len(df):,}"},
            {"label": "Claim pairs", "value": f"{pair_count:,}"},
            {"label": "Books", "value": _nunique_str(df, "book_title")},
            {"label": "Length buckets", "value": _nunique_str(df, "length_group")},
        ],
        "tables": [
            {
                "title": "Claims by book",
                "columns": ["book_title", "claim_count"],
                "rows": serialize_rows(book_counts),
            }
        ],
    }


def overview_browsecomp(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    """Build overview metrics for BrowseComp browsing-agent questions."""
    topic_counts = _count_table(df, "problem_topic", "question_count")
    return {
        "metrics": [
            {"label": "Questions", "value": f"{len(df):,}"},
            {"label": "Topics", "value": _nunique_str(df, "problem_topic")},
            {"label": "Split", "value": _split_label(df)},
        ],
        "tables": [
            {
                "title": "Questions by topic",
                "columns": ["problem_topic", "question_count"],
                "rows": serialize_rows(topic_counts),
            }
        ],
    }


def overview_toolathlon(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    """Build overview metrics for Toolathlon MCP agent tasks."""
    mcp_counts = _count_table(df, "primary_mcp", "task_count")

    avg_mcp = f"{df['mcp_server_count'].mean():.1f}" if "mcp_server_count" in df.columns else "—"
    avg_local = f"{df['local_tool_count'].mean():.1f}" if "local_tool_count" in df.columns else "—"

    return {
        "metrics": [
            {"label": "Tasks", "value": f"{len(df):,}"},
            {"label": "Primary MCP servers", "value": _nunique_str(df, "primary_mcp")},
            {"label": "Avg MCP servers / task", "value": avg_mcp},
            {"label": "Avg local tools / task", "value": avg_local},
            {"label": "Split", "value": _split_label(df)},
        ],
        "tables": [
            {
                "title": "Tasks by primary MCP server",
                "columns": ["primary_mcp", "task_count"],
                "rows": serialize_rows(mcp_counts),
            }
        ],
    }


def overview_osworld_verified(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    """Build overview metrics for OSWorld-Verified GUI agent tasks."""
    domain_counts = _count_table(df, "domain", "task_count")
    return {
        "metrics": [
            {"label": "Tasks", "value": f"{len(df):,}"},
            {"label": "Domains", "value": _nunique_str(df, "domain")},
            {"label": "Evaluator types", "value": _nunique_str(df, "evaluator_func")},
            {"label": "Split", "value": _split_label(df)},
        ],
        "tables": [
            {
                "title": "Tasks by domain",
                "columns": ["domain", "task_count"],
                "rows": serialize_rows(domain_counts),
            }
        ],
    }


def overview_arxivmath(df: pd.DataFrame, extras: dict[str, Any]) -> dict[str, Any]:
    outputs = extras.get("outputs", pd.DataFrame())
    problem_ids = set(df["problem_idx"].astype(str))
    scoped_outputs = outputs[outputs["problem_idx"].isin(problem_ids)] if len(outputs) else outputs

    source_counts = _count_table(df, "source", "problem_count")

    return {
        "metrics": [
            {"label": "Problems", "value": f"{len(df):,}"},
            {"label": "Model runs", "value": f"{len(scoped_outputs):,}"},
            {
                "label": "Models",
                "value": str(scoped_outputs["model_name"].nunique() if len(scoped_outputs) else 0),
            },
            {"label": "Sources", "value": _nunique_str(df, "source")},
        ],
        "tables": [
            {
                "title": "Problems by source",
                "columns": ["source", "problem_count"],
                "rows": serialize_rows(source_counts),
            }
        ],
    }


def sample_extras_arxivmath(row: pd.Series, extras: dict[str, Any]) -> dict[str, Any]:
    outputs = extras.get("outputs", pd.DataFrame())
    problem_idx = str(row.get("problem_idx", ""))
    problem_runs = outputs[outputs["problem_idx"] == problem_idx] if len(outputs) else outputs
    display_cols = [col for col in RUN_TABLE_COLUMNS if col in problem_runs.columns]
    runs = (
        problem_runs[display_cols].sort_values(["model_name", "idx_answer"]).reset_index(drop=True)
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


BOOK_TEXT_PREVIEW_CHARS = 12_000


def sample_extras_nocha(row: pd.Series, extras: dict[str, Any]) -> dict[str, Any]:
    """Attach a truncated book-text preview for the selected claim."""
    books = extras.get("books", {})
    book_title = str(row.get("book_title", ""))
    book_text = books.get(book_title, "") if isinstance(books, dict) else ""
    preview = book_text[:BOOK_TEXT_PREVIEW_CHARS]
    omitted_chars = max(0, len(book_text) - len(preview))
    return {
        "book_text_preview": preview,
        "book_char_count": len(book_text),
        "book_text_omitted_chars": omitted_chars,
    }
