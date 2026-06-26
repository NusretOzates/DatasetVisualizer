import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import type { SampleViewerProps } from "./types";

type Gaia2Event = {
  type?: string;
  app?: string;
  function?: string;
  arg?: string;
  value?: unknown;
};

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

function asStringList(value: unknown): string[] {
  if (value == null) return [];
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean);
  }
  const text = String(value).trim();
  if (!text) return [];
  return text.split(",").map((item) => item.trim()).filter(Boolean);
}

function asEventList(value: unknown): Gaia2Event[] {
  if (value == null) return [];
  let parsed: unknown = value;
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return [];
    try {
      parsed = JSON.parse(trimmed);
    } catch {
      return [];
    }
  }
  if (!Array.isArray(parsed)) return [];
  return parsed
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((item) => ({
      type: typeof item.type === "string" ? item.type : undefined,
      app: typeof item.app === "string" ? item.app : undefined,
      function: typeof item.function === "string" ? item.function : undefined,
      arg: typeof item.arg === "string" ? item.arg : undefined,
      value: item.value,
    }));
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
  const scenarioTags = asStringList(row.scenario_tags);
  const scenarioHints = asStringList(row.scenario_hints);
  const appNames = asStringList(row.app_names);
  const eventsSummary = asEventList(row.events_summary);
  const metadataEntries = annotatorMetadata ? annotatorMetadataEntries(annotatorMetadata) : [];
  const eventCount =
    typeof row.event_count === "number"
      ? row.event_count
      : Number.isFinite(Number(row.event_count))
        ? Number(row.event_count)
        : eventsSummary.length;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge>{String(row.task_id ?? row.id ?? row.sample_id ?? "—")}</Badge>
        {row.subject ? <Badge variant="outline">{String(row.subject)}</Badge> : null}
        {row.category ? <Badge variant="outline">{String(row.category)}</Badge> : null}
        {row.scenario_id ? <Badge variant="secondary">{String(row.scenario_id)}</Badge> : null}
        {level ? <Badge variant="secondary">Level {String(level)}</Badge> : null}
        {scenarioTags.map((tag) => (
          <Badge key={tag} variant="outline">
            {tag}
          </Badge>
        ))}
        {eventCount > 0 ? <Badge variant="secondary">{eventCount} events</Badge> : null}
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
              <Badge key={app} variant="outline">
                {app}
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
              <li key={hint}>{hint}</li>
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
        <Accordion type="single" collapsible defaultValue="events-summary">
          <AccordionItem value="events-summary">
            <AccordionTrigger className="text-sm">
              Expected agent actions{" "}
              <Badge variant="secondary" className="ml-2">
                {eventsSummary.length}
              </Badge>
            </AccordionTrigger>
            <AccordionContent>
              <ol className="space-y-3">
                {eventsSummary.map((event, index) => (
                  <li key={`${event.type}-${event.function}-${index}`} className="rounded-md border p-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-medium text-muted-foreground tabular-nums">
                        #{index + 1}
                      </span>
                      {event.type ? <Badge variant="outline">{event.type}</Badge> : null}
                      {event.app ? <Badge variant="secondary">{event.app}</Badge> : null}
                      {event.function ? (
                        <code className="text-xs text-muted-foreground">{event.function}</code>
                      ) : null}
                    </div>
                    {event.arg ? (
                      <p className="mt-2 text-xs text-muted-foreground">arg: {event.arg}</p>
                    ) : null}
                    {event.value != null && String(event.value).trim() ? (
                      <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
                        {displayText(event.value)}
                      </p>
                    ) : null}
                  </li>
                ))}
              </ol>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
