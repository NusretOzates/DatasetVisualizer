#!/usr/bin/env python3
"""Scaffold per-dataset sample viewer components and registry imports."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml


def _ts_literal(value: object) -> str:
    """Serialize a Python object as a TypeScript-compatible literal."""
    return json.dumps(value, indent=2)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "datasets.yaml"
VIEWERS_DIR = ROOT / "frontend" / "components" / "viewers" / "datasets"
REGISTRY_PATH = ROOT / "frontend" / "components" / "viewers" / "registry.tsx"

STRUCTURED_CONFIGS: dict[str, dict[str, object]] = {
    "ruler": {
        "heroFields": ["input", "context", "question", "answer"],
        "badgeFields": ["task_id", "category", "length"],
    },
    "mrcr": {
        "heroFields": ["prompt", "answer", "context"],
        "badgeFields": ["task_id", "sample_id"],
    },
    "mtob": {
        "heroFields": ["source_text", "target_text", "prompt"],
        "badgeFields": ["task_id", "language_pair"],
    },
    "gdpval": {
        "heroFields": ["task", "description", "question", "reference_answer"],
        "badgeFields": ["task_id", "occupation", "sector"],
    },
    "futurebench": {
        "heroFields": ["question", "prompt", "answer"],
        "badgeFields": ["task_id", "category"],
    },
    "futurex": {
        "heroFields": ["question", "prompt", "answer"],
        "badgeFields": ["task_id", "category"],
    },
    "coconot": {
        "heroFields": ["prompt", "response", "question"],
        "badgeFields": ["id", "category", "label"],
    },
    "dabstep": {
        "heroFields": ["question", "task", "instruction", "ground_truth"],
        "badgeFields": ["task_id", "category"],
    },
}


def _pascal_case(dataset_id: str) -> str:
    parts = re.split(r"[_-]+", dataset_id)
    return "".join(part[:1].upper() + part[1:] for part in parts if part)


def resolve_template(entry: dict[str, object]) -> str:
    """Map a catalog entry to a viewer template key."""
    dataset_id = str(entry["id"])
    archetype = entry.get("archetype")
    profile = entry.get("profile")

    if dataset_id == "hle":
        return "hle"
    if dataset_id == "mmlu_pro":
        return "mcq_cot"
    if dataset_id == "livecodebench_v6":
        return "code_problem"
    if dataset_id == "tau3_bench":
        return "tau3"
    if dataset_id == "arxivmath_0526":
        return "arxiv_math"
    if dataset_id in {"gaia", "gaia2"}:
        return "gaia"
    if dataset_id == "paperbench":
        return "paperbench"
    if dataset_id == "livemcpbench":
        return "agent_bench"
    if dataset_id == "arc_agi_2":
        return "arc_grid"
    if archetype == "issue_resolution":
        return "issue"
    if archetype == "code_eval" or profile == "scicode":
        return "code_eval"
    if profile == "instruction":
        return "instruction"
    if profile == "coconot":
        return "structured"
    if archetype == "math_competition":
        return "math"
    if archetype == "mcq_multilingual":
        return "mcq_multilingual"
    if archetype == "mcq_cot":
        return "mcq_cot"
    if archetype == "mcq":
        return "mcq"
    if dataset_id == "dabstep":
        return "structured"
    return "structured"


MCQ_COLUMN_OVERRIDES: dict[str, dict[str, str]] = {
    "mmlu_pro": {"choicesCol": "options", "answerCol": "answer"},
}


def _mcq_template(entry: dict[str, object]) -> str:
    dataset_id = str(entry["id"])
    component = f"{_pascal_case(dataset_id)}Viewer"
    overrides = MCQ_COLUMN_OVERRIDES.get(dataset_id, {})
    props = ", ".join(f'{key}="{value}"' for key, value in overrides.items())
    mcq_props = f" row={{row}}{f', {props}' if props else ''}"

    badge_fields: list[str] = []
    if dataset_id == "mmlu":
        badge_fields.append("subject")
    if dataset_id in {"arc_challenge", "mmlu_redux"}:
        badge_fields.append("subject")
    if dataset_id == "zebra_logic":
        badge_fields.extend(["puzzle_type", "difficulty"])

    if badge_fields:
        badge_jsx = "\n        ".join(
            f'{{row.{field} ? <Badge variant="outline">{{String(row.{field})}}</Badge> : null}}'
            for field in badge_fields
        )
        return f"""import {{ Badge }} from "@/components/ui/badge";
import {{ McqViewer }} from "../McqViewer";
import type {{ SampleViewerProps }} from "../types";

