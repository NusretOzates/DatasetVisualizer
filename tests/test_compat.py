"""Tests for third-party compatibility shims."""

from __future__ import annotations

import warnings

from starlette import status

from dataset_visualizer.compat import apply_warning_filters


def test_compat_suppresses_starlette_422_deprecation_warning() -> None:
    apply_warning_filters()
    with warnings.catch_warnings(record=True) as caught:
        assert status.HTTP_422_UNPROCESSABLE_ENTITY == 422

    starlette_warnings = [
        warning for warning in caught if "HTTP_422_UNPROCESSABLE_ENTITY" in str(warning.message)
    ]
    assert starlette_warnings == []
