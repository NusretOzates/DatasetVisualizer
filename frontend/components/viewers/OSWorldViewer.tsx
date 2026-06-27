import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { MarkdownContent } from "@/components/MarkdownContent";
import type { SampleViewerProps } from "./types";

function displayJson(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item)).filter(Boolean);
}

export function OSWorldViewer({ row }: SampleViewerProps) {
  const relatedApps = asStringList(row.related_apps);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge>{String(row.task_id ?? row.instance_id ?? "—")}</Badge>
        {row.domain ? <Badge variant="outline">{String(row.domain)}</Badge> : null}
        {row.snapshot ? <Badge variant="secondary">{String(row.snapshot)}</Badge> : null}
        {row.evaluator_func ? (
          <Badge variant="outline">eval: {String(row.evaluator_func)}</Badge>
        ) : null}
        {row.config_step_count != null ? (
          <Badge variant="secondary">{String(row.config_step_count)} setup steps</Badge>
        ) : null}
      </div>

      {row.instruction ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Instruction</h4>
          <div className="mt-2 rounded-lg border bg-muted/20 px-4 py-3 text-sm leading-relaxed">
            <MarkdownContent>{String(row.instruction)}</MarkdownContent>
          </div>
        </div>
      ) : null}

      {relatedApps.length ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Related apps</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {relatedApps.map((app) => (
              <Badge key={app} variant="outline">
                {app}
              </Badge>
            ))}
          </div>
        </div>
      ) : null}

      {row.source ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Source</h4>
          <a
            href={String(row.source)}
            target="_blank"
            rel="noreferrer"
            className="mt-2 block break-all text-sm text-primary underline-offset-4 hover:underline"
          >
            {String(row.source)}
          </a>
        </div>
      ) : null}

      {row.config ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="config">
            <AccordionTrigger className="text-sm">Setup config</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block mt-1 max-h-[24rem] overflow-y-auto whitespace-pre-wrap text-xs">
                {displayJson(row.config)}
              </pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}

      {row.evaluator ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="evaluator">
            <AccordionTrigger className="text-sm">Evaluator</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block mt-1 max-h-[24rem] overflow-y-auto whitespace-pre-wrap text-xs">
                {displayJson(row.evaluator)}
              </pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
