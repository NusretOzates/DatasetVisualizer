import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
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

export function GaiaViewer({ row }: SampleViewerProps) {
  const question = row.question ?? row.Question;
  const answer = row.answer ?? row["Final answer"];
  const scenarioConfig = row.scenario_config;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge>{String(row.task_id ?? row.id ?? row.sample_id ?? "—")}</Badge>
        {row.subject ? <Badge variant="outline">{String(row.subject)}</Badge> : null}
        {row.category ? <Badge variant="outline">{String(row.category)}</Badge> : null}
        {row.scenario_id ? <Badge variant="secondary">{String(row.scenario_id)}</Badge> : null}
        {row.level ? <Badge variant="secondary">Level {String(row.level)}</Badge> : null}
      </div>

      {question ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Question</h4>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{displayText(question)}</p>
        </div>
      ) : null}

      {answer ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Answer</h4>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{displayText(answer)}</p>
        </div>
      ) : null}

      {row.file_name || row.file_path ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Attachment</h4>
          <p className="mt-2 text-sm">{String(row.file_name ?? row.file_path)}</p>
        </div>
      ) : null}

      {scenarioConfig ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="scenario-config">
            <AccordionTrigger>Scenario configuration</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block whitespace-pre-wrap">{displayText(scenarioConfig)}</pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
