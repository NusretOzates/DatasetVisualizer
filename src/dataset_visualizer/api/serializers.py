"""JSON serialization helpers for API responses."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd


def serialize_value(value: object) -> object:
    """Convert a pandas/numpy value into a JSON-safe Python object."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, (np.floating,)):
        if np.isnan(value):
            return None
        return float(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, np.ndarray):
        return [serialize_value(item) for item in value.tolist()]
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if isinstance(value, pd.Series):
        return serialize_row(value)
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): serialize_value(v) for k, v in value.items()}
    return value


def serialize_row(row: pd.Series) -> dict[str, Any]:
    """Serialize a DataFrame row to a JSON-safe dict."""
    return {str(key): serialize_value(value) for key, value in row.to_dict().items()}


def serialize_rows(df: pd.DataFrame, limit: int | None = None) -> list[dict[str, Any]]:
    """Serialize DataFrame rows for API responses."""
    subset = df.head(limit) if limit is not None else df
    return [serialize_row(row) for _, row in subset.iterrows()]
