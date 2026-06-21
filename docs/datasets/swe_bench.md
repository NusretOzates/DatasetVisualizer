# SWE-Bench (Verified, Multilingual, PRO)

**Sources:**

- Verified: [`SWE-bench/SWE-bench_Verified`](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified)
- Multilingual: [`SWE-bench/SWE-bench_Multilingual`](https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual)
- PRO: [`Contextbench/SWE-bench_Pro`](https://huggingface.co/datasets/Contextbench/SWE-bench_Pro)

**Archetype:** Issue resolution (GitHub issue + gold patch + tests)

## Schema (normalized)

| Column | Type | Notes |
|--------|------|-------|
| `instance_id` | str | Unique task id (`owner__repo-PR`) |
| `repo` | str | GitHub `owner/name` |
| `base_commit` | str | Pre-fix commit hash |
| `problem_statement` | str | Issue title and body |
| `patch` | str | Gold solution patch |
| `test_patch` | str | Test-file patch from the PR |
| `hints_text` | str | Pre-PR issue comments |
| `fail_to_pass` | list[str] | Parsed from `FAIL_TO_PASS` or `fail_to_pass` |
| `pass_to_pass` | list[str] | Parsed from `PASS_TO_PASS` or `pass_to_pass` |
| `fail_to_pass_count` | int | Length of fail-to-pass list |
| `variant` | str | `verified`, `multilingual`, or `pro` |

PRO adds: `requirements`, `interface`, `repo_language`, `issue_specificity`, `issue_categories`, `before_repo_set_cmd`, `selected_test_files_to_run`.

Verified adds: `difficulty`.

## Visualization rationale

- **Repository bar chart** — shows which projects dominate each split.
- **Language / difficulty charts** — variant-specific coverage (PRO language, Verified difficulty).
- **Issue inspector** — problem statement, hints, gold patch, and test lists in expandable sections.

## Loaders

- `load_swe_bench_verified()` — 500 verified Python tasks
- `load_swe_bench_multilingual()` — 300 multilingual tasks
- `load_swe_bench_pro()` — 731 enterprise-scale tasks

## Cache

`data/cache/swe_bench/`
