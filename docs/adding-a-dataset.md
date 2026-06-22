# Adding a Dataset

**Start here:** [`dataset-system.md`](dataset-system.md) — full reference with contracts, templates, archetype table, and pitfalls. You should not need to read loader/API source files if you follow that doc.

## Checklist

- [ ] **Config** — add entry to [`config/datasets.yaml`](../config/datasets.yaml) (`id`, `label`, `loader`, `description`, `icon`, `archetype`, HF metadata)
- [ ] **Loader** — `src/dataset_visualizer/loaders/<module>.py` with `@loader_cache`, `cache_dir()`, normalized `DataFrame`, zero-arg defaults
- [ ] **Registry** — import + `LOADER_REGISTRY` line in [`registry.py`](../src/dataset_visualizer/registry.py)
- [ ] **API handlers** — wire `_load_context`, `_id_column`, controls, filters, overview in [`api/service.py`](../src/dataset_visualizer/api/service.py)
- [ ] **Frontend route** — add `id` to `DATASET_IDS` in [`frontend/app/dataset/[id]/page.tsx`](../frontend/app/dataset/[id]/page.tsx)
- [ ] **Frontend viewer** — only if no existing archetype viewer fits; see [`frontend.md`](frontend.md)
- [ ] **Inspect CLI** — `LOADER_CACHE_KEYS` in [`scripts/inspect_dataset.py`](../scripts/inspect_dataset.py) if cache key ≠ loader name
- [ ] **Tests** — `tests/test_loaders_<module>.py` with mocked HF calls and `load_*.clear()`
- [ ] **Docs** — `docs/datasets/<name>.md`, link from [`index.md`](index.md), update [`README.md`](../README.md) table

`server.py` and `app.py` do **not** need changes for standard datasets.

## Pick an archetype

See the [archetype reference](dataset-system.md#archetype-reference) in `dataset-system.md` for normalized columns, API overview helpers, and which existing `id` to mirror.

| Archetype | Reference `id` | Mirror in `api/service.py` |
|-----------|----------------|----------------------------|
| MCQ | `mmlu` | `_overview_mmlu` |
| MCQ + CoT | `mmlu_pro` | `_overview_mmlu_pro` |
| MCQ multilingual | `global_mmlu`, `mmmlu` | `_overview_global_mmlu` |
| Code generation | `livecodebench_v6` | `_overview_livecodebench` |
| Issue resolution | `swe_bench_verified` | `_overview_swe_bench` |
| Academic QA | `hle` | `_overview_hle` |
| Math + model runs | `arxivmath_0526` | `_overview_arxivmath` |
| Math final-answer | `aime_2026` | `_overview_aime` |

## Verify

```bash
uv run pytest
uv run ruff check src tests scripts
uv run python scripts/inspect_dataset.py <dataset_id>
cd frontend && npm run build
```

Run the app:

```bash
uv run dataset-viz
# optional dev frontend: cd frontend && NEXT_PUBLIC_API_URL=http://localhost:7860 npm run dev
```
