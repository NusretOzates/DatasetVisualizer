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
| Home page | `components/HomePage.tsx` | Dataset catalog table |
| Dataset routes | `app/dataset/[id]/page.tsx` | Static export; routes from `generateStaticParams` |
| API client | `lib/api.ts` | `@gradio/client` wrappers |
| Catalog hook | `lib/useCatalog.ts` | Client-side catalog fetch |
| Types | `lib/types.ts` | Catalog, overview, chart, control, and filter types |
| Explorer | `components/DatasetExplorer.tsx` | Controls, filters, tabs (via `lib/useDatasetQuery.ts`) |
| Overview | `components/OverviewTab.tsx`, `ChartPanel.tsx` | Metrics + Plotly charts |
| Samples | `components/SampleInspector.tsx` | Index slider, ID search, viewers |
| Viewer registry | `components/viewers/registry.tsx` | Maps API `viewer` key → React component |

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
| `code_problem` | `CodeProblemSampleViewer` | Public tests + optional private tests |
| `issue_resolution` | `IssueViewer` | SWE-bench style patches and test lists |
| `academic_qa` | `HleViewer` | HLE questions, images, answer types |
| `math_competition` | `MathViewer` | Competition problems + solution extras |
| `arxiv_math` | `ArxivMathViewer` | ArXiv Math problems + model-run tables |

Custom viewers live in `components/viewers/` (e.g. `McqCotViewer.tsx`, `CodeProblemSampleViewer.tsx`).

## Chart payloads

Overview charts are built server-side in `api/chart_data.py` and rendered client-side with `react-plotly.js`. Supported `type` values:

- `bar`, `pie`, `histogram`, `stacked_bar`, `timeline`, `scatter`

See `lib/types.ts` for the full TypeScript shapes. Filter option payloads use the `FilterOptions` type.

## Documentation

When changing frontend architecture, routes, viewers, or build requirements, update this file and cross-links in [`docs/index.md`](index.md) and [`README.md`](../README.md).
