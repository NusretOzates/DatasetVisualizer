# Architecture overview

The Dataset Visualizer is a Gradio Server API plus a static-exportable Next.js frontend. Dataset metadata lives in YAML, Python loaders normalize benchmark rows, API services return chart/sample payloads, and React viewers render overviews plus per-sample inspection.

## System boundaries

```mermaid
flowchart LR
  Config["config/datasets.yaml"] --> Registry["api/dataset_registry.py"]
  Registry --> Loaders["loaders/*"]
  Loaders --> Service["api/service.py"]
  Service --> Server["server.py @app.api"]
  Server --> Client["frontend/lib/api.ts"]
  Client --> UI["DatasetExplorer + viewers"]
```

## Data flow

```mermaid
flowchart TD
  Select["User selects dataset / controls"] --> Meta["get_dataset_meta"]
  Meta --> Options["get_filter_options"]
  Options --> Overview["get_overview"]
  Overview --> Charts["OverviewTab + ChartPanel"]
  Options --> Sample["get_sample or find_sample"]
  Sample --> Viewer["viewer registry"]
  Viewer --> Raw["Raw JSON fallback"]
```

## Visualizer notes

- **Manual loaders** (13 datasets) use tailored overview builders in `api/overview.py` and dedicated normalization in `loaders/<module>.py`.
- **`hf_benchmark` entries** (38 datasets) auto-register from YAML, normalize via `loaders/benchmark_normalize.py` profiles, and share `overview_generic()` plus reusable filters.
- Generic Hugging Face benchmarks use normalized columns to produce reusable charts: category bars, answer distribution, choice/test-count histograms, text-length histograms, and date timelines.
- Sample viewers are keyed by API `viewer`; the YAML `viewer` field can override the archetype when a benchmark needs a more specific presentation (`code_eval`, `arc_grid`, …).
- Math and benchmark statements render Markdown/LaTeX via the shared frontend renderer.
