# Glossary

Domain terms used across the Dataset Visualizer codebase and docs. Read this once when onboarding — it prevents re-reading loaders to learn vocabulary.

## Catalog and config

| Term | Meaning |
|------|---------|
| **Config `id`** | Globally unique snake_case key for a dataset (`mmlu`, `arc_agi_2`). Used as API `dataset_id`, frontend route `/dataset/[id]`, and inspect CLI argument. |
| **Category** | Top-level grouping in `config/datasets.yaml` (`knowledge`, `reasoning`, `code`, `math`, …). Drives sidebar sections and the home-page table. |
| **`DatasetEntry`** | Pydantic model (`dataset_visualizer.config:DatasetEntry`) validating one YAML catalog row. |
| **Catalog** | Full list of categories and datasets returned by `get_catalog()`. |

## Loading and caching

| Term | Meaning |
|------|---------|
| **`loader` (config field)** | Module or strategy name documenting how rows are fetched (`mmlu`, `hf_benchmark`, `swe_bench_verified`). May differ from config `id` when several ids share one module. |
| **Manual loader** | Hand-written module in `loaders/<name>.py` with custom normalization (13 datasets today). |
| **`hf_benchmark` loader** | Config-driven path: YAML entry with `loader: hf_benchmark` auto-registers via `build_dataset_registry()` — no new Python loader file for standard Hub datasets (38 datasets today). |
| **`@loader_cache`** | In-process memoization decorator on load functions for the server lifetime. Cleared in tests via `load_<name>.clear()`. |
| **`cache_dir(key)`** | Creates and returns `data/cache/<key>/` for on-disk artifacts; inspect CLI prints this path. |
| **`cache_key`** | Optional `DatasetDescriptor.cache_key` when the on-disk cache dir should differ from the config `loader` field (e.g. three SWE-bench variants share `swe_bench`). |

## API registration

| Term | Meaning |
|------|---------|
| **`DatasetDescriptor`** | Per-dataset API contract: `loader`, `overview`, `viewer`, `id_column`, `controls`, `filters`, optional `sample_extras` and `cache_key`. |
| **`DATASET_REGISTRY`** | Dict of config `id` → `DatasetDescriptor`, built from manual entries plus auto-registered `hf_benchmark` rows. |
| **`id_column`** | DataFrame column used by `find_sample` (API only; the UI browses by index). |
| **Controls** | Pre-load UI selects (split, language, locale, …) passed to `loader(params)` as a dict. |
| **Filters** | Post-load schema-driven filters (multiselect, text, radio, date_range) applied in `api/filters.py`. |
| **Extras** | Second dict returned by `loader` — joined data not in the main frame (e.g. ArXiv model outputs). |

## Normalization and presentation

| Term | Meaning |
|------|---------|
| **Archetype** | YAML tag describing benchmark shape (`mcq`, `code_eval`, `generic`, …). Shown as a UI badge; fallback for `viewer` when not set. |
| **`viewer`** | API/frontend key selecting the React sample component (`mcq`, `code_eval`, `arc_grid`, …). YAML `viewer` can override archetype for special cases. |
| **`profile`** | Normalization strategy for `hf_benchmark` rows (`arc`, `gsm`, `code_eval`, `generic`, …). Passed to `normalize_benchmark()` in `loaders/benchmark_normalize.py`. |
| **Normalized columns** | Stable DataFrame column names after the loader (e.g. `question`, `choices`, `answer_letter` for MCQ). Contracts live in [dataset-system.md § Column contracts](dataset-system.md#column-contracts-python-helpers). |
| **Overview** | JSON payload of `metrics` and optional `tables` for the Overview tab. Built per dataset or via `overview_generic()` for `hf_benchmark` entries. The Hub README is fetched separately via `get_dataset_meta`. |

## Frontend and tooling

| Term | Meaning |
|------|---------|
| **Gradio Server** | FastAPI-backed `gradio.Server` exposing `@app.api` endpoints consumed by `@gradio/client`. |
| **Static export** | Next.js `output: "export"` — dataset routes pre-rendered at build time via `generateStaticParams()`. |
| **Inspect CLI** | `scripts/inspect_dataset.py` — prints schema, dtypes, sample row, and cache path for any config `id`. |

## Related docs

- [Architecture overview](architecture/overview.md) — system boundaries and data flow
- [Code map](architecture/code-map.md) — capability → file lookup
- [Dataset system reference](dataset-system.md) — contracts and touchpoints
- [How to add a dataset](how-to/add-dataset.md) — step-by-step recipes
