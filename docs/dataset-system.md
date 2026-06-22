# Dataset System Reference

Read this document **before** opening loader or API source files. It describes every touchpoint, contract, and template needed to add or modify a dataset. Per-dataset schema notes live under [`datasets/`](datasets/).

## Mental model

The app is a **config-driven dataset explorer** with a **Gradio Server** backend and a **Next.js** React frontend. It is not an evaluation harness. Each dataset: download from Hugging Face → normalize to a `pandas.DataFrame` → serve JSON via `@app.api()` endpoints → render overview charts and per-sample inspection in the browser.

```
config/datasets.yaml
       │
       ├─► config.py                    validates DatasetEntry (Pydantic)
       ├─► api/dataset_registry.py      DATASET_REGISTRY (single registration per id)
       ├─► loaders/<module>.py          @loader_cache + cache_dir() + normalization
       ├─► api/service.py               orchestration (catalog, meta, samples)
       ├─► api/filters.py               schema-driven filtering
       ├─► api/overview.py              per-dataset overview builders
       ├─► server.py                    gradio.Server + @app.api() routes
       └─► frontend/                    Next.js UI (@gradio/client → server APIs)
```

Navigation is automatic: `get_catalog()` reads YAML categories and the React sidebar renders one link per dataset entry. **No per-dataset edits** are needed in `server.py`. Frontend routes are generated at build time from `get_catalog()` via `generateStaticParams()` — no manual route list.

## Complete touchpoint checklist

Every new dataset requires edits in **all** of these places. Missing one causes a runtime, build, or CLI failure.

| # | File | What to add |
|---|------|-------------|
| 1 | `config/datasets.yaml` | YAML entry (`id`, `label`, `loader`, `description`, …) |
| 2 | `src/dataset_visualizer/loaders/<module>.py` | Loader function(s) returning normalized `DataFrame` |
| 3 | `src/dataset_visualizer/api/dataset_registry.py` | `DatasetDescriptor` with loader, overview, viewer, controls, filters |
| 4 | `src/dataset_visualizer/api/overview.py` | `overview_<dataset>()` builder (or reuse existing) |
| 5 | `frontend/components/viewers/` | New viewer + `registry.tsx` entry only if `viewer` key is new |
| 6 | `scripts/inspect_dataset.py` | `LOADER_CACHE_KEYS` entry (if cache key ≠ config `loader` field) |
| 7 | `tests/test_loaders_<module>.py` | Mocked HF download tests |
| 8 | `tests/test_api_service.py` | Optional smoke test for overview/meta if behavior is non-trivial |
| 9 | `docs/datasets/<name>.md` + link in `docs/index.md` | Schema notes |
| 10 | `README.md` | Dataset table row when user-facing |

**Also update** `docs/dataset-system.md`, `docs/adding-a-dataset.md`, `docs/backend.md`, or `docs/frontend.md` when registration steps or architecture change.

**Do not edit** `server.py` for new datasets unless you add a brand-new API endpoint. Existing routes are dataset-agnostic.

## Naming conventions

| Concept | Convention | Example |
|---------|------------|---------|
| Config `id` | `snake_case`; unique globally; version/variant in name | `swe_bench_verified`, `livecodebench_v6` |
| Config `loader` | `snake_case`; documents loader module; used by inspect CLI cache mapping | `livecodebench`, `swe_bench_verified` |
| Registry key | Same as config `id` | `mmlu`, `gpqa_diamond` |
| Loader module | `loaders/<module>.py` | `loaders/swe_bench.py` |
| Loader function | `load_<dataset>()` or `load_<family>_<variant>()` | `load_swe_bench_verified()` |
| Cache directory | `data/cache/<key>/` via `cache_dir("<key>")` | `swe_bench` (shared by three SWE loaders) |
| `archetype` | Free-form tag in YAML; shown in UI badges | `mcq`, `issue_resolution` |
| API `viewer` | Key in `DatasetDescriptor`; drives React viewer | `mcq`, `code_problem`, `arxiv_math` |
| Inspect CLI arg | Config `id`, **not** loader name | `swe_bench_verified` |
| API `dataset_id` | Same as config `id` | `mmlu`, `gpqa_diamond` |

