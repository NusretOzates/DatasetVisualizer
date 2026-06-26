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

function compactKwargs(value: unknown): unknown {
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return null;
    try {
      return compactKwargs(JSON.parse(trimmed));
    } catch {
      return value;
    }
  }
  if (Array.isArray(value)) {
    const items = value
      .map((item) => compactKwargs(item))
      .filter((item) => {
        if (item == null) return false;
        if (typeof item === "object" && !Array.isArray(item)) {
          return Object.keys(item).length > 0;
        }
        return true;
      });
    return items.length ? items : null;
  }
  if (value && typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>).filter(
      ([, entryValue]) => entryValue != null,
    );
    if (!entries.length) return null;
    return Object.fromEntries(entries);
  }
  return value;
}

function formatKwargs(value: unknown): string {
  const compacted = compactKwargs(value);
  if (compacted == null) return "";
  if (typeof compacted === "string") return compacted;
  try {
    return JSON.stringify(compacted, null, 2);
  } catch {
    return String(compacted);
  }
}

function parseInstructionIdList(value: unknown): string[] {
  if (value == null) return [];
  if (Array.isArray(value)) {
    return value.flatMap((item) => parseInstructionIdList(item));
  }
  if (typeof value !== "string") {
    return [String(value).trim()].filter(Boolean);
  }
  const trimmed = value.trim();
  if (!trimmed) return [];
  if (trimmed.startsWith("[") || trimmed.startsWith("{")) {
    try {
      return parseInstructionIdList(JSON.parse(trimmed));
    } catch {
      return [trimmed];
    }
  }
  return trimmed
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatInstructionChip(label: string): string {
  return label.replace(/_/g, " ");
}

export function InstructionViewer({ row }: InstructionViewerProps) {
  const prompt = String(row.prompt ?? row.question ?? "");
  const kwargs = formatKwargs(row.kwargs);
  const instructionIds = parseInstructionIdList(row.instruction_id_list);
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

      {instructionIds.length ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Instruction checks</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {instructionIds.map((instruction) => (
              <Badge key={instruction} variant="secondary" className="font-mono text-xs">
                {formatInstructionChip(instruction)}
              </Badge>
            ))}
          </div>
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
