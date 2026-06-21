"""CLI entry point for launching the Streamlit app."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Launch the Dataset Visualizer via the Streamlit server."""
    app_path = Path(__file__).resolve().parent / "app.py"
    completed = subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path), *sys.argv[1:]],
        check=False,
    )
    raise SystemExit(completed.returncode)
