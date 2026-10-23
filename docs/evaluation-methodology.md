# Evaluation Methodology

Dataset Visualizer is **not** an evaluation harness: it loads benchmark
tasks so you can inspect them, but it never runs a model or computes a
score. Every dataset page therefore carries a small **“How this benchmark
is evaluated”** section describing how the benchmark's own upstream
evaluation scores model outputs. The per-dataset text lives in
[`config/evaluation_methods.yaml`](../config/evaluation_methods.yaml)
(one entry per catalog `id`, enforced by `tests/test_evaluation_methods.py`)
and is served to the frontend through `get_dataset_meta`.

## Why the same benchmark can score differently

A published score is produced by a whole system, not just a dataset:

| Layer | What varies between labs |
|-------|--------------------------|
| Dataset | Split, version, decontamination |
| Environment | Sandbox, container, desktop VM, internet access |
| Agent scaffold | Tools, retries, time/token/step limits, system prompt |
| Scorer | The methods in the table below |
| Protocol | Temperature, attempts, `pass@1` vs `pass@5`, number of trials |

This is why OpenAI, Anthropic, Meta, Moonshot, and independent evaluators
can report different numbers on the “same” benchmark: they usually share
the tasks, not the harness. Agentic benchmarks (terminal, coding,
computer-use) are the most sensitive to the scaffold; static
multiple-choice benchmarks are the least.

## Method families used in this catalog

| Method key | Scorer | Typical headline metric |
|------------|--------|-------------------------|
| `multiple_choice` | Chosen option compared with the gold letter | Accuracy |
| `exact_match` | Final answer (number, label, short string) matched exactly, sometimes after normalization | Accuracy |
| `reference_grading` | Output graded against a reference answer where literal match is too brittle (equivalence, acceptable ranges) | Accuracy |
| `llm_judge` | A judge model decides correctness against the reference or expected behavior | Accuracy / win rate |
| `code_execution` | Generated code or patch is executed against unit tests (including SWE-bench `FAIL_TO_PASS`/`PASS_TO_PASS`) | `pass@k`, resolved rate |
| `container_task_tests` | Agent acts in a container; task-specific verifier tests run afterwards | Task success rate |
| `desktop_state_check` | Checker functions inspect the final desktop/VM state (files, apps, OS settings) | Task success rate |
| `tool_task_verification` | Tool calls and final artifacts/state are verified against task expectations | Task success rate |
| `agent_simulation` | A simulated user interacts with the agent; final environment state is checked | Task success rate |
| `rubric_grading` | Deliverables graded criterion by criterion against a rubric (judge- or expert-applied) | Rubric score / win rate |
| `human_expert_grading` | Professionals blind-grade or compare deliverables | Win rate / Elo-style score |
| `programmatic_verification` | Deterministic checkers validate constraints, synthetic gold answers, or computed results | Accuracy / constraint satisfaction |
| `forecast_outcome` | Predictions scored after events resolve, against actual outcomes | Accuracy / proper scoring rules |
| `grid_exact_match` | Predicted ARC grid must equal the gold grid cell by cell | Puzzle solve rate |
| `translation_scoring` | Translation compared with reference translations by automatic overlap metrics | chrF-style score |

## Reading the per-dataset summaries

- Summaries name the scorer and the headline metric only. They do not name
  a specific judge model, numeric tolerance, or trial count unless the
  upstream source states it, because labs change those between runs.
- “With tools” variants (for example ZeroBench or Humanity's Last Exam
  with tools) reuse the same tasks with a tool scaffold; their scores are
  a different setting, not a better run of the same setting.
- Gated datasets (for example OfficeQA Pro v2) keep summaries at the level
  confirmed from public material; grader details should be re-checked on
  first access before being made more specific.

## Adding or changing an entry

1. Add the dataset to `config/datasets.yaml` as usual.
2. Add a matching entry to `config/evaluation_methods.yaml` with a
   `method` from the table above and a one- or two-sentence `summary`.
3. Base the summary on the benchmark's paper, repository, or dataset
   card. If the grader is not publicly specified, describe only what is
   known (for example “graded against reference answers”) instead of
   guessing a judge or metric.
4. Run `uv run pytest tests/test_evaluation_methods.py` — coverage of
   every catalog `id` is enforced.