export function {component}({{ row }}: SampleViewerProps) {{
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {badge_jsx}
      </div>
      <McqViewer{mcq_props} />
    </div>
  );
}}
"""

    return f"""import {{ McqViewer }} from "../McqViewer";
import type {{ SampleViewerProps }} from "../types";

export function {component}({{ row }}: SampleViewerProps) {{
  return <McqViewer{mcq_props} />;
}}
"""


def render_viewer_file(entry: dict[str, object], template: str) -> str:
    """Return TypeScript source for one dataset viewer module."""
    dataset_id = str(entry["id"])
    component = f"{_pascal_case(dataset_id)}Viewer"

    if template == "mcq":
        return _mcq_template(entry)

    if template == "mcq_multilingual":
        return f"""import {{ Badge }} from "@/components/ui/badge";
import {{ McqViewer }} from "../McqViewer";
import type {{ SampleViewerProps }} from "../types";

export function {component}({{ row }}: SampleViewerProps) {{
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {{row.subject ? <Badge variant="outline">{{String(row.subject)}}</Badge> : null}}
        {{row.language ? <Badge variant="secondary">{{String(row.language)}}</Badge> : null}}
        {{row.locale ? <Badge variant="secondary">{{String(row.locale)}}</Badge> : null}}
      </div>
      <McqViewer row={{row}} />
    </div>
  );
}}
"""

    if template == "mcq_cot":
        return f"""import {{ McqCotViewer }} from "../McqCotViewer";
import type {{ SampleViewerProps }} from "../types";

export function {component}(props: SampleViewerProps) {{
  return <McqCotViewer {{...props}} />;
}}
"""

    primitive_imports = {
        "hle": ('import { HleViewer } from "../HleViewer";\n', "HleViewer"),
        "code_problem": (
            'import { CodeProblemSampleViewer } from "../CodeProblemSampleViewer";\n',
            "CodeProblemSampleViewer",
        ),
        "issue": ('import { IssueViewer } from "../IssueViewer";\n', "IssueViewer"),
        "tau3": ('import { Tau3BenchViewer } from "../Tau3BenchViewer";\n', "Tau3BenchViewer"),
        "gaia": ('import { GaiaViewer } from "../GaiaViewer";\n', "GaiaViewer"),
        "paperbench": (
            'import { PaperBenchViewer } from "../PaperBenchViewer";\n',
            "PaperBenchViewer",
        ),
        "agent_bench": (
            'import { AgentBenchViewer } from "../AgentBenchViewer";\n',
            "AgentBenchViewer",
        ),
        "code_eval": ('import { CodeEvalViewer } from "../CodeEvalViewer";\n', "CodeEvalViewer"),
        "instruction": (
            'import { InstructionViewer } from "../InstructionViewer";\n',
            "InstructionViewer",
        ),
        "arc_grid": ('import { ArcGridViewer } from "../ArcGridViewer";\n', "ArcGridViewer"),
        "math": ('import { MathViewer } from "../MathViewer";\n', "MathViewer"),
        "arxiv_math": (
            'import { ArxivMathViewer } from "../ArxivMathViewer";\n',
            "ArxivMathViewer",
        ),
    }

    if template in primitive_imports:
        _import_line, primitive = primitive_imports[template]
        aliased_import = f'import {{ {primitive} as ViewerPrimitive }} from "../{primitive}";\n'
        if template == "math":
            return f"""{aliased_import}import type {{ SampleViewerProps }} from "../types";

export function {component}({{ row, extras }}: SampleViewerProps) {{
  const solution = String(extras.solution ?? row.solution ?? "");
  return <ViewerPrimitive row={{row}} solution={{solution || undefined}} />;
}}
"""
        if template == "arxiv_math":
            return f"""{aliased_import}import type {{ SampleViewerProps }} from "../types";

export function {component}(props: SampleViewerProps) {{
  return <ViewerPrimitive row={{props.row}} extras={{props.extras}} />;
}}
"""
        if template == "arc_grid":
            return f"""{aliased_import}import type {{ SampleViewerProps }} from "../types";

export function {component}({{ row }}: SampleViewerProps) {{
  return <ViewerPrimitive row={{row}} />;
}}
"""
        if template in {"code_problem", "tau3", "gaia", "paperbench", "agent_bench"}:
            return f"""{aliased_import}import type {{ SampleViewerProps }} from "../types";

export function {component}(props: SampleViewerProps) {{
  return <ViewerPrimitive {{...props}} />;
}}
"""
        return f"""{aliased_import}import type {{ SampleViewerProps }} from "../types";

