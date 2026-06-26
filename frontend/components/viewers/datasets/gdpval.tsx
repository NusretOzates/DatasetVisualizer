import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

type RubricItem = {
  score?: number;
  criterion?: string;
};

function asStringList(value: unknown): string[] {
  if (value == null) return [];
  if (Array.isArray(value)) {
    return value.flatMap((item) => asStringList(item));
  }
  const text = String(value).trim();
  if (!text) return [];
  if (text.includes("\n")) {
    return text.split("\n").map((item) => item.trim()).filter(Boolean);
  }
  return [text];
}

function fileName(path: string): string {
  const parts = path.split("/");
  return parts[parts.length - 1] || path;
}

function parseRubricJson(value: unknown): RubricItem[] {
  if (value == null) return [];
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return [];
    try {
      return parseRubricJson(JSON.parse(trimmed));
    } catch {
      return [];
    }
  }
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((item) => ({
      score: typeof item.score === "number" ? item.score : Number(item.score),
      criterion: typeof item.criterion === "string" ? item.criterion : String(item.criterion ?? ""),
    }))
    .filter((item) => item.criterion);
}

function FileLinks({
  title,
  paths,
  urls,
}: {
  title: string;
  paths: string[];
  urls: string[];
}) {
  if (!paths.length && !urls.length) return null;

  return (
    <div>
      <h4 className="text-sm font-medium text-muted-foreground">{title}</h4>
      <ul className="mt-2 space-y-2 text-sm">
        {paths.map((path, index) => {
          const url = urls[index] ?? urls[0];
          const label = fileName(path);
          return (
            <li key={`${path}-${index}`} className="rounded-md border px-3 py-2">
              {url ? (
                <a
                  href={url}
                  target="_blank"
                  rel="noreferrer"
                  className="font-medium text-primary hover:underline"
                >
                  {label}
                </a>
              ) : (
                <span className="font-medium">{label}</span>
              )}
              <p className="mt-1 break-all font-mono text-xs text-muted-foreground">{path}</p>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export function GdpvalViewer({ row }: SampleViewerProps) {
  const prompt = typeof row.prompt === "string" ? row.prompt : "";
  const rubricPretty = typeof row.rubric_pretty === "string" ? row.rubric_pretty.trim() : "";
  const rubricItems = parseRubricJson(row.rubric_json);
  const referencePaths = asStringList(row.reference_files);
  const referenceUrls = asStringList(row.reference_file_urls);
  const deliverablePaths = asStringList(row.deliverable_files);
  const deliverableUrls = asStringList(row.deliverable_file_urls);

  if (!prompt && !rubricPretty && !rubricItems.length) {
    return <p className="text-sm text-muted-foreground">No fields to display.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.task_id ? <Badge variant="outline">task id: {String(row.task_id)}</Badge> : null}
        {row.occupation ? <Badge variant="secondary">{String(row.occupation)}</Badge> : null}
        {row.sector ? <Badge variant="outline">{String(row.sector)}</Badge> : null}
      </div>

      {prompt ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Task prompt</h4>
          <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {prompt}
          </MarkdownMath>
        </div>
      ) : null}

      <FileLinks title="Reference files" paths={referencePaths} urls={referenceUrls} />
      <FileLinks title="Deliverable files" paths={deliverablePaths} urls={deliverableUrls} />

      {rubricPretty || rubricItems.length ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="rubric">
            <AccordionTrigger className="text-sm">
              Grading rubric{" "}
              {rubricItems.length ? (
                <Badge variant="secondary" className="ml-2">
                  {rubricItems.length} criteria
                </Badge>
              ) : null}
            </AccordionTrigger>
            <AccordionContent>
              {rubricItems.length ? (
                <ol className="space-y-3 text-sm">
                  {rubricItems.map((item, index) => (
                    <li key={`${item.criterion}-${index}`} className="rounded-md border px-3 py-2">
                      {Number.isFinite(item.score) ? (
                        <Badge variant="outline" className="mb-2">
                          +{item.score}
                        </Badge>
                      ) : null}
                      <p className="leading-relaxed">{item.criterion}</p>
                    </li>
                  ))}
                </ol>
              ) : (
                <pre className="code-block whitespace-pre-wrap text-sm">{rubricPretty}</pre>
              )}
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
