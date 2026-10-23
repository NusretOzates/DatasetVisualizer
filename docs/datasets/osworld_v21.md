# OSWorld V2.1

**Source:** [xlang-ai/OSWorld-V2](https://github.com/xlang-ai/OSWorld-V2) release `osworld-v2.1`; task classes in the gated Hub dataset [`xlangai/osworld_v2_tasks`](https://huggingface.co/datasets/xlangai/osworld_v2_tasks)  
**Archetype:** Agent task (desktop GUI)  
**Loader:** `dataset_visualizer.loaders.osworld_v2` (`load_osworld_v21`)

OSWorld V2.1 is the current OSWorld release: 108 desktop GUI agent tasks with pinned task, asset, website, and provider-image versions. The task implementation classes are distributed only through the gated Hub dataset to reduce benchmark leakage, so this catalog entry loads the public release hash manifest (`benchmark_releases/osworld-v2.1.task_hashes.json`) from the tagged GitHub archive instead of mirroring task content.

## Normalized columns

| Column | Description |
|--------|-------------|
| `task_id` / `instance_id` | Task stem (`task_001` … `task_108`) |
| `task_file` | Gated task class filename |
| `sha256`, `file_size_bytes` | Pinned content hash and size from the release manifest |
| `release` / `split` | `osworld-v2.1` |
| `source_repo`, `source_revision` | Gated Hub dataset and pinned commit |

## Cache

Downloaded GitHub archive lives under `data/cache/osworld_v21/`.

## Links

- [OSWorld V2.1 release notes](https://github.com/xlang-ai/OSWorld-V2/releases)
- [OSWorld-Verified (v1 suite)](osworld_verified.md)
