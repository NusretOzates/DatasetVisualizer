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

function hasDisplayValue(value: unknown): boolean {
  if (value == null) return false;
  if (typeof value === "string") return Boolean(value.trim());
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === "object") return Object.keys(value as object).length > 0;
  return true;
}

function annotatorMetadataEntries(
  metadata: Record<string, unknown>,
): Array<[string, unknown]> {
  return Object.entries(metadata).filter(([, value]) => hasDisplayValue(value));
}

export function GaiaViewer({ row }: SampleViewerProps) {
  const question = row.question ?? row.Question;
  const userMessage = row.user_message;
  const answer = row.answer ?? row["Final answer"];
  const level = row.level ?? row.Level;
  const annotatorMetadata =
    (row.annotator_metadata as Record<string, unknown> | undefined) ??
    (row["Annotator Metadata"] as Record<string, unknown> | undefined);
  const scenarioTags = Array.isArray(row.scenario_tags) ? row.scenario_tags : [];
  const scenarioHints = Array.isArray(row.scenario_hints) ? row.scenario_hints : [];
  const appNames = Array.isArray(row.app_names) ? row.app_names : [];
  const eventsSummary = Array.isArray(row.events_summary) ? row.events_summary : [];
  const metadataEntries = annotatorMetadata ? annotatorMetadataEntries(annotatorMetadata) : [];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge>{String(row.task_id ?? row.id ?? row.sample_id ?? "—")}</Badge>
        {row.subject ? <Badge variant="outline">{String(row.subject)}</Badge> : null}
        {row.category ? <Badge variant="outline">{String(row.category)}</Badge> : null}
        {row.scenario_id ? <Badge variant="secondary">{String(row.scenario_id)}</Badge> : null}
        {level ? <Badge variant="secondary">Level {String(level)}</Badge> : null}
        {scenarioTags.map((tag) => (
          <Badge key={String(tag)} variant="outline">
            {String(tag)}
          </Badge>
        ))}
        {typeof row.event_count === "number" ? (
          <Badge variant="secondary">{row.event_count} events</Badge>
        ) : null}
      </div>

      {question ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Question</h4>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{displayText(question)}</p>
        </div>
      ) : null}

      {!question && userMessage ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">User request</h4>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {displayText(userMessage)}
          </p>
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

      {appNames.length ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Simulated apps</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {appNames.map((app) => (
              <Badge key={String(app)} variant="outline">
                {String(app)}
              </Badge>
            ))}
          </div>
        </div>
      ) : null}

      {scenarioHints.length ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Hints</h4>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-relaxed">
            {scenarioHints.map((hint) => (
              <li key={String(hint)}>{String(hint)}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {metadataEntries.length ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="annotator-metadata">
            <AccordionTrigger>Annotator metadata</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-3">
                {metadataEntries.map(([key, value]) => (
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

      {eventsSummary.length ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="events-summary">
            <AccordionTrigger>Expected agent actions</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block whitespace-pre-wrap">
                {displayText(eventsSummary)}
              </pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
