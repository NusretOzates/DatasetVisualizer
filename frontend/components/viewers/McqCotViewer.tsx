"use client";

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { McqViewer } from "./McqViewer";
import type { SampleViewerProps } from "./registry";

export function McqCotViewer({ row }: SampleViewerProps) {
  return (
    <div className="space-y-4">
      <McqViewer row={row} choicesCol="options" answerCol="answer" />
      {row.cot_content ? (
        <Collapsible>
          <CollapsibleTrigger>Chain-of-thought</CollapsibleTrigger>
          <CollapsibleContent className="pt-3">
            <pre className="code-block">{String(row.cot_content)}</pre>
          </CollapsibleContent>
        </Collapsible>
      ) : null}
    </div>
  );
}
