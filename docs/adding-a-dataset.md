# Adding a Dataset

**Start here:** [`dataset-system.md`](dataset-system.md) — full reference with contracts, templates, archetype table, and pitfalls. You should not need to read loader/page source files if you follow that doc.

## Checklist

- [ ] **Config** — add entry to [`config/datasets.yaml`](../config/datasets.yaml) (`id`, `label`, `loader`, `icon`, `archetype`, HF metadata)
- [ ] **Loader** — `src/dataset_visualizer/loaders/<module>.py` with `@st.cache_data`, `cache_dir()`, normalized `DataFrame`, zero-arg defaults
- [ ] **Registry** — import + `LOADER_REGISTRY` line in [`registry.py`](../src/dataset_visualizer/registry.py)
- [ ] **Page** — `src/dataset_visualizer/pages/<category>/<id>.py` using `render_dataset_page()`
- [ ] **Inspect CLI** — `LOADER_CACHE_KEYS` in [`scripts/inspect_dataset.py`](../scripts/inspect_dataset.py) if cache key ≠ loader name
- [ ] **Tests** — `tests/test_loaders_<module>.py` with mocked HF calls and `load_*.clear()`
- [ ] **Docs** — `docs/datasets/<name>.md`, link from [`index.md`](index.md), update [`README.md`](../README.md) table

`app.py` does **not** need changes.

## Pick an archetype

See the [archetype reference](dataset-system.md#archetype-reference) in `dataset-system.md` for normalized columns, components, and which existing `id` to mirror.

| Archetype | Reference `id` |
|-----------|----------------|
| MCQ | `mmlu` |
| MCQ + CoT | `mmlu_pro` |
| MCQ multilingual | `global_mmlu`, `mmmlu` |
| Code generation | `livecodebench_v6` |
| Issue resolution | `swe_bench_verified` |
| Math + model runs | `arxivmath_0526` |
| Math final-answer | `aime_2026` |

## Verify

```bash
uv run pytest
uv run ruff check src tests scripts
uv run python scripts/inspect_dataset.py <dataset_id>
```
