# Terminal-Bench 4.0

**Source:** [harbor-framework/terminal-bench](https://github.com/harbor-framework/terminal-bench) on GitHub, tag `v4.0.0`  
**Archetype:** Agent task (containerized CLI)  
**Loader:** `dataset_visualizer.loaders.terminal_bench` (`load_terminal_bench_40`)

Terminal-Bench 4.0 is a maintenance release of the Terminal-Bench task set: 66 tasks after removing eight saturated or broken tasks from 3.0 and revising twenty more, with calibrated agent resources (flat 8-hour timeout) and fixed verifiers. Tasks are Harbor-format directories (`task.toml` + `instruction.md`) downloaded from the tagged GitHub archive; the loader reuses the Terminal-Bench 2.1 parser, extended for the newer `task.toml` schema (`expert_time_estimate_hours`, list-valued authors, `network_mode`).

## Normalized columns

See [terminal_bench_21.md](terminal_bench_21.md); 4.0 rows additionally carry `task_path` (path under `tasks/`), `domain`, and `field` when present in task metadata.

## Cache

Downloaded GitHub archive and extracted tasks live under `data/cache/terminal_bench_40/`.

## Links

- [Terminal-Bench 4.0 announcement](https://www.tbench.ai/news/terminal-bench-4-0)
- [Harbor docs — running Terminal-Bench](https://www.harborframework.com/docs/tutorials/running-terminal-bench)
