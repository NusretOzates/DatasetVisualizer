"""Tests for Math-Arena dataset loading through the API layer."""

from __future__ import annotations

import numpy as np
import pandas as pd

from dataset_visualizer.api.filters import build_filter_options
from dataset_visualizer.api.generic_overview import overview_generic
from dataset_visualizer.loaders.benchmark_normalize import normalize_benchmark


def test_math_arena_like_rows_support_filters_and_overview() -> None:
    df = pd.DataFrame(
        {
            "problem": ["Compute 1+1", "Solve for x"],
            "answer": ["2", "4"],
            "problem_type": [
                np.array(["Number Theory"], dtype=object),
                np.array(["Algebra", "Number Theory"], dtype=object),
            ],
            "split": ["train", "train"],
        }
    )
    normalized = normalize_benchmark(df, "math_competition", "problem_idx")
    schema = [
        {
            "name": "problem_types",
            "label": "Problem type",
            "type": "multiselect",
            "column": "problem_type",
        }
    ]

    options = build_filter_options(normalized, schema)
    overview = overview_generic(normalized, {})

    assert options["problem_types"] == ["Algebra, Number Theory", "Number Theory"]
    assert overview["metrics"][0]["value"] == "2"


def test_build_filter_options_accepts_ndarray_cells() -> None:
    df = pd.DataFrame(
        {
            "problem_type": [np.array(["Number Theory"], dtype=object)],
        }
    )
    schema = [
        {
            "name": "problem_types",
            "type": "multiselect",
            "column": "problem_type",
        }
    ]

    options = build_filter_options(df, schema)

    assert options["problem_types"] == [["Number Theory"]]
