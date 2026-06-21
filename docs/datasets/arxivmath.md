# ArXiv Math 0526

**Sources:**

- Problems: [`MathArena/arxivmath-0526`](https://huggingface.co/datasets/MathArena/arxivmath-0526)
- Model outputs: [`MathArena/arxivmath-0526_outputs`](https://huggingface.co/datasets/MathArena/arxivmath-0526_outputs)

**Archetype:** Math competition with model runs  
**Status:** Stub (Wave 2)

## Planned schema

**Problems (~40 rows):** `problem_idx`, `title`, `problem`, `answer`, `source`, `authors`

**Outputs (~960 rows):** `problem_idx` (str join key), `model_name`, `correct`, `parsed_answer`, `gold_answer`, token/cost fields

## Planned visualization

- All-problems table, model accuracy bar chart, token scatter
- Two-column sample view: problem + paper metadata | model runs joined on `problem_idx`

## Gotcha

Cast `problem_idx` to `str` in both frames before joining.
