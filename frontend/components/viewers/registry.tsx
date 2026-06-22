"use client";

import type { ComponentType, ReactNode } from "react";
import type { DatasetMeta } from "@/lib/types";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ChevronDown } from "lucide-react";
import { ArxivMathViewer } from "./ArxivMathViewer";
import { CodeProblemViewer } from "./CodeProblemViewer";
import { HleViewer } from "./HleViewer";
import { IssueViewer } from "./IssueViewer";
import { MathViewer } from "./MathViewer";
import { McqViewer } from "./McqViewer";

export type SampleViewerProps = {
  row: Record<string, unknown>;
  extras: Record<string, unknown>;
  privateTests: Record<string, unknown>[] | null;
};

function McqCotViewer({ row }: SampleViewerProps) {
  return (
    <div className="space-y-4">
      <McqViewer row={row} choicesCol="options" answerCol="answer" />
      {row.cot_content ? (
        <Collapsible>
          <CollapsibleTrigger>
            <ChevronDown className="size-4" />
            Chain-of-thought
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-3">
            <pre className="code-block">{String(row.cot_content)}</pre>
          </CollapsibleContent>
        </Collapsible>
      ) : null}
    </div>
  );
}

function CodeProblemSampleViewer({ row, privateTests }: SampleViewerProps) {
  return (
    <div className="space-y-4">
      <CodeProblemViewer row={row} />
      {privateTests ? (
        <Collapsible>
          <CollapsibleTrigger>
            <ChevronDown className="size-4" />
            Private test cases
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-3">
            <CodeProblemViewer row={{ public_test_cases: privateTests }} />
          </CollapsibleContent>
        </Collapsible>
      ) : null}
    </div>
  );
}

const VIEWER_REGISTRY: Record<string, ComponentType<SampleViewerProps>> = {
  mcq: ({ row }) => <McqViewer row={row} />,
  mcq_multilingual: ({ row }) => <McqViewer row={row} />,
  mcq_cot: McqCotViewer,
  math_competition: ({ row, extras }) => (
    <MathViewer row={row} solution={String(extras.solution ?? "")} />
  ),
  arxiv_math: ({ row, extras }) => <ArxivMathViewer row={row} extras={extras} />,
  academic_qa: ({ row }) => <HleViewer row={row} />,
  code_problem: CodeProblemSampleViewer,
  issue_resolution: ({ row }) => <IssueViewer row={row} />,
};

export function renderSample(
  meta: DatasetMeta,
  payload: { row: Record<string, unknown> | null; extras: Record<string, unknown> },
  privateTests: Record<string, unknown>[] | null,
): ReactNode {
  if (!payload.row) {
    return <p className="text-sm text-muted-foreground">No sample available.</p>;
  }

  const viewerKey = meta.viewer ?? meta.archetype ?? "";
  const Viewer = VIEWER_REGISTRY[viewerKey];
  if (!Viewer) {
    return <pre className="code-block">{JSON.stringify(payload.row, null, 2)}</pre>;
  }

  return (
    <Viewer row={payload.row} extras={payload.extras} privateTests={privateTests} />
  );
}
