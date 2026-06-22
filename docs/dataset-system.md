# Dataset System Reference

Read this document **before** opening loader or API source files. It describes every touchpoint, contract, and template needed to add or modify a dataset. Per-dataset schema notes live under [`datasets/`](datasets/).

## Mental model

The app is a **config-driven dataset explorer** with a **Gradio Server** backend and a **Next.js** React frontend. It is not an evaluation harness. Each dataset: download from Hugging Face → normalize to a `pandas.DataFrame` → serve JSON via `@app.api()` endpoints → render overview charts and per-sample inspection in the browser.

```
config/datasets.yaml
       │
       ├─► config.py              validates DatasetEntry (Pydantic)
       ├─► registry.py            LOADER_REGISTRY (inspect CLI + home row counts)
       ├─► loaders/<module>.py    @loader_cache + cache_dir() + normalization
       ├─► api/service.py         controls, filters, overview, samples per dataset id
       ├─► server.py              gradio.Server + @app.api() routes
       └─► frontend/              Next.js UI (@gradio/client → server APIs)
```

Navigation is automatic: `get_catalog()` reads YAML categories and the React sidebar renders one link per dataset entry. **No per-dataset edits** are needed in `server.py` or the frontend router beyond registering handler logic in `api/service.py` and adding the dataset id to `frontend/app/dataset/[id]/page.tsx` → `DATASET_IDS` for static export.

## Complete touchpoint checklist

Every new dataset requires edits in **all** of these places. Missing one causes a runtime, build, or CLI failure.

