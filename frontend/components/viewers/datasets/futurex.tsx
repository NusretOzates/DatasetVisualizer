import { Badge } from "@/components/ui/badge";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

function parseGroundTruth(value: unknown): string[] {
  if (value == null) return [];
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean);
  }
  const text = String(value).trim();
  if (!text) return [];
  if (text.startsWith("[") || text.startsWith("(")) {
    try {
      const parsed: unknown = JSON.parse(text.replace(/'/g, '"'));
      if (Array.isArray(parsed)) {
        return parsed.map((item) => String(item).trim()).filter(Boolean);
      }
    } catch {
      try {
        const inner = text.slice(1, -1);
        return inner
          .split(",")
          .map((item) => item.trim().replace(/^['"]|['"]$/g, ""))
          .filter(Boolean);
      } catch {
        return [text];
      }
    }
  }
  return [text];
}

export function FuturexViewer({ row }: SampleViewerProps) {
  const title = typeof row.title === "string" ? row.title.trim() : "";
  const prompt = typeof row.prompt === "string" ? row.prompt.trim() : "";
  const endTime = row.end_time != null ? String(row.end_time) : "";
  const level = row.level != null ? String(row.level) : "";
  const groundTruth = parseGroundTruth(row.ground_truth);

  if (!title && !prompt && !groundTruth.length) {
    return <p className="text-sm text-muted-foreground">No fields to display.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.id != null ? <Badge variant="outline">id: {String(row.id)}</Badge> : null}
        {level ? <Badge variant="secondary">level {level}</Badge> : null}
        {endTime ? <Badge variant="outline">resolves {endTime}</Badge> : null}
      </div>

      {title ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Event</h4>
          <p className="mt-2 text-sm font-medium leading-relaxed">{title}</p>
        </div>
      ) : null}

      {groundTruth.length ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Ground truth</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {groundTruth.map((answer) => (
              <Badge key={answer} variant="secondary" className="font-mono">
                {answer}
              </Badge>
            ))}
          </div>
        </div>
      ) : null}

      {prompt ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Prompt</h4>
          <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {prompt}
          </MarkdownMath>
        </div>
      ) : null}
    </div>
  );
}
