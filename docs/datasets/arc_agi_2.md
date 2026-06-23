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

## Visualization rationale

- **Grid viewer** — renders train/test input-output matrices with ARC color IDs instead of showing raw JSON.
- **Raw JSON fallback** — remains available under the sample inspector for exact schema inspection.

## Touchpoints

- Viewer override: `config/datasets.yaml` (`viewer: arc_grid`)
- Renderer: `frontend/components/viewers/ArcGridViewer.tsx`
- Registry: `frontend/components/viewers/registry.tsx`
