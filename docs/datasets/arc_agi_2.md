# ARC-AGI 2

**Source:** [`arc-agi-community/arc-agi-2`](https://huggingface.co/datasets/arc-agi-community/arc-agi-2) (`test` split, 120 puzzles)  
**Archetype:** Grid transformation puzzle  
**Loader:** `dataset_visualizer.loaders.hf_benchmark` with `profile: arc_agi`

## Schema

| Column | Type | Description |
|--------|------|-------------|
| `sample_id` | `string` | Stable puzzle id |
| `puzzle_json` | `string` | JSON-serialized ARC puzzle with train/test input-output grids |
| `split` | `string` | Dataset split |

## UI notes

- **Overview** — row count, split, group count (via generic overview).
- **Sample inspector** — ARC color grids for train/test pairs; raw JSON fallback.

## Touchpoints

- Viewer override: `config/datasets.yaml` (`viewer: arc_grid`)
- Renderer: `frontend/components/viewers/ArcGridViewer.tsx`
- Registry: `frontend/components/viewers/registry.tsx`
