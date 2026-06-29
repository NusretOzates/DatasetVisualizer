# Frontend (Next.js)

The Dataset Visualizer UI is a **Next.js 15** React app in [`frontend/`](../frontend/) styled with **Tailwind CSS v4** and **shadcn/ui**. It talks to the Gradio Server backend via [`@gradio/client`](https://www.npmjs.com/package/@gradio/client).

## Stack

| Piece | Location | Role |
|-------|----------|------|
| Styling | Tailwind CSS v4 + `app/globals.css` | Theme tokens, layout utilities |
| Components | `components/ui/` (shadcn/ui) | Button, Card, Tabs, Table, Select, etc. |
| Icons | `lucide-react` | Sidebar and action icons |
| Typography | `next/font` (Inter) | App-wide font |
| App shell | `components/Sidebar.tsx` | Sidebar + `AppShell` layout |
| Sidebar FAQ | `components/SidebarFaq.tsx`, `lib/faq.ts` | Collapsible FAQ cards under the dataset nav |
| Home page | `components/HomePage.tsx` | Dataset catalog table |
| Dataset routes | `app/dataset/[id]/page.tsx` | Static export; routes from `generateStaticParams` |
| API client | `lib/api.ts` | `@gradio/client` wrappers |
| Catalog hook | `lib/useCatalog.ts` | Client-side catalog fetch |
| Types | `lib/types.ts` | Catalog, overview, control, and filter types |
| Explorer | `components/DatasetExplorer.tsx` | Controls, top filters, tabs (via `lib/useDatasetQuery.ts`) |
| Overview | `components/OverviewTab.tsx`, `DatasetReadme.tsx` | Metric cards, optional tables, README |
| Samples | `components/SampleInspector.tsx` | Index slider, prev/next, and viewers |
| Viewer registry | `components/viewers/registry.tsx` | Maps API `viewer` key → React component |
| Rich text | `components/viewers/MarkdownMath.tsx` | Markdown + LaTeX rendering for benchmark statements |
| Frontend linting | `eslint.config.mjs` | Next.js core web vitals + TypeScript rules |

shadcn configuration lives in [`frontend/components.json`](../frontend/components.json).

## Development

Terminal 1 — backend:

```bash
uv run dataset-viz
```

Terminal 2 — frontend with hot reload:

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:7860 npm run dev
```

Open http://localhost:3000. The API client uses `NEXT_PUBLIC_API_URL` when set; otherwise, when the UI runs on port **3000** (Next.js dev), it connects to `http://localhost:7860` automatically. In production (same origin as the Gradio server), it uses `window.location.origin`. Failed connect attempts reset the Gradio client promise so the next request retries.

## Quality checks

Run these from `frontend/`:

```bash
npm run lint
npm run typecheck
NEXT_PUBLIC_API_URL=http://localhost:7860 npm run build
```

`npm run lint` uses the ESLint CLI with `eslint.config.mjs`; do not use deprecated `next lint`.

## Production build

The backend must be reachable during `npm run build` so `generateStaticParams` can call `get_catalog` and pre-render `/dataset/[id]` routes:

```bash
uv run dataset-viz   # terminal 1
cd frontend
NEXT_PUBLIC_API_URL=http://localhost:7860 npm run build   # terminal 2
```

`server.py` serves `frontend/out/` at `/` when the build exists. Rebuild the frontend after UI changes.

## Adding a dataset to the frontend

1. Register the dataset in `api/dataset_registry.py` with a `viewer` key and overview/filters.
2. Ensure `get_dataset_meta` returns the correct `viewer`, controls, filters, and `id_column`.
3. Rebuild the frontend with the backend running so the new route is exported.
4. Add a dedicated viewer under `components/viewers/` only when no existing viewer fits; register it in `components/viewers/registry.tsx`.

No manual route list is required — `app/dataset/[id]/page.tsx` uses `generateStaticParams()` from `fetchCatalog()`.

### Viewer key → component mapping

Defined in `components/viewers/registry.tsx` (dispatched by API `viewer`, with `archetype` as fallback):

| `viewer` | Component | Notes |
|----------|-----------|-------|
| `mcq` | `McqViewer` | Also used for multilingual MCQ datasets |
| `mcq_cot` | `McqCotViewer` | MCQ + chain-of-thought collapsible |
| `code_problem` | `CodeProblemSampleViewer` | Public tests plus decoded private tests (first 10 shown) |
| `issue_resolution` | `IssueViewer` | SWE-bench style patches and test lists |
| `agent_task` | `Tau3BenchViewer` | τ³-Bench customer-service agent tasks |
| `terminal_bench_21` | `TerminalBenchViewer` | Terminal-Bench CLI container tasks |
| `academic_qa` | `HleViewer` | HLE questions, images, answer types |
| `math_competition` | `MathViewer` | Competition problems + solution extras |
| `arxiv_math` | `ArxivMathViewer` | ArXiv Math problems + model-run tables |
| `arc_grid` | `ArcGridViewer` | ARC-AGI input/output grid puzzles |
| `code_eval` | `CodeEvalViewer` | HumanEval/MBPP-style prompts, tests, and solutions |
| `gaia` | `GaiaViewer` | GAIA / GAIA2 assistant scenarios |
| `paperbench` | `PaperBenchViewer` | ML paper replication rubrics and reference files |
| `generic` | `GenericViewer` | Long-context, instruction-following, and other pass-through benchmarks |

Custom viewers live in `components/viewers/` (e.g. `McqCotViewer.tsx`, `CodeProblemSampleViewer.tsx`).

## Overview tab

`OverviewTab` shows summary metric cards, optional overview tables, and the Hugging Face dataset **README** at the bottom (via `readme` on `get_dataset_meta`), rendered with `MarkdownContent` (GFM tables, links, math).

## Sample navigation

`SampleInspector` loads samples through `get_sample` using the slider and previous/next controls only. Jump-to-id lookup was removed; use index navigation to browse rows.

Filter option payloads use the `FilterOptions` type. Empty generated filters are hidden client-side so generic benchmark descriptors can advertise reusable filter candidates safely.

## Documentation

When changing frontend architecture, routes, viewers, or build requirements, update this file and cross-links in [`docs/index.md`](index.md) and [`README.md`](../README.md).