| # | File | What to add |
|---|------|-------------|
| 1 | `config/datasets.yaml` | YAML entry (`id`, `label`, `loader`, `description`, …) |
| 2 | `src/dataset_visualizer/loaders/<module>.py` | Loader function(s) returning normalized `DataFrame` |
| 3 | `src/dataset_visualizer/registry.py` | Import + `LOADER_REGISTRY["<loader>"] = <function>` |
| 4 | `src/dataset_visualizer/api/service.py` | Handler wiring: `_load_context`, `_id_column`, controls, filters, overview, sample extras |
| 5 | `frontend/app/dataset/[id]/page.tsx` | Add `id` to `DATASET_IDS` (required for `output: "export"`) |
| 6 | `frontend/components/` | New viewer only if archetype is not covered (see [Frontend viewers](#frontend-viewers)) |
| 7 | `scripts/inspect_dataset.py` | `LOADER_CACHE_KEYS` entry (if cache key ≠ loader name) |
| 8 | `tests/test_loaders_<module>.py` | Mocked HF download tests |
| 9 | `tests/test_api_service.py` | Optional smoke test for overview/meta if behavior is non-trivial |
| 10 | `docs/datasets/<name>.md` + link in `docs/index.md` | Schema notes |

**Also update** `README.md` dataset table when adding a user-facing dataset.

**Do not edit** `server.py` for new datasets unless you add a brand-new API endpoint. Existing routes are dataset-agnostic.

## Naming conventions

| Concept | Convention | Example |
|---------|------------|---------|
| Config `id` | `snake_case`; unique globally; version/variant in name | `swe_bench_verified`, `livecodebench_v6` |
| Config `loader` | `snake_case`; registry key; often without version | `livecodebench`, `swe_bench_verified` |
| Loader module | `loaders/<module>.py` | `loaders/swe_bench.py` |
| Loader function | `load_<dataset>()` or `load_<family>_<variant>()` | `load_swe_bench_verified()` |
| Cache directory | `data/cache/<key>/` via `cache_dir("<key>")` | `swe_bench` (shared by three SWE loaders) |
| `archetype` | Free-form tag; drives React sample viewer selection | `mcq`, `issue_resolution` |
| Inspect CLI arg | Config `id`, **not** loader name | `swe_bench_verified` |
| API `dataset_id` | Same as config `id` | `mmlu`, `gpqa_diamond` |

**`id` vs `loader`:** Multiple config entries may share one loader module but each needs a **distinct** `loader` registry key if defaults differ (see [Variant datasets](#variant-datasets-one-module-multiple-registry-keys) below).

## Config schema (`DatasetEntry`)

Defined in `src/dataset_visualizer/config.py`. Required fields: `id`, `label`, `loader`, `description`.

| Field | Required | Purpose |
|-------|----------|---------|
| `id` | yes | API key, frontend route, inspect CLI argument; must be globally unique |
| `label` | yes | Sidebar and page title |
| `loader` | yes | Key in `LOADER_REGISTRY` |
| `description` | yes | Shown at the top of the dataset page (1–3 sentences) |
| `icon` | no | Sidebar emoji in React nav |
| `archetype` | no | Guides overview/sample viewer selection |
| `hf_id` | no | Shown on home page |
| `hf_repo` | no | HF repo when not a standard `datasets` id |
| `files` | no | File list within `hf_repo` |
| `problems_hf_id` | no | Primary HF id (multi-repo datasets) |
| `outputs_hf_id` | no | Secondary HF id (multi-repo datasets) |
| `license` | no | License string for home page |
| `docs` | no | Link to extended documentation |

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
5. Expose **zero-argument defaults** on the function registered in `LOADER_REGISTRY` — the inspect CLI calls `loader()` with no kwargs.
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

### Registry entry (`registry.py`)

```python
from dataset_visualizer.loaders.my_benchmark import load_my_benchmark

LOADER_REGISTRY: dict[str, Callable[..., pd.DataFrame]] = {
    # …
    "my_benchmark": load_my_benchmark,  # key must match config `loader`
}
```

### Inspect CLI cache mapping (`scripts/inspect_dataset.py`)

```python
LOADER_CACHE_KEYS: dict[str, str] = {
  # …
  "my_benchmark": "my_benchmark",  # omit if loader name == cache key
}
```

The CLI runs `loader()` then prints `cache_dir(LOADER_CACHE_KEYS.get(entry.loader, entry.loader))`.

## API handler contract (`api/service.py`)

Dataset-specific UI logic lives in `api/service.py`, not in Streamlit pages. When adding a dataset, wire these functions (search for a similar `id` and copy the pattern):

| Function | Purpose |
|----------|---------|
| `_load_context()` | Map `dataset_id` → loader call + optional `extras` (e.g. ArXiv outputs) |
| `_id_column()` | Column used for sample ID search in the inspector |
| `_controls_for_dataset()` | Pre-load selectors (split, language, locale) returned by `get_dataset_meta` |
| `_filter_schema()` | Filter definitions (multiselect, text, radio, date_range) |
| `_apply_filters()` | Apply filter payload to a DataFrame |
| `_build_overview()` | Dispatch to `_overview_<dataset>()` builder |
| `_overview_<dataset>()` | Return `{"metrics": [...], "charts": [...], "tables": [...]}` |
| `_sample_extras()` | Optional per-row payload (model runs, solution text, etc.) |

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
| `get_dataset_meta` | Description, archetype, controls, filter schema, `id_column` |
| `get_filter_options` | Unique values for multiselect/date filters after load |
| `get_overview` | Metrics, charts, tables for filtered data |
| `get_sample` | Row at index + extras |
| `find_sample` | Row by `id_column` value |
| `decode_private_tests` | LiveCodeBench private test decoding |

The React frontend calls these via `@gradio/client` (`frontend/lib/api.ts`).

### Minimal API wiring template

After adding the loader and config entry, extend `api/service.py`:

```python
# _id_column
"my_benchmark": "sample_id",

# _load_context loaders dict
"my_benchmark": lambda p: (load_my_benchmark(split=p.get("split", "test")), {}),

# _controls_for_dataset (if needed)
if dataset_id == "my_benchmark":
    return [{"name": "split", "label": "Split", "type": "select",
             "options": ["test", "dev"], "default": "test"}]

# _filter_schema
"my_benchmark": [{"name": "subjects", "label": "Subject",
                   "type": "multiselect", "column": "subject"}],

# _apply_filters — add multiselect branch if needed
# _build_overview builders dict
"my_benchmark": _overview_my_benchmark,

def _overview_my_benchmark(df: pd.DataFrame, _extras: dict[str, Any]) -> dict[str, Any]:
    return {
        "metrics": [{"label": "Total rows", "value": f"{len(df):,}"}],
        "charts": [value_counts_chart(df["subject"], title="Rows per subject")],
        "tables": [],
    }
```

## Frontend viewers

Sample rendering is archetype-driven in `frontend/components/SampleInspector.tsx`:

| Archetype | React component | Normalized columns |
|-----------|-----------------|-------------------|
| `mcq`, `mcq_multilingual` | `McqViewer` | `question`, `choices`, `answer_letter` |
| `mcq_cot` | `McqViewer` + CoT expander | above + `cot_content`; uses `options` column |
| `code_problem` | `CodeProblemViewer` | `question_content`, `starter_code`, `public_test_cases` |
| `issue_resolution` | `IssueViewer` | `instance_id`, `repo`, `problem_statement`, patches, test lists |
| `academic_qa` | `HleViewer` | `question`, `answer`, `has_image`, `answer_type` |
| `math_competition` | `MathViewer` or `ArxivMathViewer` | `problem`, `problem_idx`, `answer` |

Add a dedicated viewer under `frontend/components/viewers/` only when an existing archetype viewer cannot render your samples.

### Static export requirement

`frontend/next.config.ts` uses `output: "export"`. Every dataset route must be listed in `DATASET_IDS` inside `frontend/app/dataset/[id]/page.tsx` or the production build fails.

## Archetype reference

Pick the archetype closest to your dataset. The table lists **normalized columns** the loader must produce, **where to mirror logic**, and the sample `id_column`.

| Archetype | Normalized columns (loader output) | API overview helper | Reference `id` | `id_column` |
|-----------|-----------------------------------|---------------------|----------------|-------------|
| `mcq` | `question`, `choices` (list[str]), `answer_letter` (A–D) | `_overview_mmlu` | `mmlu`, `gpqa_diamond` | `subject` or `question` |
| `mcq_cot` | Above + `cot_content`, `options` | `_overview_mmlu_pro` | `mmlu_pro` | `question_id` |
| `mcq_multilingual` | MCQ columns + `language`, `split` | `_overview_global_mmlu` | `global_mmlu`, `mmmlu` | `sample_id` |
| `code_problem` | `question_content`, `starter_code`, `public_test_cases` (parsed list) | `_overview_livecodebench` | `livecodebench_v6` | `question_id` |
| `issue_resolution` | `instance_id`, `repo`, `problem_statement`, `patch`, test lists | `_overview_swe_bench` | `swe_bench_verified` | `instance_id` |
| `academic_qa` | `question`, `answer`, `answer_type`, `has_image` | `_overview_hle` | `hle` | `id` |
| `math_competition` | Problem fields + optional joined outputs | `_overview_aime` / `_overview_arxivmath` | `aime_2026`, `arxivmath_0526` | `problem_idx` |

### Column contracts (Python helpers)

**`components/mcq_viewer.py`** — `resolve_correct_letter()`, `format_options()`:

- `choices`: `list[str]` with 2–26 non-empty options (filters `"N/A"`).
- `answer_letter`: single letter; or raw `answer` int index 0–3.

**Code problems** — `public_test_cases`: list of `{"input", "output", "testtype"}` dicts.

**Issue resolution** — `fail_to_pass` / `pass_to_pass` as parsed lists; normalize SWE-bench column casing in the loader.

## Registered datasets (lookup)

| `id` | Category | `loader` | Archetype | Cache key |
|------|----------|----------|-----------|-----------|
| `mmlu` | reasoning | `mmlu` | mcq | `mmlu` |
| `mmlu_pro` | reasoning | `mmlu_pro` | mcq_cot | `mmlu_pro` |
| `gpqa_diamond` | reasoning | `gpqa` | mcq | `gpqa` |
| `global_mmlu` | reasoning | `global_mmlu` | mcq_multilingual | `global_mmlu` |
| `mmmlu` | reasoning | `mmmlu` | mcq_multilingual | `mmmlu` |
| `aime_2026` | reasoning | `aime_2026` | math_competition | `aime_2026` |
| `hle` | reasoning | `hle` | academic_qa | `hle` |
| `livecodebench_v6` | code | `livecodebench` | code_problem | `livecodebench` |
| `swe_bench_verified` | code | `swe_bench_verified` | issue_resolution | `swe_bench` |
| `swe_bench_multilingual` | code | `swe_bench_multilingual` | issue_resolution | `swe_bench` |
| `swe_bench_pro` | code | `swe_bench_pro` | issue_resolution | `swe_bench` |
| `arxivmath_0526` | math | `arxivmath` | math_competition | `arxivmath` |

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

Optional API smoke test in `tests/test_api_service.py`:

```python
def test_get_overview_my_benchmark(monkeypatch):
    monkeypatch.setattr("dataset_visualizer.api.service.load_my_benchmark", lambda **kw: sample_df)
    overview = get_overview("my_benchmark", {"split": "test"}, {})
    assert overview["metrics"]
```

Run: `uv run pytest`

## Variant datasets (one module, multiple registry keys)

When several config entries share download logic but differ in HF source or normalization (e.g. SWE-Bench Verified / Multilingual / PRO):

1. One loader module with a shared `_load_*()` helper and **separate** `@loader_cache` functions per variant.
2. **Separate** `LOADER_REGISTRY` keys matching each config `loader` field.
3. **Separate** handler branches in `api/service.py` (`_load_context`, overview, filters) — one per config `id`.
4. Add each config `id` to `DATASET_IDS` in the frontend.
5. Shared `LOADER_CACHE_KEYS` mapping all registry keys to one cache dir if appropriate.

Do **not** rely on a single loader with a `variant` config field unless you also update the inspect CLI to pass that variant (it currently does not).

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| Dataset missing from sidebar | Check `config/datasets.yaml` entry; `get_catalog()` reads it automatically |
| Frontend build fails on `/dataset/[id]` | Add `id` to `DATASET_IDS` in `frontend/app/dataset/[id]/page.tsx` |
| `get_dataset_meta` raises unknown id | Config `id` must match keys wired in `api/service.py` |
| Inspect CLI: "No loader registered" | `config.loader` must match `LOADER_REGISTRY` key exactly |
| Inspect CLI loads wrong data | Registered loader must work with `loader()` — no required kwargs |
| Gated HF datasets (e.g. GPQA) | Set `HF_TOKEN` in `.env`; document gating in dataset doc |
| Huge multilingual splits | Expose language/split as **controls** (pre-load), default to smaller split (`dev`) |
| JSON columns as strings | Parse in loader (`json.loads`, `ast.literal_eval`); store as `list`/`dict` in DataFrame |
| SWE-bench column casing | Verified/Multilingual: `FAIL_TO_PASS`; PRO: `fail_to_pass` — normalize in loader |
| Tests flaky across runs | Always call `load_<name>.clear()` after monkeypatching |
| Frontend cannot reach API | Dev: set `NEXT_PUBLIC_API_URL=http://localhost:7860`; prod: served from same origin |

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
3. Wire handler branches in `api/service.py` (mirror closest existing dataset).
4. Add `id` to `DATASET_IDS` in the frontend.
5. Walk the [touchpoint checklist](#complete-touchpoint-checklist).
6. Add tests using the [test contract](#test-contract).
7. Run `uv run pytest`, `uv run ruff check src tests scripts`, and `cd frontend && npm run build`.
8. Verify with inspect CLI and the running app.

Only open an existing loader/API handler when your dataset diverges from the archetype table (extra joins, custom decoding, gated access workarounds).
