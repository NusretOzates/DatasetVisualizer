# Terminal-Bench Science 0.1

**Source:** [harbor-framework/terminal-bench-science](https://github.com/harbor-framework/terminal-bench-science) on GitHub, tag `v0.1.0`  
**Archetype:** Agent task (containerized CLI)  
**Loader:** `dataset_visualizer.loaders.terminal_bench` (`load_terminal_bench_science`)

Terminal-Bench Science measures agents on real-world computational research workflows across the life, physical, earth, mathematical, and engineering sciences. The `v0.1.0` release contains 70 tasks nested under `tasks/<domain>/<field>/<task>/` directories; the shared Terminal-Bench loader walks `task.toml` files recursively and surfaces `domain` and `field` metadata for filtering.

## Normalized columns

See [terminal_bench_21.md](terminal_bench_21.md); Science rows carry `domain`, `field`, and `task_path` from the nested layout.

## Cache

Downloaded GitHub archive and extracted tasks live under `data/cache/terminal_bench_science_01/`.

## Links

- [Terminal-Bench Science](https://terminal-bench-science.ai/)
- [Harbor docs](https://www.harborframework.com/docs)
