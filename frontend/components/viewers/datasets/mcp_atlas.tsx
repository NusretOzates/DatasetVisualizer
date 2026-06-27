import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item)).filter(Boolean);
}

function displayJson(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export function McpAtlasViewer({ row }: SampleViewerProps) {
  const prompt = row.prompt ?? row.question;
  const enabledTools = asStringList(row.enabled_tools);
  const claims = asStringList(row.gtfa_claims);
  const trajectory = row.trajectory;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge>{String(row.task_id ?? row.sample_id ?? "—")}</Badge>
        {row.enabled_tool_count != null ? (
          <Badge variant="secondary">{String(row.enabled_tool_count)} tools enabled</Badge>
        ) : null}
        {row.gtfa_claim_count != null ? (
          <Badge variant="outline">{String(row.gtfa_claim_count)} GTFA claims</Badge>
        ) : null}
        {row.trajectory_step_count != null ? (
          <Badge variant="outline">{String(row.trajectory_step_count)} trajectory steps</Badge>
        ) : null}
      </div>

      {prompt ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Prompt</h4>
          <MarkdownMath className="mt-2 text-sm leading-relaxed">{String(prompt)}</MarkdownMath>
        </div>
      ) : null}

      {enabledTools.length ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Enabled tools</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {enabledTools.map((tool) => (
              <Badge key={tool} variant="outline" className="font-mono text-xs">
                {tool}
              </Badge>
            ))}
          </div>
        </div>
      ) : null}

      {claims.length ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">GTFA claims</h4>
          <ul className="mt-2 list-disc space-y-2 pl-5 text-sm leading-relaxed">
            {claims.map((claim, index) => (
              <li key={`${index}-${claim.slice(0, 24)}`}>{claim}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {trajectory ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="trajectory">
            <AccordionTrigger className="text-sm">Reference trajectory</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block mt-1 max-h-[28rem] overflow-y-auto whitespace-pre-wrap text-xs">
                {displayJson(trajectory)}
              </pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
