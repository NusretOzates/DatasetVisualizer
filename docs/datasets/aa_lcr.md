# AA-LCR

**Source:** [`ArtificialAnalysis/AA-LCR`](https://huggingface.co/datasets/ArtificialAnalysis/AA-LCR) (`test` split, 100 questions)  
**Archetype:** Long-context reasoning (open answers over multi-document sets)  
**Loader:** `dataset_visualizer.loaders.aa_lcr:load_aa_lcr`

## What ships on the Hub

| Asset | Contents |
|-------|----------|
| Parquet / CSV rows | Question, answer, document category, set id, source filenames/URLs, `input_tokens` |
| `AA-LCR_extracted-text.zip` | Plain-text extracts (~11.6 MB uncompressed) under `lcr/{category}/{set_id}/{filename}.txt` |

Questions reference document sets averaging ~100k tokens when fully assembled for evaluation.

## What the visualizer loads

The manual loader downloads and caches the extracted-text zip once, then for each row:

- Preserves normalized metadata from the Hub table (`normalize_aa_lcr`)
- Adds **`document_preview`** — first **500 words** of all source documents concatenated in filename order
- Adds **`document_previews`** — per-file 500-word previews with total word counts
- Flags **`document_preview_truncated`** when the combined text exceeds 500 words

Full document bodies are not loaded into every API payload beyond these previews.

## UI notes

- **Overview** — generic metrics via `overview_generic`
- **Filters** — `document_category`
- **Sample inspector** — question, combined 500-word preview, reference answer, expandable per-source previews and URLs

## Cache

`data/cache/aa_lcr/` — extracted zip under `extracted/` plus Hub dataset cache via `datasets`.