**`id` vs `loader`:** The config `loader` field documents which loader module backs the dataset and maps to `LOADER_CACHE_KEYS` in the inspect CLI. API registration always uses config `id` as the `DATASET_REGISTRY` key. Multiple config entries may share one loader module (e.g. three SWE-bench variants) but each needs its own `DatasetDescriptor`.

## Config schema (`DatasetEntry`)

Defined in `src/dataset_visualizer/config.py`. Required fields: `id`, `label`, `loader`, `description`.

| Field | Required | Purpose |
|-------|----------|---------|
| `id` | yes | API key, frontend route, inspect CLI argument; must be globally unique |
| `label` | yes | Sidebar and page title |
| `loader` | yes | Loader module name; inspect CLI cache mapping |
| `description` | yes | Shown at the top of the dataset page (1–3 sentences) |
| `icon` | no | Sidebar emoji in React nav |
| `archetype` | no | UI badge; fallback when `viewer` is absent |
| `hf_id` | no | Shown on home page |
| `hf_repo` | no | HF repo when not a standard `datasets` id |
| `files` | no | File list within `hf_repo` |
| `problems_hf_id` | no | Primary HF id (multi-repo datasets) |
| `outputs_hf_id` | no | Secondary HF id (multi-repo datasets) |
| `license` | no | License string for home page |
| `docs` | no | Link to extended documentation |
| `row_count` | no | Fallback for home page when loader fails |

Example entry:

```yaml
categories:
  reasoning:
    - id: my_benchmark
      label: My Benchmark
      loader: my_benchmark
      icon: "🧠"
      archetype: mcq
      hf_id: org/my-benchmark
      description: >
        One- to three-sentence summary of what the benchmark measures and any
        access notes (gated, multilingual, etc.).
```

## Loader contract

### Requirements

1. Decorate the public load function with `@loader_cache(show_spinner="Downloading …")`.
2. Call `cache_dir("<cache_key>")` early (creates `data/cache/<cache_key>/`).
3. Download via `datasets.load_dataset` and/or `huggingface_hub.hf_hub_download`.
4. Return a **normalized** `pandas.DataFrame` with stable column names for API handlers and frontend viewers.
5. Work with **default arguments** — the inspect CLI and home-page row counts call `descriptor.loader({})`.
6. Parse JSON-in-string columns in the loader, not in the API layer.

### Minimal loader template

```python
"""My benchmark loader."""

from __future__ import annotations

import pandas as pd
from datasets import load_dataset

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache

MY_HF_ID = "org/my-benchmark"


@loader_cache(show_spinner="Downloading My Benchmark …")
def load_my_benchmark(split: str = "test") -> pd.DataFrame:
    """Load and normalize My Benchmark.

    Args:
        split: Dataset split to load.

    Returns:
        Normalized DataFrame ready for API handlers and frontend viewers.
    """
    cache_dir("my_benchmark")
    dataset = load_dataset(MY_HF_ID, split=split)
    df = dataset.to_pandas()
    df["split"] = split
    return df
```

### Registry entry (`api/dataset_registry.py`)

```python
from dataset_visualizer.api.overview import overview_my_benchmark
from dataset_visualizer.loaders.my_benchmark import load_my_benchmark

def _controls_my_benchmark() -> list[dict[str, Any]]:
    return [
        {
            "name": "split",
            "label": "Split",
            "type": "select",
            "options": ["test", "dev"],
            "default": "test",
        }
    ]

DATASET_REGISTRY: dict[str, DatasetDescriptor] = {
    # …
    "my_benchmark": DatasetDescriptor(
        id_column="sample_id",
        viewer="mcq",
        loader=lambda p: (load_my_benchmark(split=p.get("split", "test")), {}),
        overview=overview_my_benchmark,
        controls=_controls_my_benchmark,
        filters=[
            {"name": "subjects", "label": "Subject", "type": "multiselect", "column": "subject"},
        ],
    ),
}
```

The `loader` callable receives UI control values as a dict and returns `(DataFrame, extras_dict)`. Use `extras` for joined data (e.g. ArXiv model outputs).

### Inspect CLI cache mapping (`scripts/inspect_dataset.py`)

