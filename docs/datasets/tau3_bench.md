# τ³-Bench

**Source:** [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench) (`data/tau2/domains/*/tasks.json` on GitHub)  
**Archetype:** Agent task (tool-agent-user interaction)  
**Loader:** `dataset_visualizer.loaders.tau3_bench` (`load_tau3_bench`)

τ³-bench is the v1.0.0 release of the τ-bench family. This app loads task definitions directly from the upstream GitHub repository (not Hugging Face).

## Domains (base split)

| Domain | Tasks |
|--------|------:|
| `airline` | 50 |
| `retail` | 114 |
| `telecom` | 114 |
| `banking_knowledge` | 97 |
| **Total** | **375** |

Other splits (`train`, `test`) are available for airline, retail, and telecom via the **Task split** control. Banking knowledge always loads all tasks.

## Normalized columns

| Column | Description |
|--------|-------------|
| `instance_id` | Stable id `{domain}-{task_id}` |
| `task_id` | Upstream task id |
| `domain` | `airline`, `retail`, `telecom`, or `banking_knowledge` |
| `task_split` | Selected split (`base`, `train`, `test`) |
| `purpose` | Task purpose from `description.purpose` |
| `reason_for_call` | Simulated user reason for contacting support |
| `task_instructions` | Instructions for the simulated user |
| `known_info` / `unknown_info` / `persona` | Optional user-scenario fields |
| `purpose_preview` | Truncated preview for overview tables |
| `evaluation_action_count` | Count of expected actions in evaluation criteria |
| `has_ticket` | Whether the telecom task includes a support ticket |
| `evaluation_criteria` | Raw expected-action payload (sample inspector) |
| `initial_state` | Optional environment seed state |
| `ticket` | Optional telecom ticket payload |

## Cache

Downloaded JSON is cached under `data/cache/tau3_bench/`.

## UI notes

- **Overview** — task count, domain count, split; full task table with purpose previews.
- **Sample inspector** — purpose, user scenario, evaluation criteria, ticket, and initial state expanders.
