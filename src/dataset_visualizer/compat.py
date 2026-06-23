"""Compatibility shims for third-party dependency mismatches."""

from __future__ import annotations

import warnings


def apply_warning_filters() -> None:
    """Register warning filters for known upstream dependency mismatches."""
    # Gradio 6.19 still reads Starlette's deprecated HTTP_422_UNPROCESSABLE_ENTITY constant.
    # Silence until upstream switches to HTTP_422_UNPROCESSABLE_CONTENT (gradio-app/gradio#13548).
    warnings.filterwarnings(
        "ignore",
        message="'HTTP_422_UNPROCESSABLE_ENTITY' is deprecated.*",
    )
