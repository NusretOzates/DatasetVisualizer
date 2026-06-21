"""Shared chart helpers for dataset overview tabs."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def bar_chart(series: pd.Series, title: str, x_label: str = "", y_label: str = "Count") -> None:
    """Render a Plotly bar chart for a value-count series."""
    counts = series.value_counts().reset_index()
    counts.columns = ["category", "count"]
    fig = px.bar(
        counts,
        x="category",
        y="count",
        title=title,
        labels={"category": x_label, "count": y_label},
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


def histogram(series: pd.Series, title: str, x_label: str = "") -> None:
    """Render a Plotly histogram for a numeric series."""
    fig = px.histogram(series, title=title, labels={"value": x_label})
    st.plotly_chart(fig, use_container_width=True)


def pie_chart(series: pd.Series, title: str) -> None:
    """Render a Plotly pie chart for a categorical series."""
    counts = series.value_counts().reset_index()
    counts.columns = ["category", "count"]
    fig = px.pie(counts, names="category", values="count", title=title)
    st.plotly_chart(fig, use_container_width=True)


def timeline(dates: pd.Series, title: str) -> None:
    """Render a timeline histogram for datetime values."""
    fig = px.histogram(dates, title=title, labels={"value": "Date"})
    st.plotly_chart(fig, use_container_width=True)
