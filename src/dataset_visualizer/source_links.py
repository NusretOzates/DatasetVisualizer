"""Resolve external source links for catalog datasets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from dataset_visualizer.config import DatasetEntry
from dataset_visualizer.loaders.browsecomp import BROWSECOMP_GITHUB_REPO
from dataset_visualizer.loaders.nocha import NOCHA_GITHUB_REPO
from dataset_visualizer.loaders.osworld_verified import OSWORLD_GITHUB_REPO
from dataset_visualizer.loaders.toolathlon import TOOLATHLON_GITHUB_REPO
from dataset_visualizer.loaders.tau3_bench import TAU3_BENCH_GITHUB_REPO
from dataset_visualizer.loaders.terminal_bench import TERMINAL_BENCH_GITHUB_REPO

SourceKind = Literal["huggingface", "github", "web"]

_GITHUB_LOADER_REPOS: dict[str, str] = {
    "tau3_bench": TAU3_BENCH_GITHUB_REPO,
    "terminal_bench_21": TERMINAL_BENCH_GITHUB_REPO,
    "nocha": NOCHA_GITHUB_REPO,
    "browsecomp": BROWSECOMP_GITHUB_REPO,
    "osworld_verified": OSWORLD_GITHUB_REPO,
    "toolathlon": TOOLATHLON_GITHUB_REPO,
}


@dataclass(frozen=True)
class SourceLink:
    """External link to a dataset's upstream source."""

    url: str
    label: str
    kind: SourceKind


def resolve_source_link(entry: DatasetEntry) -> SourceLink | None:
    """Return the best external source link for a catalog entry."""
    if entry.hf_id:
        return SourceLink(
            url=f"https://huggingface.co/datasets/{entry.hf_id}",
            label=entry.hf_id,
            kind="huggingface",
        )
    if entry.hf_repo:
        return SourceLink(
            url=f"https://huggingface.co/datasets/{entry.hf_repo}",
            label=entry.hf_repo,
            kind="huggingface",
        )
    if entry.problems_hf_id:
        return SourceLink(
            url=f"https://huggingface.co/datasets/{entry.problems_hf_id}",
            label=entry.problems_hf_id,
            kind="huggingface",
        )
    if entry.loader in _GITHUB_LOADER_REPOS:
        repo = _GITHUB_LOADER_REPOS[entry.loader]
        return SourceLink(
            url=f"https://github.com/{repo}",
            label=repo,
            kind="github",
        )
    if entry.docs and entry.docs.startswith(("http://", "https://")):
        return SourceLink(url=entry.docs, label=entry.docs, kind="web")
    return None


def source_link_payload(entry: DatasetEntry) -> dict[str, Any] | None:
    """Serialize a source link for API responses."""
    link = resolve_source_link(entry)
    if link is None:
        return None
    return {"url": link.url, "label": link.label, "kind": link.kind}
