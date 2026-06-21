# Adding a Dataset

Follow these four steps to register a new dataset. No changes to `app.py` are required after the initial framework.

## 1. Register in config

Add an entry under an existing or new category in [`config/datasets.yaml`](../config/datasets.yaml):

```yaml
categories:
  reasoning:
    - id: my_dataset
      label: My Dataset
      loader: my_dataset
      icon: ":brain:"
      archetype: mcq
      hf_id: org/my-dataset
```

New top-level category keys appear automatically in the sidebar (title-cased). The `id` field is the page filename stem (`pages/<category>/<id>.py`) and the inspect CLI argument.

## 2. Implement loader

Create `src/dataset_visualizer/loaders/<loader>.py`:

- Use `@st.cache_data` with a spinner message
- Call `cache_dir("<cache_key>")` from `loaders/base.py` (usually matches the loader name)
- Return a normalized `pandas.DataFrame`
- Register the function in `LOADER_REGISTRY` in [`registry.py`](../src/dataset_visualizer/registry.py)

## 3. Create page

Create `src/dataset_visualizer/pages/<category>/<id>.py`:

- Compose `render_dataset_page()` from `components/page_layout.py`
- Implement `render_overview()` and `render_sample()` callbacks
- Reuse shared components where possible:
  - `mcq_viewer` — MMLU-style MCQ
  - `code_problem_viewer` — LiveCodeBench-style code problems
  - `charts` — Plotly overview charts

Copy the closest existing page for your dataset archetype:

| Archetype | Copy from |
|-----------|-----------|
| MCQ | `pages/reasoning/mmlu.py` |
| MCQ + CoT | `pages/reasoning/mmlu_pro.py` |
| Code generation | `pages/code/livecodebench_v6.py` |
| Math + model runs | `pages/math/arxivmath_0526.py` |

## 4. Add tests and docs

Create `tests/test_loaders_<loader>.py` with mocked Hugging Face downloads. Use small fixtures under `tests/fixtures/`.

Add `docs/datasets/<short_name>.md` with schema notes. Run the inspect CLI on real data to populate fields:

```bash
uv run python scripts/inspect_dataset.py <dataset_id>
```

Link the new doc from [`docs/index.md`](index.md).
