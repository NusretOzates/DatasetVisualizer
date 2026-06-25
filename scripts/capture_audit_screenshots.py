#!/usr/bin/env python3
"""Capture overview and sample screenshots for the dataset visual audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dataset_visualizer.config import load_config

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs" / "images" / "audit"


def _all_dataset_ids() -> list[str]:
    config = load_config()
    ids: list[str] = []
    for datasets in config.categories.values():
        ids.extend(entry.id for entry in datasets)
    return sorted(ids)


def capture_screenshots(
    *,
    base_url: str = "http://localhost:3000",
    output_dir: Path = OUTPUT_DIR,
    dataset_ids: list[str] | None = None,
    skip_existing: bool = False,
) -> list[str]:
    """Capture overview and sample screenshots for each dataset id."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as err:
        msg = "playwright is required: uv run playwright install chromium"
        raise RuntimeError(msg) from err

    output_dir.mkdir(parents=True, exist_ok=True)
    ids = dataset_ids or _all_dataset_ids()
    captured: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1200})

        for dataset_id in ids:
            overview_path = output_dir / f"{dataset_id}-overview.png"
            sample_path = output_dir / f"{dataset_id}-sample.png"
            if skip_existing and overview_path.exists() and sample_path.exists():
                continue

            url = f"{base_url}/dataset/{dataset_id}"
            page.goto(url, wait_until="domcontentloaded", timeout=180_000)
            page.wait_for_timeout(3000)

            overview_path = output_dir / f"{dataset_id}-overview.png"
            page.screenshot(path=str(overview_path), full_page=True)
            captured.append(str(overview_path))

            sample_tab = page.get_by_role("tab", name="Sample Inspector")
            if sample_tab.count():
                sample_tab.click()
                page.wait_for_timeout(3000)

            sample_path = output_dir / f"{dataset_id}-sample.png"
            page.screenshot(path=str(sample_path), full_page=True)
            captured.append(str(sample_path))
            print(f"Captured {dataset_id}")

        browser.close()

    return captured


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:3000")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--id", dest="dataset_ids", action="append", default=None)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    try:
        capture_screenshots(
            base_url=args.base_url,
            output_dir=args.output_dir,
            dataset_ids=args.dataset_ids,
            skip_existing=args.skip_existing,
        )
    except Exception as err:
        print(err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
