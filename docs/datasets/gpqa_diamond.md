# GPQA Diamond

**Source:** [`Idavidrein/gpqa`](https://huggingface.co/datasets/Idavidrein/gpqa) (`gpqa_diamond` config)  
**Archetype:** MCQ (4 options, graduate-level science)  
**Access:** Gated — accept terms on Hugging Face and set `HF_TOKEN` in `.env`.

## Schema (normalized)

| Column | Type | Notes |
|--------|------|-------|
| `question` | str | Graduate-level science question |
| `choices` | list[str] | Four shuffled options (deterministic per question) |
| `answer_letter` | str | Correct option A–D |
| `split` | str | Always `gpqa_diamond` |

## Visualization rationale

- **Answer letter pie** — sanity check for option balance after shuffling.
- **MCQ sample inspector** — reuses shared `mcq_viewer`.

## Loader

`load_dataset("Idavidrein/gpqa", "gpqa_diamond", split="train")` with deterministic option shuffle.

## Cache

`data/cache/gpqa/`