```python
LOADER_CACHE_KEYS: dict[str, str] = {
  # …
  "my_benchmark": "my_benchmark",  # omit if config loader field == cache key
}
```

The CLI calls `get_descriptor(dataset_id).loader({})` then prints `cache_dir(LOADER_CACHE_KEYS.get(entry.loader, entry.loader))`.

## API handler contract

Dataset-specific behaviour is registered in `api/dataset_registry.py` and implemented in focused modules:

| Module | Responsibility |
|--------|----------------|
| `api/dataset_registry.py` | `DatasetDescriptor` per config `id` |
| `api/service.py` | Catalog, meta, filter options, overview, samples (no per-id branches) |
| `api/filters.py` | `apply_filters(df, schema, filters)` — multiselect, text, radio (`value_map`), date_range |
| `api/overview.py` | `overview_<dataset>(df, extras)` builders |
| `api/serializers.py` | JSON-safe row/value serialization |

### Filter schema

Supported `type` values:

| Type | Schema fields | Behaviour |
|------|---------------|-----------|
| `multiselect` | `column` | Subset rows where column value is in selected list |
| `text` | `column` | Prefix match on string column |
| `radio` | `column`, `options`, `value_map` (optional) | Map option label → column value (e.g. HLE modality on `has_image`) |
| `date_range` | `column` | Inclusive start/end dates on datetime column |

Filter options for multiselect/radio/date_range are built in `service._filter_options_from_df()` from the loaded DataFrame.

### Overview payload shape

```python
{
    "metrics": [{"label": "Total rows", "value": "1,234"}],
    "charts": [
        {
            "type": "bar",  # bar | pie | histogram | stacked_bar | timeline | scatter
            "title": "Rows per subject",
            "categories": ["math", "physics"],
            "values": [100, 200],
        }
    ],
    "tables": [
        {
            "title": "All problems",
            "columns": ["problem_idx", "problem_preview"],
            "rows": [{"problem_idx": "1", "problem_preview": "…"}],
        }
    ],
}
```

Build charts with helpers in `api/chart_data.py`. Serialize table rows with `api/serializers.serialize_rows()`.

### Gradio API endpoints (`server.py`)

| Endpoint | Purpose |
|----------|---------|
| `get_catalog` | Navigation + home table rows |
| `get_dataset_meta` | Description, archetype, `viewer`, controls, filter schema, `id_column` |
| `get_filter_options` | Unique values for multiselect/date filters after load |
| `get_overview` | Metrics, charts, tables for filtered data |
| `get_sample` | Row at index + extras |
| `find_sample` | Row by `id_column` value |
| `decode_private_tests` | LiveCodeBench private test decoding |

The React frontend calls these via `@gradio/client` (`frontend/lib/api.ts`).

### Minimal overview builder (`api/overview.py`)

```python
def overview_my_benchmark(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    return {
        "metrics": [{"label": "Total rows", "value": f"{len(df):,}"}],
        "charts": [value_counts_chart(df["subject"], title="Rows per subject")],
        "tables": [],
    }
```

Wire it in `dataset_registry.py` as `overview=overview_my_benchmark`.

## Frontend viewers

Sample rendering uses the API `viewer` field (fallback: YAML `archetype`) via `components/viewers/registry.tsx`:

| `viewer` | React component | Normalized columns |
|----------|-----------------|-------------------|
| `mcq` | `McqViewer` | `question`, `choices`, `answer_letter` |
| `mcq_cot` | `McqCotViewer` | above + `cot_content`; uses `options` column |
| `code_problem` | `CodeProblemSampleViewer` | `question_content`, `starter_code`, `public_test_cases` |
| `issue_resolution` | `IssueViewer` | `instance_id`, `repo`, `problem_statement`, patches, test lists |
| `academic_qa` | `HleViewer` | `question`, `answer`, `has_image`, `answer_type` |
| `math_competition` | `MathViewer` | `problem`, `problem_idx`, `answer` |
| `arxiv_math` | `ArxivMathViewer` | problem fields + model-run tables from extras |

Add a dedicated viewer under `frontend/components/viewers/` only when an existing viewer cannot render your samples. Register it in `registry.tsx`.

### Static export requirement

