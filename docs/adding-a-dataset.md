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

New top-level category keys appear automatically in the sidebar (title-cased).

## 2. Implement loader

Create `src/dataset_visualizer/loaders/<loader>.py`:

- Use `@st.cache_data` with a spinner message
- Call `cache_dir("<dataset_id>")` from `loaders/base.py`
- Return a normalized `pandas.DataFrame`
- Register the function in `LOADER_REGISTRY` in `registry.py`

## 3. Create page

Create `src/dataset_visualizer/pages/<category>/<id>.py`:

- Compose `render_dataset_page()` from `components/page_layout.py`
- Implement `render_overview()` and `render_sample()` callbacks
- Reuse shared components (`mcq_viewer`, `charts`, etc.) where possible

Copy the closest existing page for your dataset archetype (MCQ → `mmlu.py`, code → `livecodebench_v6.py`, etc.).

## 4. Add tests

Create `tests/test_loaders_<id>.py` with mocked Hugging Face downloads. Use small fixtures under `tests/fixtures/`.

Optionally add `docs/datasets/<id>.md` with schema notes after inspecting real data.
