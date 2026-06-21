"""Tests for row value presence helpers."""

from __future__ import annotations

import numpy as np
import pytest

from dataset_visualizer.row_values import has_display_value


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("No", True),
        (None, False),
        (float("nan"), False),
        (["none"], True),
        ([], False),
        (np.array(["cultural"]), True),
        (np.array([]), False),
    ],
)
def test_has_display_value(value: object, expected: bool) -> None:
    assert has_display_value(value) is expected


def test_has_display_value_list_does_not_use_pd_notna_in_boolean_context() -> None:
    """Regression: pd.notna on a list returns an array and breaks ``if pd.notna(...)``."""
    assert has_display_value(["none"]) is True
    assert has_display_value([]) is False
