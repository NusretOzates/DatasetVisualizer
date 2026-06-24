"""Pick the smallest Hugging Face dataset split for inspection workloads."""

from __future__ import annotations

import functools

from datasets import get_dataset_config_info

_SPLIT_PREFERENCE = ("test", "validation", "dev", "train", "default")
_UNKNOWN_SPLIT_SIZE = 10**18


def _split_num_examples(split_info: object) -> int:
    """Return a split's row count when Hub metadata exposes it."""
    count = getattr(split_info, "num_examples", None)
    if isinstance(count, int):
        return count
    if isinstance(split_info, dict):
        dict_count = split_info.get("num_examples")
        if isinstance(dict_count, int):
            return dict_count
    return _UNKNOWN_SPLIT_SIZE


def _preference_key(split_name: str) -> tuple[int, str]:
    """Rank splits for stable tie-breaking when row counts match."""
    try:
        return (_SPLIT_PREFERENCE.index(split_name), split_name)
    except ValueError:
        return (len(_SPLIT_PREFERENCE), split_name)


@functools.lru_cache(maxsize=256)
def select_smallest_split(hf_id: str, hf_config: str | None = None) -> str:
    """Return the published split with the fewest rows for a Hub dataset config.

    Args:
        hf_id: Hugging Face dataset repository id.
        hf_config: Optional dataset config/subset name.

    Returns:
        Split name to pass to ``load_dataset(..., split=...)``.

    Raises:
        ValueError: If the dataset exposes no splits in its metadata.
    """
    if hf_config:
        info = get_dataset_config_info(hf_id, config_name=hf_config)
    else:
        info = get_dataset_config_info(hf_id)

    if not info.splits:
        msg = f"Dataset {hf_id} has no published splits"
        raise ValueError(msg)

    return min(
        info.splits.keys(),
        key=lambda name: (_split_num_examples(info.splits[name]), _preference_key(name)),
    )
