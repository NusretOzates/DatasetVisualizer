"""In-process cache for dataset loaders (replaces Streamlit ``@loader_cache``)."""

from __future__ import annotations

import functools
import pickle
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def _cache_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[Any, ...]:
    """Build a hashable cache key from call arguments."""

    def _normalize(obj: Any) -> Any:
        try:
            pickle.dumps(obj)
            return obj
        except Exception:
            return repr(obj)

    return tuple(_normalize(a) for a in args) + tuple(
        (k, _normalize(v)) for k, v in sorted(kwargs.items())
    )


class _CachedLoader:
    """Callable wrapper that memoizes loader results in memory."""

    def __init__(self, fn: Callable[P, R], cache: dict[tuple[Any, ...], R]) -> None:
        functools.update_wrapper(self, fn)
        self._fn = fn
        self._cache = cache

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        key = _cache_key(args, kwargs)
        if key not in self._cache:
            self._cache[key] = self._fn(*args, **kwargs)
        return self._cache[key]

    def clear(self) -> None:
        """Clear cached results (used in tests)."""
        self._cache.clear()


def loader_cache(*, show_spinner: str | bool = False) -> Callable[[Callable[P, R]], _CachedLoader]:
    """Cache loader results in memory for the lifetime of the process."""
    _ = show_spinner  # kept for drop-in compatibility with former ``@loader_cache`` calls

    def decorator(fn: Callable[P, R]) -> _CachedLoader:
        cache_store: dict[tuple[Any, ...], R] = {}
        return _CachedLoader(fn, cache_store)

    return decorator