`frontend/next.config.ts` uses `output: "export"`. Dataset routes are generated by `generateStaticParams()` in `app/dataset/[id]/page.tsx`, which calls `fetchCatalog()` at build time. **Start the backend** (or set `NEXT_PUBLIC_API_URL` to a running server) before `npm run build` so new datasets get exported routes.

## Archetype reference

Pick the archetype closest to your dataset. The table lists **normalized columns** the loader must produce, **where to mirror logic**, and the sample `id_column`.

| Archetype | Normalized columns (loader output) | Overview helper | Reference `id` | `viewer` | `id_column` |
|-----------|-----------------------------------|-----------------|----------------|----------|-------------|
| `mcq` | `question`, `choices` (list[str]), `answer_letter` (A–D) | `overview_mmlu` | `mmlu`, `gpqa_diamond` | `mcq` | `subject` or `question` |
| `mcq_cot` | Above + `cot_content`, `options` | `overview_mmlu_pro` | `mmlu_pro` | `mcq_cot` | `question_id` |
| `mcq_multilingual` | MCQ columns + `language`/`locale`, `split` | `overview_global_mmlu` / `overview_mmmlu` | `global_mmlu`, `mmmlu` | `mcq` | `sample_id` |
| `code_problem` | `question_content`, `starter_code`, `public_test_cases` (parsed list) | `overview_livecodebench` | `livecodebench_v6` | `code_problem` | `question_id` |
| `issue_resolution` | `instance_id`, `repo`, `problem_statement`, `patch`, test lists | `overview_swe_bench` | `swe_bench_verified` | `issue_resolution` | `instance_id` |
| `academic_qa` | `question`, `answer`, `answer_type`, `has_image` | `overview_hle` | `hle` | `academic_qa` | `id` |
| `math_competition` | Problem fields + optional joined outputs | `overview_aime` / `overview_arxivmath` | `aime_2026`, `arxivmath_0526` | `math_competition` / `arxiv_math` | `problem_idx` |

### Column contracts (Python helpers)

**`utils/mcq.py`** — `resolve_correct_letter()`, `format_options()`:

- `choices`: `list[str]` with 2–26 non-empty options (filters `"N/A"`).
- `answer_letter`: single letter; or raw `answer` int index 0–3.

**Code problems** — `public_test_cases`: list of `{"input", "output", "testtype"}` dicts.

**Issue resolution** — `fail_to_pass` / `pass_to_pass` as parsed lists; normalize SWE-bench column casing in the loader.

## Registered datasets (lookup)

| `id` | Category | Config `loader` | Archetype | `viewer` | Cache key |
|------|----------|-------------------|-----------|----------|-----------|
| `mmlu` | reasoning | `mmlu` | mcq | `mcq` | `mmlu` |
| `mmlu_pro` | reasoning | `mmlu_pro` | mcq_cot | `mcq_cot` | `mmlu_pro` |
| `gpqa_diamond` | reasoning | `gpqa` | mcq | `mcq` | `gpqa` |
| `global_mmlu` | reasoning | `global_mmlu` | mcq_multilingual | `mcq` | `global_mmlu` |
| `mmmlu` | reasoning | `mmmlu` | mcq_multilingual | `mcq` | `mmmlu` |
| `aime_2026` | reasoning | `aime_2026` | math_competition | `math_competition` | `aime_2026` |
| `hle` | reasoning | `hle` | academic_qa | `academic_qa` | `hle` |
| `livecodebench_v6` | code | `livecodebench` | code_problem | `code_problem` | `livecodebench` |
| `swe_bench_verified` | code | `swe_bench_verified` | issue_resolution | `issue_resolution` | `swe_bench` |
| `swe_bench_multilingual` | code | `swe_bench_multilingual` | issue_resolution | `issue_resolution` | `swe_bench` |
| `swe_bench_pro` | code | `swe_bench_pro` | issue_resolution | `issue_resolution` | `swe_bench` |
| `arxivmath_0526` | math | `arxivmath` | math_competition | `arxiv_math` | `arxivmath` |

## Test contract

File: `tests/test_loaders_<module>.py`. Mock Hugging Face — never hit the network in tests.

