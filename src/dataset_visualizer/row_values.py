"""Helpers for interpreting pandas row field values."""

from __future__ import annotations

import pandas as pd


def has_display_value(value: object) -> bool:
    """Return whether a row field value is present and should be shown in the UI."""
    if value is None:
        return False
    if isinstance(value, float) and pd.isna(value):
        return False
    if isinstance(value, (list, tuple)):
        return len(value) > 0
    if hasattr(value, "shape") and hasattr(value, "size"):
        return value.size > 0
    return bool(pd.notna(value))
