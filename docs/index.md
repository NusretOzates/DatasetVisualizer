# Dataset Visualizer Docs

Internal developer documentation for the Dataset Visualizer project.

## Start here

- **[Dataset system reference](dataset-system.md)** — architecture, touchpoint checklist, loader/page/test contracts, archetype table, templates, pitfalls. **Read this before opening source files** when adding or modifying datasets.
- [Adding a dataset](adding-a-dataset.md) — short checklist (links to the system reference)

## Datasets

Per-dataset schema and visualization notes:

- [MMLU](datasets/mmlu.md)
- [MMLU-Pro](datasets/mmlu_pro.md)
- [GPQA Diamond](datasets/gpqa_diamond.md)
- [Global-MMLU](datasets/global_mmlu.md)
- [Humanity's Last Exam](datasets/hle.md)
- [LiveCodeBench v6](datasets/livecodebench.md)
- [SWE-Bench](datasets/swe_bench.md)
- [ArXiv Math 0526](datasets/arxivmath.md)

## Architecture (summary)

```
config/datasets.yaml  →  config.py (Pydantic)
                      →  registry.py (LOADER_REGISTRY + build_navigation)
                      →  app.py (st.navigation — no per-dataset edits)

pages/<category>/<id>.py  →  loaders/<loader>.py  →  data/cache/<cache_key>/
```

Details, naming rules, and the full touchpoint list: [dataset-system.md](dataset-system.md).

## Shared components

| Module | Purpose |
|--------|---------|
| `page_layout.py` | Overview + Sample Inspector tabs (`render_dataset_page`) |
| `sample_navigator.py` | Index slider, prev/next, ID search |
| `charts.py` | Plotly bar, histogram, pie, timeline, scatter |
| `mcq_viewer.py` | Multiple-choice rendering |
| `code_problem_viewer.py` | Code problems and test cases |
| `issue_viewer.py` | SWE-bench issues, patches, test lists |

Column contracts per archetype: [dataset-system.md § Component column contracts](dataset-system.md#component-column-contracts).

## Inspect CLI

```bash
uv run python scripts/inspect_dataset.py <dataset_id>
```

`<dataset_id>` is the config `id` (e.g. `mmlu`, `swe_bench_verified`). The CLI calls `loader()` with no arguments — loaders must define safe defaults. See [dataset-system.md § Loader contract](dataset-system.md#loader-contract).

## Run

```bash
uv run streamlit run src/dataset_visualizer/app.py
```