export function {component}({{ row }}: SampleViewerProps) {{
  return <ViewerPrimitive row={{row}} />;
}}
"""

    if template == "structured":
        config = STRUCTURED_CONFIGS.get(
            dataset_id,
            {
                "heroFields": ["question", "prompt", "task", "input", "context", "answer"],
                "badgeFields": ["task_id", "id", "sample_id", "category"],
            },
        )
        config_literal = _ts_literal(config)
        return f"""import {{ StructuredViewer }} from "../StructuredViewer";
import type {{ SampleViewerProps }} from "../types";

const CONFIG = {config_literal} as const;

export function {component}({{ row }}: SampleViewerProps) {{
  return <StructuredViewer row={{row}} config={{CONFIG}} />;
}}
"""

    msg = f"Unknown template: {template}"
    raise ValueError(msg)


def render_registry(entries: list[dict[str, object]]) -> str:
    """Generate registry.tsx keyed by dataset id."""
    imports: list[str] = []
    mappings: list[str] = []
    for entry in sorted(entries, key=lambda item: str(item["id"])):
        dataset_id = str(entry["id"])
        component = f"{_pascal_case(dataset_id)}Viewer"
        imports.append(
            f'import {{ {component} }} from "./datasets/{dataset_id}";',
        )
        mappings.append(f"  {dataset_id}: {component},")

    import_block = "\n".join(imports)
    mapping_block = "\n".join(mappings)
    return f""""use client";

import type {{ ComponentType, ReactNode }} from "react";
import type {{ DatasetMeta }} from "@/lib/types";
import {{ GenericViewer }} from "./GenericViewer";
import type {{ SampleViewerProps }} from "./types";
{import_block}

const DATASET_VIEWERS: Record<string, ComponentType<SampleViewerProps>> = {{
{mapping_block}
}};

export function renderSample(
  meta: DatasetMeta,
  payload: {{ row: Record<string, unknown> | null; extras: Record<string, unknown> }},
  privateTests: Record<string, unknown>[] | null,
  privateTestsLoading = false,
): ReactNode {{
  if (!payload.row) {{
    return <p className="text-sm text-muted-foreground">No sample available.</p>;
  }}

  const Viewer = DATASET_VIEWERS[meta.id];
  if (!Viewer) {{
    if (process.env.NODE_ENV === "development") {{
      return <GenericViewer row={{payload.row}} />;
    }}
    return <pre className="code-block">{{JSON.stringify(payload.row, null, 2)}}</pre>;
  }}

  return (
    <Viewer
      row={{payload.row}}
      extras={{payload.extras}}
      privateTests={{privateTests}}
      privateTestsLoading={{privateTestsLoading}}
    />
  );
}}
"""


def load_entries() -> list[dict[str, object]]:
    """Load all dataset entries from config."""
    raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    entries: list[dict[str, object]] = []
    for datasets in raw["categories"].values():
        entries.extend(datasets)
    return entries


def scaffold(*, write_registry: bool = True) -> list[str]:
    """Generate viewer files for every catalog dataset."""
    entries = load_entries()
    VIEWERS_DIR.mkdir(parents=True, exist_ok=True)

    generated: list[str] = []
    for entry in entries:
        dataset_id = str(entry["id"])
        template = resolve_template(entry)
        content = render_viewer_file(entry, template)
        path = VIEWERS_DIR / f"{dataset_id}.tsx"
        path.write_text(content, encoding="utf-8")
        generated.append(dataset_id)

    if write_registry:
        REGISTRY_PATH.write_text(render_registry(entries), encoding="utf-8")
        ids_path = ROOT / "frontend" / "lib" / "catalog-ids.ts"
        ids_literal = ",\n  ".join(
            f'"{entry["id"]}"' for entry in sorted(entries, key=lambda item: str(item["id"]))
        )
        ids_path.write_text(
            f"export const CATALOG_DATASET_IDS = [\n  {ids_literal},\n] as const;\n",
            encoding="utf-8",
        )

    return generated


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry-only",
        action="store_true",
        help="Only regenerate registry.tsx from existing viewer files.",
    )
    args = parser.parse_args()

    if args.registry_only:
        entries = load_entries()
        REGISTRY_PATH.write_text(render_registry(entries), encoding="utf-8")
        print(f"Updated {REGISTRY_PATH}")
        return 0

    ids = scaffold()
    print(f"Generated {len(ids)} dataset viewers in {VIEWERS_DIR}")
    print(f"Updated {REGISTRY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
