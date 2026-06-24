"""Pre-download catalog datasets to warm local Hugging Face caches."""

from __future__ import annotations

import argparse
import sys
import threading
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed

from dataset_visualizer.api.dataset_registry import get_descriptor
from dataset_visualizer.config import DatasetEntry, get_dataset_by_id, load_config

FAST_DATASET_IDS = ("arxivmath_0526", "humaneval", "mbpp", "openbookqa")
GATED_HF_IDS = frozenset(
    {
        "Idavidrein/gpqa",
        "gaia-benchmark/GAIA",
        "cais/hle",
        "meta-agents-research-environments/gaia2",
    }
)
DEFAULT_WORKERS = 4


def _all_dataset_ids() -> list[str]:
    config = load_config()
    return sorted(entry.id for datasets in config.categories.values() for entry in datasets)


def _is_gated_entry(entry: DatasetEntry) -> bool:
    if entry.hf_id and entry.hf_id in GATED_HF_IDS:
        return True
    if entry.problems_hf_id and entry.problems_hf_id in GATED_HF_IDS:
        return True
    description = entry.description.lower()
    return "gated" in description


def _resolve_dataset_ids(
    *,
    dataset_id: str | None,
    category: str | None,
    fast: bool,
) -> list[str]:
    if fast:
        return list(FAST_DATASET_IDS)

    config = load_config()
    if dataset_id:
        entry = get_dataset_by_id(config, dataset_id)
        if entry is None:
            valid = ", ".join(_all_dataset_ids())
            msg = f"Unknown dataset id: {dataset_id}. Valid ids: {valid}"
            raise ValueError(msg)
        return [dataset_id]

    if category:
        datasets = config.categories.get(category)
        if not datasets:
            valid = ", ".join(sorted(config.categories))
            msg = f"Unknown category: {category}. Valid categories: {valid}"
            raise ValueError(msg)
        return [entry.id for entry in datasets]

    return _all_dataset_ids()


def _default_loader_params(entry: DatasetEntry) -> dict[str, str]:
    """Pick registry defaults for loaders that still expose non-split controls."""
    if entry.loader == "global_mmlu":
        return {"language": "en"}
    if entry.loader == "mmmlu":
        return {"locale": "DE_DE"}
    if entry.loader == "tau3_bench":
        return {"task_split": "base"}
    return {}


def _download_one(
    *,
    index: int,
    total: int,
    dataset_id: str,
    entry: DatasetEntry,
    print_lock: threading.Lock,
) -> bool:
    """Load one dataset. Returns True when the run should count as a failure."""
    with print_lock:
        print(f"[{index}/{total}] Loading {entry.label} ({dataset_id}) …")
    try:
        descriptor = get_descriptor(dataset_id)
        params = _default_loader_params(entry)
        df, _extras = descriptor.loader(params)
        split = df["split"].iloc[0] if "split" in df.columns and len(df) else "—"
        with print_lock:
            print(f"  OK {len(df):,} rows (split={split})")
    except Exception as err:
        lowered = str(err).lower()
        with print_lock:
            if "gated" in lowered or "authenticated" in lowered:
                print(
                    f"[{index}/{total}] WARN {dataset_id}: gated on Hugging Face — "
                    f"set HF_TOKEN and accept dataset terms ({err})",
                    file=sys.stderr,
                )
            else:
                print(
                    f"[{index}/{total}] FAIL {dataset_id}: {err}",
                    file=sys.stderr,
                )
        return True
    return False


def pre_download_datasets(
    dataset_ids: Iterable[str],
    *,
    skip_gated: bool = False,
    workers: int = DEFAULT_WORKERS,
) -> int:
    """Download and normalize each dataset id, printing progress along the way.

    Args:
        dataset_ids: Config entry ids to warm.
        skip_gated: When true, skip datasets known to require Hub terms or a token.
        workers: Number of parallel download threads. Use 1 for sequential loading.

    Returns:
        Process exit code (0 if every dataset loaded, 1 if any failed).
    """
    if workers < 1:
        msg = f"workers must be >= 1, got {workers}"
        raise ValueError(msg)

    config = load_config()
    failures = 0
    ids = list(dataset_ids)
    total = len(ids)
    print_lock = threading.Lock()
    jobs: list[tuple[int, str, DatasetEntry]] = []

    for index, dataset_id in enumerate(ids, start=1):
        entry = get_dataset_by_id(config, dataset_id)
        if entry is None:
            print(f"[{index}/{total}] SKIP {dataset_id}: not in config", file=sys.stderr)
            failures += 1
            continue

        if skip_gated and _is_gated_entry(entry):
            print(
                f"[{index}/{total}] WARN {dataset_id}: skipped gated dataset "
                f"({entry.hf_id or entry.problems_hf_id or 'see description'})",
                file=sys.stderr,
            )
            continue

        jobs.append((index, dataset_id, entry))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                _download_one,
                index=index,
                total=total,
                dataset_id=dataset_id,
                entry=entry,
                print_lock=print_lock,
            )
            for index, dataset_id, entry in jobs
        ]
        for future in as_completed(futures):
            if future.result():
                failures += 1

    if failures:
        print(f"\nFinished with {failures} warning(s)/failure(s).", file=sys.stderr)
        return 1

    print(f"\nAll {total} dataset(s) loaded successfully.")
    return 0


def main(argv: list[str] | None = None) -> None:
    """CLI entry point for ``uv run pre-download``."""
    parser = argparse.ArgumentParser(
        description="Pre-download registered datasets before starting the backend.",
    )
    parser.add_argument("--id", dest="dataset_id", help="Single config dataset id.")
    parser.add_argument("--category", help="All datasets in a config category key.")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Download a small smoke-test subset only.",
    )
    parser.add_argument(
        "--skip-gated",
        action="store_true",
        help="Skip datasets known to be gated on Hugging Face.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        metavar="N",
        help=f"Parallel download threads (default: {DEFAULT_WORKERS}). Use 1 for sequential.",
    )
    args = parser.parse_args(argv)

    if sum(bool(value) for value in (args.dataset_id, args.category, args.fast)) > 1:
        parser.error("Use only one of --id, --category, or --fast.")

    if args.workers < 1:
        parser.error("--workers must be >= 1.")

    try:
        dataset_ids = _resolve_dataset_ids(
            dataset_id=args.dataset_id,
            category=args.category,
            fast=args.fast,
        )
    except ValueError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1) from err

    raise SystemExit(
        pre_download_datasets(
            dataset_ids,
            skip_gated=args.skip_gated,
            workers=args.workers,
        ),
    )


if __name__ == "__main__":
    main()
