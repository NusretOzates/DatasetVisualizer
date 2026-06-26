# Code map

Use this map to locate the right files before searching the whole repository.

| Capability / Concern | Entry point | Key files | Tests |
|------------------------|------------------------------|-------------------------------|-----------------------------|
| App launch (`dataset-viz`) | `dataset_visualizer.cli:main` | `src/dataset_visualizer/cli.py`, `src/dataset_visualizer/server.py` | `tests/test_cli.py` |
| Pre-download CLI | `dataset_visualizer.pre_download:main` | `src/dataset_visualizer/pre_download.py` | `tests/test_pre_download.py` |
| Smallest Hub split selection | `dataset_visualizer.loaders.split_select:select_smallest_split` | `src/dataset_visualizer/loaders/split_select.py` | `tests/test_split_select.py` |
| Config load / validation | `dataset_visualizer.config:load_config` | `config/datasets.yaml`, `src/dataset_visualizer/config.py` | `tests/test_config.py` |
| Dataset catalog and metadata | `dataset_visualizer.api.service:get_catalog` | `config/datasets.yaml`, `src/dataset_visualizer/api/service.py`, `src/dataset_visualizer/source_links.py` | `tests/test_api_service.py`, `tests/test_home.py`, `tests/test_source_links.py` |
| Dataset registration | `dataset_visualizer.api.dataset_registry:get_descriptor` | `src/dataset_visualizer/api/dataset_registry.py` | `tests/test_registry.py`, `tests/test_benchmark_registry.py` |
| Manual Hugging Face loaders | `dataset_visualizer.loaders.*:load_*` | `src/dataset_visualizer/loaders/*.py`, `src/dataset_visualizer/loaders/base.py` | `tests/test_loaders_*.py` |
| Generic HF benchmark loading | `dataset_visualizer.loaders.hf_benchmark:load_hf_benchmark_entry` | `src/dataset_visualizer/loaders/hf_benchmark.py`, `src/dataset_visualizer/loaders/benchmark_normalize.py` | `tests/test_loaders_hf_benchmark.py`, `tests/test_benchmark_normalize.py` |
| MTOB ciphertext decryption | `dataset_visualizer.loaders.mtob_crypto:decrypt_mtob_text` | `src/dataset_visualizer/loaders/mtob_crypto.py`, `profile: mtob` in `benchmark_normalize.py` | `tests/test_mtob_crypto.py` |
| Loader in-process cache | `dataset_visualizer.loaders.cache:loader_cache` | `src/dataset_visualizer/loaders/cache.py` | `tests/test_cache.py` |
| Overview payloads (manual) | `dataset_visualizer.api.overview:overview_*` | `src/dataset_visualizer/api/overview.py` | `tests/test_api_service.py` |
| Overview payloads (generic HF) | `dataset_visualizer.api.generic_overview:overview_generic` | `src/dataset_visualizer/api/generic_overview.py` | `tests/test_generic_overview.py` |
| Filter options and filtering | `dataset_visualizer.api.service:get_filter_options` | `src/dataset_visualizer/api/filters.py`, `src/dataset_visualizer/api/dataset_registry.py` | `tests/test_filters.py`, `tests/test_api_service.py` |
| Sample lookup and inspection | `dataset_visualizer.api.service:get_sample` | `src/dataset_visualizer/api/service.py`, `src/dataset_visualizer/api/serializers.py` | `tests/test_api_service.py` |
| Home-page row counts | `dataset_visualizer.row_count:row_count` | `src/dataset_visualizer/row_count.py`, `src/dataset_visualizer/api/service.py` | `tests/test_home.py` |
| Inspect CLI | `scripts.inspect_dataset:inspect_dataset` | `scripts/inspect_dataset.py` | `tests/test_inspect_dataset.py` |
| MCQ helpers | `dataset_visualizer.utils.mcq:resolve_correct_letter` | `src/dataset_visualizer/utils/mcq.py` | `tests/test_components_mcq.py` |
| React overview tab | `frontend/components/OverviewTab.tsx:OverviewTab` | `frontend/components/DatasetReadme.tsx`, `frontend/lib/types.ts` | Frontend lint/typecheck |
| React sample viewers | `frontend/components/viewers/registry.tsx:renderSample` | `frontend/components/viewers/datasets/*.tsx`, `frontend/components/viewers/*Viewer.tsx`, `scripts/scaffold_dataset_viewer.py` | `tests/test_benchmark_registry.py`, frontend typecheck |
| Dataset README (Overview) | `frontend/components/DatasetReadme.tsx:DatasetReadme` | `src/dataset_visualizer/dataset_readme.py:get_dataset_readme`, `frontend/components/MarkdownContent.tsx` | `tests/test_dataset_readme.py` |
| Dataset visual audit | `scripts/audit_datasets.py:audit_datasets` | `docs/audit/dataset-audit-matrix.md`, `scripts/capture_audit_screenshots.py` | `scripts/audit_datasets.py` |
| ARC-AGI grid visualization | `frontend/components/viewers/ArcGridViewer.tsx:ArcGridViewer` | `config/datasets.yaml`, `frontend/components/viewers/registry.tsx` | `tests/test_benchmark_registry.py` |
| Code-eval sample viewer | `frontend/components/viewers/CodeEvalViewer.tsx` | `frontend/components/viewers/registry.tsx` | `tests/test_benchmark_registry.py` |
| Generic sample viewer | `frontend/components/viewers/GenericViewer.tsx` | `frontend/components/viewers/registry.tsx` | `tests/test_benchmark_registry.py` |
| Static frontend routes | `frontend/app/dataset/[id]/page.tsx:generateStaticParams` | `frontend/lib/api.ts`, `src/dataset_visualizer/server.py` | Frontend build |
| Frontend lint/type quality | `frontend/eslint.config.mjs` | `frontend/package.json`, `frontend/tsconfig.json` | `npm run lint`, `npm run typecheck` |

## Related navigation

- [Architecture overview](overview.md) — boundaries and Mermaid diagrams
- [Glossary](../glossary.md) — domain terms (`profile`, `viewer`, `hf_benchmark`, …)
- [How to add a dataset](../how-to/add-dataset.md) — registration playbooks
