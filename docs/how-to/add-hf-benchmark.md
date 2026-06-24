# How to add a Hugging Face benchmark (YAML-only)

Use this recipe when a benchmark fits an existing **normalization profile** and **viewer** — no custom download logic or column transforms. Most new catalog entries follow this path (38 of 51 datasets today).

## 1. Pick profile and viewer

| If the benchmark looks like… | Set `profile` | Set `archetype` / `viewer` | Example `id` |
|------------------------------|---------------|----------------------------|--------------|
| Standard MCQ (AI2 ARC, PIQA, …) | matching name in `benchmark_normalize.py` (`arc`, `piqa`, …) | `mcq` | `arc_challenge` |
| Grade-school / competition math | `gsm` or `math_competition` | `math_competition` | `gsm8k`, `math` |
| Python function completion + tests | `code_eval` or `mbpp` or `apps` | `code_eval` (set `viewer:` explicitly) | `humaneval` |
| Long-context / instruction / forecasting QA | `generic` or `instruction` or `coconot` | `generic` | `ruler`, `ifeval` |
| Agent / assistant scenarios | `agent_task`, `gaia`, `gaia2` | `agent_task` (set `viewer:` — use `generic` or `gaia`, not `agent_task`) | `gaia`, `livemcpbench`, `dabstep` |
| ARC-AGI grid puzzles | `arc_agi` | `arc_grid` (set `viewer:`) | `arc_agi_2` |

Full profile list: `NORMALIZERS` in `src/dataset_visualizer/loaders/benchmark_normalize.py`.

## 2. Add YAML entry

Edit [`config/datasets.yaml`](../../config/datasets.yaml) under the right category:

```yaml
categories:
  reasoning:
    - id: my_benchmark
      label: My Benchmark
      loader: hf_benchmark
      icon: "🧠"
      archetype: mcq
      hf_id: org/my-benchmark
      hf_config: main          # omit if single-config dataset
      profile: arc             # must match a normalizer
      id_column: id            # stable row id column in HF schema
      row_count: 1000          # optional; speeds home page
      description: >
        One- to three-sentence summary for the dataset page.
```

Optional fields: `source_file` (JSONL), `multi_config: true`, `exclude_configs`, `viewer` (override archetype).

**Splits:** loaders auto-select the smallest published Hub split (`train` / `validation` / `test` / …) for inspection. The active split appears in the dataset overview and page header. YAML `split:` is informational only.

## 3. Verify auto-registration

`build_dataset_registry()` picks up every `loader: hf_benchmark` entry not already in `_MANUAL_REGISTRY`. No edits to `dataset_registry.py` unless you need custom filters or a non-generic overview.

```bash
uv run python -c "from dataset_visualizer.api.dataset_registry import get_descriptor; print(get_descriptor('my_benchmark'))"
```

## 4. Test and document

```bash
uv run pytest tests/test_benchmark_registry.py tests/test_loaders_hf_benchmark.py
uv run python scripts/inspect_dataset.py my_benchmark
```

- Add [`docs/datasets/<name>.md`](../datasets/) only when schema or visualization is non-obvious (see [ARC-AGI 2](../datasets/arc_agi_2.md)).
- Link from [`docs/index.md`](../index.md) when you add a dataset doc.
- Rebuild frontend with backend running so `/dataset/my_benchmark` is exported.

## Gotchas

- **Gated Hub repos** — set `HF_TOKEN`; document access in the dataset doc.
- **Wrong profile** — columns won't match the viewer; inspect CLI is the fastest check.
- **`archetype: agent_task` without `viewer:`** — falls back to `Tau3BenchViewer`, which only renders τ³-Bench fields. Set `viewer: generic` (or `gaia` / another dedicated viewer) for Hub benchmarks that are not τ³-Bench.
- **Missing `id_column`** — defaults to `sample_id`; set explicitly when HF uses another name.
- **Build-time routes** — start `uv run dataset-viz` before `npm run build`.

For custom loaders or overview builders, use [add-dataset.md](add-dataset.md) instead.
