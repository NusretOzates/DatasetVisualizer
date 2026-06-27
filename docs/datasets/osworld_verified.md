# OSWorld-Verified

**Source:** [xlang-ai/OSWorld](https://github.com/xlang-ai/OSWorld) (`evaluation_examples/test_nogdrive.json`)  
**Website:** [os-world.github.io](https://os-world.github.io/)  
**Archetype:** Desktop GUI agent task  
**Loader:** `dataset_visualizer.loaders.osworld_verified` (`load_osworld_verified`)

OSWorld-Verified is the refined OSWorld benchmark suite with community-reported issues fixed. This app loads the **361-task** `test_nogdrive` split (excludes eight Google Drive–dependent tasks).

## Normalized columns

| Column | Description |
|--------|-------------|
| `task_id` | UUID task identifier |
| `domain` | App domain folder (`chrome`, `gimp`, `libreoffice_calc`, …) |
| `instruction` | Natural-language GUI task instruction |
| `instruction_preview` | Truncated instruction for overview tables |
| `snapshot` | Environment snapshot id |
| `source` | Reference URL where the task originated |
| `related_apps` | Apps involved in the task |
| `config` | Setup script steps (launch/download/open files) |
| `config_step_count` | Number of setup steps |
| `evaluator` | Evaluation script metadata |
| `evaluator_func` | Evaluator function name |
| `trajectory` | Upstream trajectory directory label |
| `split` | `verified` |

## UI notes

- **Overview** — task count, domain count, evaluator types, tasks-by-domain summary.
- **Filters** — domain and evaluator multiselect.
- **Sample inspector** — instruction, related apps, source link, collapsible setup config and evaluator JSON.

## Cache

Downloaded GitHub archive lives under `data/cache/osworld_verified/`.

## Links

- [OSWorld-Verified announcement](https://xlang.ai/blog/osworld-verified)
- [Project page](https://os-world.github.io/)
