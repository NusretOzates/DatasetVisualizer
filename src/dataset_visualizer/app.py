"""Streamlit application entry point."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from dataset_visualizer.config import load_config
from dataset_visualizer.registry import build_navigation

PAGES_ROOT = Path(__file__).resolve().parent / "pages"


def main() -> None:
    """Run the Dataset Visualizer Streamlit app."""
    st.set_page_config(page_title="Dataset Visualizer", layout="wide")
    config = load_config()
    home = st.Page(str(PAGES_ROOT / "home.py"), title="Home", icon=":house:", default=True)
    nav = build_navigation(config)
    pg = st.navigation({"": [home], **nav})
    pg.run()


if __name__ == "__main__":
    main()
