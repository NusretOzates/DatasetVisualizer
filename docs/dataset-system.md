# Dataset System Reference

Read this document **before** opening loader or page source files. It describes every touchpoint, contract, and template needed to add or modify a dataset. Per-dataset schema notes live under [`datasets/`](datasets/).

## Mental model

The app is a **config-driven Streamlit explorer**, not an evaluation harness. Each dataset is: download from Hugging Face → normalize to a `pandas.DataFrame` → render overview charts + per-sample inspector.

```
config/datasets.yaml
       │
       ├─► config.py          validates DatasetEntry (Pydantic)
       ├─► registry.py        LOADER_REGISTRY + build_navigation()
       └─► app.py             calls build_navigation() — no per-dataset edits

pages/<category>/<id>.py  ──calls──►  loaders/<loader>.py  ──writes──►  data/cache/<key>/
       │                                      │
       └─ components/ (mcq_viewer, charts, …) ┘
```

Navigation is automatic: each YAML entry becomes `st.Page(pages/<category>/<id>.py)` in a sidebar group titled from the category key (e.g. `reasoning` → "Reasoning").

## Complete touchpoint checklist

Every new dataset requires edits in **all** of these places. Missing one causes a runtime or CLI failure.

| # | File | What to add |
|---|------|-------------|
| 1 | `config/datasets.yaml` | YAML entry (`id`, `label`, `loader`, …) |
| 2 | `src/dataset_visualizer/loaders/<module>.py` | Loader function(s) returning normalized `DataFrame` |
| 3 | `src/dataset_visualizer/registry.py` | Import + `LOADER_REGISTRY["<loader>"] = <function>` |
| 4 | `src/dataset_visualizer/pages/<category>/<id>.py` | Streamlit page calling `render_dataset_page()` |
| 5 | `scripts/inspect_dataset.py` | `LOADER_CACHE_KEYS` entry (if cache key ≠ loader name) |
| 6 | `tests/test_loaders_<module>.py` | Mocked HF download tests |
| 7 | `docs/datasets/<name>.md` + link in `docs/index.md` | Schema notes |

**Also update** `README.md` dataset table when adding a user-facing dataset.

**Do not edit** `app.py` for new datasets. Navigation is fully config-driven.

## Naming conventions

| Concept | Convention | Example |
|---------|------------|---------|
| Config `id` | `snake_case`; unique globally; version/variant in name | `swe_bench_verified`, `livecodebench_v6` |
| Config `loader` | `snake_case`; registry key; often without version | `livecodebench`, `swe_bench_verified` |
| Page path | `pages/<category>/<id>.py` | `pages/code/swe_bench_verified.py` |
| Loader module | `loaders/<module>.py` | `loaders/swe_bench.py` |
| Loader function | `load_<dataset>()` or `load_<family>_<variant>()` | `load_swe_bench_verified()` |
| Cache directory | `data/cache/<key>/` via `cache_dir("<key>")` | `swe_bench` (shared by three SWE loaders) |
| `key_prefix` | Short unique Streamlit widget prefix | `swe_verified`, `gpqa` |
| `archetype` | Free-form tag for home page / docs | `mcq`, `issue_resolution` |
| Inspect CLI arg | Config `id`, **not** loader name | `swe_bench_verified` |

