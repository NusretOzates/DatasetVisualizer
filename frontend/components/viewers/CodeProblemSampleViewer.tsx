"use client";

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { CodeProblemViewer } from "./CodeProblemViewer";
import type { SampleViewerProps } from "./types";

export function CodeProblemSampleViewer({ row, privateTests }: SampleViewerProps) {
  return (
    <div className="space-y-4">
      <CodeProblemViewer row={row} />
      {privateTests ? (
        <Collapsible>
          <CollapsibleTrigger>Private test cases</CollapsibleTrigger>
          <CollapsibleContent className="pt-3">
            <CodeProblemViewer row={{ public_test_cases: privateTests }} />
          </CollapsibleContent>
        </Collapsible>
      ) : null}
    </div>
  );
}
