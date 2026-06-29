import { Badge } from "@/components/ui/badge";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

export function AaOmniscienceViewer({ row }: SampleViewerProps) {
  const question = typeof row.question === "string" ? row.question.trim() : "";
  const answer = typeof row.answer === "string" ? row.answer.trim() : "";

  if (!question && !answer) {
    return <p className="text-sm text-muted-foreground">No fields to display.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.question_id != null ? (
          <Badge variant="outline">ID: {String(row.question_id)}</Badge>
        ) : null}
        {row.domain ? <Badge variant="secondary">{String(row.domain)}</Badge> : null}
        {row.topic ? <Badge variant="outline">{String(row.topic)}</Badge> : null}
      </div>

      {question ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Question</h4>
          <MarkdownMath className="mt-2 text-sm leading-relaxed">{question}</MarkdownMath>
        </div>
      ) : null}

      {answer ? (
        <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          <strong>Reference answer:</strong> {answer}
        </div>
      ) : null}
    </div>
  );
}
