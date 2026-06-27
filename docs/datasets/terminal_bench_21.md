# Terminal-Bench 2.1

**Source:** [harbor-framework/terminal-bench-2-1](https://github.com/harbor-framework/terminal-bench-2-1) on GitHub  
**Archetype:** Agent task (containerized CLI)  
**Loader:** `dataset_visualizer.loaders.terminal_bench` (`load_terminal_bench_21`)

Terminal-Bench measures agents on hard, realistic tasks in command-line container environments. Version 2.1 is a verified iteration of Terminal-Bench 2.0 with bug fixes and anti–reward-hacking improvements.

## Normalized columns

| Column | Description |
|--------|-------------|
| `task_id` | Task directory slug (stable id) |
| `instance_id` | Same as `task_id` |
| `task_name` | Harbor task name from `task.toml` |
| `description` | Short task summary from `task.toml` |
| `instruction` | Agent instruction from `instruction.md` |
| `instruction_preview` | Truncated instruction for overview table |
| `task_readme` | Upstream task README when present |
| `category` | Task category (e.g. `software-engineering`) |
| `difficulty` | `easy`, `medium`, or `hard` |
| `author_name` | Task author |
| `docker_image` | Evaluation container image |
| `allow_internet` | Whether the environment allows network access |
| `cpus`, `memory_mb` | Container resource limits |
| `expert_time_estimate_min`, `junior_time_estimate_min` | Human time estimates |
| `split` | Upstream branch label (`main`) |

## UI notes

- **Overview** — task count, category count, tasks-by-category summary.
- **Filters** — category and difficulty multiselect.
- **Sample inspector** — instruction markdown, Harbor metadata, collapsible task README.

## Cache

Downloaded GitHub archive and extracted tasks live under `data/cache/terminal_bench_21/`.

## Links

- [Harbor docs — running Terminal-Bench](https://www.harborframework.com/docs/tutorials/running-terminal-bench)
- [Terminal-Bench 2.1 leaderboard](https://www.tbench.ai/leaderboard/terminal-bench/2.1)
