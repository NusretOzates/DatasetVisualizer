# Adding a Dataset

**Start here:** [`dataset-system.md`](dataset-system.md) — full reference with contracts, templates, archetype table, and pitfalls. You should not need to read loader/API source files if you follow that doc.

## Checklist

- [ ] **Config** — add entry to [`config/datasets.yaml`](../config/datasets.yaml) (`id`, `label`, `loader`, `description`, `icon`, `archetype`, HF metadata)
- [ ] **Loader** — `src/dataset_visualizer/loaders/<module>.py` with `@loader_cache`, `cache_dir()`, normalized `DataFrame`, safe defaults for `loader({})`
- [ ] **API registry** — `DatasetDescriptor` entry in [`api/dataset_registry.py`](../src/dataset_visualizer/api/dataset_registry.py) (`loader`, `overview`, `viewer`, controls, filters, …)
- [ ] **Overview builder** — `overview_<dataset>()` in [`api/overview.py`](../src/dataset_visualizer/api/overview.py) (or reuse an existing builder)
- [ ] **Frontend viewer** — only if no existing `viewer` key fits; register in [`components/viewers/registry.tsx`](../frontend/components/viewers/registry.tsx)
- [ ] **Inspect CLI** — `LOADER_CACHE_KEYS` in [`scripts/inspect_dataset.py`](../scripts/inspect_dataset.py) if cache key ≠ config `loader` field
- [ ] **Tests** — `tests/test_loaders_<module>.py` with mocked HF calls and `load_*.clear()`; optional smoke tests in `tests/test_api_service.py`
- [ ] **Docs** — `docs/datasets/<name>.md`, link from [`index.md`](index.md), update [`README.md`](../README.md) table

`server.py` does **not** need changes for standard datasets. Frontend routes are generated from `get_catalog` at build time — no manual route list.

## Pick an archetype

See the [archetype reference](dataset-system.md#archetype-reference) in `dataset-system.md` for normalized columns, overview helpers, and which existing `id` to mirror.

| Archetype | Reference `id` | Mirror in `dataset_registry.py` |
|-----------|----------------|--------------------------------|
| MCQ | `mmlu` | `viewer="mcq"`, `overview_mmlu` |
| MCQ + CoT | `mmlu_pro` | `viewer="mcq_cot"`, `overview_mmlu_pro` |
| MCQ multilingual | `global_mmlu`, `mmmlu` | `viewer="mcq"`, `overview_global_mmlu` / `overview_mmmlu` |
| Code generation | `livecodebench_v6` | `viewer="code_problem"`, `overview_livecodebench` |
| Issue resolution | `swe_bench_verified` | `viewer="issue_resolution"`, `overview_swe_bench` |
| Academic QA | `hle` | `viewer="academic_qa"`, `overview_hle` |
| Math + model runs | `arxivmath_0526` | `viewer="arxiv_math"`, `overview_arxivmath` |
| Math final-answer | `aime_2026` | `viewer="math_competition"`, `overview_aime` |

## Verify

```bash
uv run pytest
uv run ruff check src tests scripts
uv run python scripts/inspect_dataset.py <dataset_id>
```

Frontend (backend must be running for static route export):

```bash
uv run dataset-viz   # terminal 1
cd frontend && NEXT_PUBLIC_API_URL=http://localhost:7860 npm run build
```

Run the app:

```bash
uv run dataset-viz
# optional dev frontend: cd frontend && NEXT_PUBLIC_API_URL=http://localhost:7860 npm run dev
```

## Documentation

Update [`dataset-system.md`](dataset-system.md), this checklist, and [`README.md`](../README.md) whenever you add or change dataset registration steps.