```python
def test_load_my_benchmark(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = pd.DataFrame({"question": ["Q1"], "choices": [["a", "b"]], "answer": [0]})

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.my_benchmark.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    load_my_benchmark.clear()  # clear @loader_cache between tests

    df = load_my_benchmark(split="test")
    assert len(df) == 1
    assert "answer_letter" in df.columns
```

Also test private normalization helpers (`_parse_*`, `_normalize_*_frame`) with unit inputs — no mocking needed.

Optional API smoke test in `tests/test_api_service.py` — patch `_load_context` or the descriptor loader:

```python
def test_get_overview_my_benchmark(monkeypatch):
    monkeypatch.setattr(
        "dataset_visualizer.api.service._load_context",
        lambda dataset_id, params: DatasetContext(df=sample_df, extras={}),
    )
    overview = get_overview("my_benchmark", {"split": "test"}, {})
    assert overview["metrics"]
```

Run: `uv run pytest`

## Variant datasets (one module, multiple descriptors)

When several config entries share download logic but differ in HF source or normalization (e.g. SWE-Bench Verified / Multilingual / PRO):

1. One loader module with a shared `_load_*()` helper and **separate** `@loader_cache` functions per variant.
2. **Separate** `DatasetDescriptor` entries — one per config `id`.
3. Shared `LOADER_CACHE_KEYS` mapping all config `loader` values to one cache dir if appropriate.
4. Rebuild the frontend with the backend running so each new `id` is exported.

Do **not** rely on a single descriptor with a `variant` param unless the inspect CLI and `loader({})` defaults handle it (they use empty params today).

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| Dataset missing from sidebar | Check `config/datasets.yaml` entry; `get_catalog()` reads it automatically |
| Frontend build missing `/dataset/[id]` | Start backend before `npm run build`; `generateStaticParams` calls `get_catalog` |
| `get_dataset_meta` raises unknown id | Add `DatasetDescriptor` in `api/dataset_registry.py` for that config `id` |
| Inspect CLI: "No API descriptor registered" | Register the config `id` in `DATASET_REGISTRY` |
| Inspect CLI loads wrong data | `descriptor.loader({})` must work with empty params |
| Gated HF datasets (e.g. GPQA) | Set `HF_TOKEN` in `.env`; document gating in dataset doc |
| Huge multilingual splits | Expose language/split as **controls** (pre-load), default to smaller split (`dev`) |
| JSON columns as strings | Parse in loader (`json.loads`, `ast.literal_eval`); store as `list`/`dict` in DataFrame |
| SWE-bench column casing | Verified/Multilingual: `FAIL_TO_PASS`; PRO: `fail_to_pass` — normalize in loader |
| Tests flaky across runs | Always call `load_<name>.clear()` after monkeypatching |
| Frontend cannot reach API | Dev: set `NEXT_PUBLIC_API_URL=http://localhost:7860`; prod: served from same origin |
| Overview stale after control change | Frontend refetches overview when `{params, filters}` changes |
| Docs out of date | Update `docs/` and `README.md` with every architecture or workflow change |

## Documentation for a new dataset

Create `docs/datasets/<short_name>.md` with:

- HF source URL and archetype
- Normalized column table (post-loader schema, not raw HF schema)
- Visualization rationale (why each chart exists)
- Loader call signature and defaults
- Cache path
- Access notes (gated, large download, etc.)

Link from `docs/index.md`. Run inspect CLI on real data to verify columns:

```bash
uv run python scripts/inspect_dataset.py <dataset_id>
```

## Quick add workflow

1. Read archetype row in [Archetype reference](#archetype-reference) above.
2. Copy loader template from this doc; adjust normalization columns.
3. Add `DatasetDescriptor` in `api/dataset_registry.py` and overview builder in `api/overview.py`.
4. Walk the [touchpoint checklist](#complete-touchpoint-checklist).
5. Add tests using the [test contract](#test-contract).
6. Update docs (`docs/datasets/`, `docs/index.md`, `README.md`).
7. Run `uv run pytest`, `uv run ruff check src tests scripts`, and `cd frontend && npm run build` (with backend running).
8. Verify with inspect CLI and the running app.

Only open an existing loader when your dataset diverges from the archetype table (extra joins, custom decoding, gated access workarounds).
