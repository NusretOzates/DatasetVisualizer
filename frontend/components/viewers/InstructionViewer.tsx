"use client";

import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { MarkdownMath } from "./MarkdownMath";

type InstructionViewerProps = {
  row: Record<string, unknown>;
};

function formatKwargs(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export function InstructionViewer({ row }: InstructionViewerProps) {
  const prompt = String(row.prompt ?? row.question ?? "");
  const kwargs = formatKwargs(row.kwargs);
  const instructionId = row.instruction_id ?? row.key ?? row.id ?? row.sample_id;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {instructionId ? <Badge variant="outline">ID: {String(instructionId)}</Badge> : null}
        {row.split ? <Badge variant="secondary">{String(row.split)}</Badge> : null}
      </div>

      {prompt ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Prompt</h4>
          <MarkdownMath className="mt-2 text-sm leading-relaxed">{prompt}</MarkdownMath>
        </div>
      ) : null}

      {kwargs ? (
        <Accordion type="single" collapsible defaultValue="kwargs">
          <AccordionItem value="kwargs">
            <AccordionTrigger className="text-sm">Instruction constraints (kwargs)</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block whitespace-pre-wrap">{kwargs}</pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