**`id` vs `loader`:** Multiple config entries may share one loader module but each needs a **distinct** `loader` registry key if defaults differ (see [Variant datasets](#variant-datasets-one-module-multiple-registry-keys) below).

## Config schema (`DatasetEntry`)

Defined in `src/dataset_visualizer/config.py`. Required fields: `id`, `label`, `loader`.

| Field | Required | Purpose |
|-------|----------|---------|
| `id` | yes | Page filename stem, inspect CLI argument, must be globally unique |
| `label` | yes | Sidebar and page title |
| `loader` | yes | Key in `LOADER_REGISTRY` |
| `icon` | no | Streamlit sidebar emoji |
| `archetype` | no | Informational; guides which page template to copy |
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
```

## Loader contract

### Requirements

1. Decorate the public load function with `@st.cache_data(show_spinner="Downloading …")`.
2. Call `cache_dir("<cache_key>")` early (creates `data/cache/<cache_key>/`).
3. Download via `datasets.load_dataset` and/or `huggingface_hub.hf_hub_download`.
4. Return a **normalized** `pandas.DataFrame` with stable column names for the page and shared components.
5. Expose **zero-argument defaults** on the function registered in `LOADER_REGISTRY` — the inspect CLI calls `loader()` with no kwargs.
6. Parse JSON-in-string columns in the loader, not in the page.

### Minimal loader template

```python
"""My benchmark loader."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from datasets import load_dataset

from dataset_visualizer.loaders.base import cache_dir

MY_HF_ID = "org/my-benchmark"


@st.cache_data(show_spinner="Downloading My Benchmark …")
def load_my_benchmark(split: str = "test") -> pd.DataFrame:
    """Load and normalize My Benchmark.

    Args:
        split: Dataset split to load.

    Returns:
        Normalized DataFrame ready for the page and shared components.
    """
    cache_dir("my_benchmark")
    dataset = load_dataset(MY_HF_ID, split=split)
    df = dataset.to_pandas()
    # Add normalized columns here (e.g. answer_letter, choices, split metadata)
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

## Page contract

### `render_dataset_page()` signature

```python
render_dataset_page(
    title: str,                              # Page heading
    df: pd.DataFrame,                        # Full dataset (before sidebar filters)
    id_column: str,                          # Column for sample ID search
    render_overview: Callable[[pd.DataFrame], None],
    render_sample: Callable[[pd.Series], None],
    sidebar_filters: Callable[[pd.DataFrame], pd.DataFrame] | None = None,
    key_prefix: str = "page",                # Unique Streamlit widget keys
)
```

Behavior:

- Renders **Overview** and **Sample Inspector** tabs.
- `sidebar_filters` runs inside the sidebar; return a filtered copy of `df`.
- Split/language selectors that change **which data is downloaded** belong in the page **before** calling the loader (see Global-MMLU pattern), not as post-hoc filters on a huge frame.

### Minimal page template

```python
"""My Benchmark exploration page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dataset_visualizer.components.page_layout import render_dataset_page
from dataset_visualizer.loaders.my_benchmark import load_my_benchmark


@st.cache_data(show_spinner=False)
def _load_data() -> pd.DataFrame:
    return load_my_benchmark()


def _render_overview(df: pd.DataFrame) -> None:
    st.metric("Total rows", f"{len(df):,}")


def _render_sample(row: pd.Series) -> None:
    st.write(row["question"])


df = _load_data()

render_dataset_page(
    title="My Benchmark",
    df=df,
    id_column="sample_id",
    render_overview=_render_overview,
    render_sample=_render_sample,
    key_prefix="my_bench",
)
```

## Archetype reference

Pick the archetype closest to your dataset. The table lists **normalized columns** the loader must produce, **shared components** to use, and an existing dataset to mirror (open only if your case diverges).

| Archetype | Normalized columns (loader output) | Components | Reference `id` | `id_column` |
|-----------|-----------------------------------|------------|----------------|-------------|
| `mcq` | `question`, `choices` (list[str]), `answer_letter` (A–D) | `mcq_viewer`, `charts` | `mmlu`, `gpqa_diamond` | `subject` or `sample_id` |
| `mcq_cot` | Above + `cot_content` or chain-of-thought field | `mcq_viewer`, expander for CoT | `mmlu_pro` | `question_id` |
| `mcq_multilingual` | MCQ columns + `language`, `split` | `mcq_viewer`, language selectbox before load | `global_mmlu` | `sample_id` |
| `code_problem` | `question_content`, `starter_code`, `public_test_cases` (parsed list), metadata | `code_problem_viewer`, `charts` | `livecodebench_v6` | `question_id` |
| `issue_resolution` | `instance_id`, `repo`, `problem_statement`, `patch`, `test_patch`, `fail_to_pass`/`pass_to_pass` (parsed lists) | `issue_viewer`, `charts` | `swe_bench_verified` | `instance_id` |
| `math_competition` | Problem fields + optional joined model outputs | Custom expanders | `arxivmath_0526` | `problem_idx` |

### Component column contracts

**`mcq_viewer.render_mcq(row, question_col="question", choices_col="choices", answer_col="answer_letter")`**

- `choices`: `list[str]` with 2–26 non-empty options (filters `"N/A"`).
- `answer_letter`: single letter; or use raw `answer` int index 0–3.

**`code_problem_viewer.render_code_problem(row)`** expects `question_title`, `question_content`, `starter_code`, `difficulty`, `platform`.

**`code_problem_viewer.render_test_cases(cases)`** expects list of `{"input", "output", "testtype"}` dicts.

**`issue_viewer.render_issue(row)`** expects `instance_id`, `repo`, `base_commit`, `problem_statement`; optional `hints_text`, `patch`, `test_patch`, `fail_to_pass`, `pass_to_pass` (lists), `repo_language`, `difficulty`, `requirements`, `interface`.

**`charts`**: `bar_chart(series, title)`, `pie_chart(series, title)`, `histogram`, `timeline`, `scatter_chart` — all take a `pd.Series`.

## Registered datasets (lookup)

| `id` | Category | `loader` | Archetype | Cache key |
|------|----------|----------|-----------|-----------|
| `mmlu` | reasoning | `mmlu` | mcq | `mmlu` |
| `mmlu_pro` | reasoning | `mmlu_pro` | mcq_cot | `mmlu_pro` |
| `gpqa_diamond` | reasoning | `gpqa` | mcq | `gpqa` |
| `global_mmlu` | reasoning | `global_mmlu` | mcq_multilingual | `global_mmlu` |
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
    load_my_benchmark.clear()  # clear @st.cache_data between tests

    df = load_my_benchmark(split="test")
    assert len(df) == 1
    assert "answer_letter" in df.columns  # assert normalized columns
```

Also test private normalization helpers (`_parse_*`, `_normalize_*_frame`) with unit inputs — no mocking needed.

Run: `uv run pytest`

## Variant datasets (one module, multiple registry keys)

When several config entries share download logic but differ in HF source or normalization (e.g. SWE-Bench Verified / Multilingual / PRO):

1. One loader module with a shared `_load_*()` helper and **separate** `@st.cache_data` functions per variant.
2. **Separate** `LOADER_REGISTRY` keys matching each config `loader` field.
3. **Separate** page files (`pages/<category>/<id>.py`) — one per config entry.
4. Shared `LOADER_CACHE_KEYS` mapping all registry keys to one cache dir if appropriate.

Do **not** rely on a single loader with a `variant` config field unless you also update the inspect CLI to pass that variant (it currently does not).

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| Page 404 / missing from sidebar | Page path must be exactly `pages/<category>/<id>.py` matching YAML `id` and category key |
| Inspect CLI: "No loader registered" | `config.loader` must match `LOADER_REGISTRY` key exactly |
| Inspect CLI loads wrong data | Registered loader must work with `loader()` — no required kwargs |
| Gated HF datasets (e.g. GPQA) | Set `HF_TOKEN` in `.env`; document gating in dataset doc |
| Huge multilingual splits | Select language/split **before** `load_*()` in the page, default to smaller split (`dev`) |
| JSON columns as strings | Parse in loader (`json.loads`, `ast.literal_eval`); store as `list`/`dict` in DataFrame |
| SWE-bench column casing | Verified/Multilingual: `FAIL_TO_PASS`; PRO: `fail_to_pass` — normalize to one name in loader |
| Streamlit widget key collisions | Use unique `key_prefix` and `key=` on sidebar widgets |
| Tests flaky across runs | Always call `load_<name>.clear()` after monkeypatching |

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
2. Copy loader and page **templates** from this doc; adjust normalization columns.
3. Walk the [touchpoint checklist](#complete-touchpoint-checklist).
4. Add tests using the [test contract](#test-contract).
5. Run `uv run pytest` and `uv run ruff check src tests scripts`.
6. Verify with inspect CLI.

Only open an existing page/loader file when your dataset diverges from the archetype table (extra joins, custom decoding, gated access workarounds).
