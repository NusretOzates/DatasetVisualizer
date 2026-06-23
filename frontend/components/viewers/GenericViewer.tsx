"use client";

import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

type GenericViewerProps = {
  row: Record<string, unknown>;
};

const HIDDEN_KEYS = new Set(["split", "sample_id"]);

function formatValue(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function isLongText(value: string): boolean {
  return value.length > 240 || value.includes("\n");
}

export function GenericViewer({ row }: GenericViewerProps) {
  const entries = Object.entries(row).filter(([key, value]) => {
    if (HIDDEN_KEYS.has(key)) return false;
    if (value == null) return false;
    if (typeof value === "string" && !value.trim()) return false;
    return true;
  });

  if (!entries.length) {
    return <p className="text-sm text-muted-foreground">No fields to display.</p>;
  }

  const preview = entries.slice(0, 6);
  const rest = entries.slice(6);

  return (
    <div className="space-y-4">
      {preview.map(([key, value]) => {
        const text = formatValue(value);
        const label = key.replace(/_/g, " ");
        if (isLongText(text)) {
          return (
            <Accordion key={key} type="single" collapsible>
              <AccordionItem value={key}>
                <AccordionTrigger className="text-sm capitalize">{label}</AccordionTrigger>
                <AccordionContent>
                  <pre className="code-block whitespace-pre-wrap">{text}</pre>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          );
        }
        return (
          <div key={key}>
            <h4 className="text-sm font-medium capitalize text-muted-foreground">{label}</h4>
            <p className="mt-1 text-sm leading-relaxed">{text}</p>
          </div>
        );
      })}

      {rest.length ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="all-fields">
            <AccordionTrigger className="text-sm">
              All fields <Badge variant="secondary">{rest.length}</Badge>
            </AccordionTrigger>
            <AccordionContent>
              <pre className="code-block">{JSON.stringify(Object.fromEntries(rest), null, 2)}</pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
