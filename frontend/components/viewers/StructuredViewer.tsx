"use client";

import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { MarkdownMath } from "./MarkdownMath";

export type StructuredViewerConfig = {
  heroFields?: readonly string[];
  badgeFields?: readonly string[];
  hideFields?: readonly string[];
  title?: string;
};

type StructuredViewerProps = {
  row: Record<string, unknown>;
  config?: StructuredViewerConfig;
};

const DEFAULT_HIDE = new Set(["split", "sample_id"]);

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

function hasValue(value: unknown): boolean {
  if (value == null) return false;
  if (typeof value === "string") return Boolean(value.trim());
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === "object") return Object.keys(value as object).length > 0;
  return true;
}

function isLongText(value: string): boolean {
  return value.length > 240 || value.includes("\n");
}

function labelForKey(key: string): string {
  return key.replace(/_/g, " ");
}

export function StructuredViewer({ row, config }: StructuredViewerProps) {
  const hide = new Set([...DEFAULT_HIDE, ...(config?.hideFields ?? [])]);
  const heroFields = config?.heroFields ?? [];
  const badgeFields = config?.badgeFields ?? [];
  const used = new Set<string>();

  const badges = badgeFields
    .filter((key) => hasValue(row[key]))
    .map((key) => {
      used.add(key);
      return { key, value: String(row[key]) };
    });

  const heroes = heroFields
    .filter((key) => hasValue(row[key]))
    .map((key) => {
      used.add(key);
      return { key, text: formatValue(row[key]) };
    });

  const rest = Object.entries(row).filter(([key, value]) => {
    if (hide.has(key) || used.has(key)) return false;
    return hasValue(value);
  });

  if (!badges.length && !heroes.length && !rest.length) {
    return <p className="text-sm text-muted-foreground">No fields to display.</p>;
  }

  return (
    <div className="space-y-4">
      {config?.title ? (
        <h3 className="text-base font-semibold tracking-tight">{config.title}</h3>
      ) : null}

      {badges.length ? (
        <div className="flex flex-wrap gap-2">
          {badges.map(({ key, value }) => (
            <Badge key={key} variant="outline">
              {labelForKey(key)}: {value}
            </Badge>
          ))}
        </div>
      ) : null}

      {heroes.map(({ key, text }) => (
        <div key={key}>
          <h4 className="text-sm font-medium capitalize text-muted-foreground">
            {labelForKey(key)}
          </h4>
          {isLongText(text) ? (
            <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
              {text}
            </MarkdownMath>
          ) : (
            <p className="mt-2 text-sm leading-relaxed">{text}</p>
          )}
        </div>
      ))}

      {rest.length ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="additional-fields">
            <AccordionTrigger className="text-sm">
              Additional fields <Badge variant="secondary">{rest.length}</Badge>
            </AccordionTrigger>
            <AccordionContent>
              <div className="space-y-3">
                {rest.map(([key, value]) => {
                  const text = formatValue(value);
                  return (
                    <div key={key}>
                      <h5 className="text-sm font-medium capitalize text-muted-foreground">
                        {labelForKey(key)}
                      </h5>
                      <pre className="code-block mt-1 whitespace-pre-wrap text-sm">{text}</pre>
                    </div>
                  );
                })}
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
