"use client";

import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { MarkdownMath } from "./MarkdownMath";
import type { SampleViewerProps } from "./types";

function displayText(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function metadataEntries(metadata: Record<string, unknown>): Array<[string, unknown]> {
  return Object.entries(metadata).filter(([, value]) => {
    if (value == null) return false;
    if (typeof value === "string") return Boolean(value.trim());
    return true;
  });
}

/** Agent/tool benchmark viewer with question-first layout. */
export function AgentBenchViewer({ row }: SampleViewerProps) {
  const question = row.question ?? row.Question ?? row.task ?? row.instruction;
  const answer = row.answer ?? row.ground_truth ?? row.expected_answer;
  const annotatorMetadata = row.annotator_metadata as Record<string, unknown> | undefined;
  const metaEntries = annotatorMetadata ? metadataEntries(annotatorMetadata) : [];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge>{String(row.task_id ?? row.id ?? row.sample_id ?? "—")}</Badge>
        {row.category ? <Badge variant="outline">{String(row.category)}</Badge> : null}
        {row.domain ? <Badge variant="outline">{String(row.domain)}</Badge> : null}
        {row.level ? <Badge variant="secondary">Level {String(row.level)}</Badge> : null}
      </div>

      {question ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Question</h4>
          <MarkdownMath className="mt-2 text-sm leading-relaxed">
            {displayText(question)}
          </MarkdownMath>
        </div>
      ) : null}

      {answer ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Answer</h4>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {displayText(answer)}
          </p>
        </div>
      ) : null}

      {metaEntries.length ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="annotator-metadata">
            <AccordionTrigger>Annotator metadata</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-3">
                {metaEntries.map(([key, value]) => (
                  <div key={key}>
                    <h5 className="text-sm font-medium capitalize text-muted-foreground">
                      {key.replace(/_/g, " ")}
                    </h5>
                    <p className="mt-1 whitespace-pre-wrap text-sm leading-relaxed">
                      {displayText(value)}
                    </p>
                  </div>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
