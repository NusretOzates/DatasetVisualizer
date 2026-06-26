import { Badge } from "@/components/ui/badge";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

export function DabstepViewer({ row }: SampleViewerProps) {
  const question = typeof row.question === "string" ? row.question.trim() : "";
  const guidelines = typeof row.guidelines === "string" ? row.guidelines.trim() : "";
  const level = typeof row.level === "string" ? row.level.trim() : "";
  const answer = typeof row.answer === "string" ? row.answer.trim() : "";

  if (!question && !guidelines && !answer) {
    return <p className="text-sm text-muted-foreground">No fields to display.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.task_id != null ? (
          <Badge variant="outline">task id: {String(row.task_id)}</Badge>
        ) : null}
        {level ? <Badge variant="secondary">{level}</Badge> : null}
      </div>

      {question ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Question</h4>
          <MarkdownMath className="mt-2 text-sm leading-relaxed">{question}</MarkdownMath>
        </div>
      ) : null}

      {guidelines ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Guidelines</h4>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{guidelines}</p>
        </div>
      ) : null}

      {answer ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Reference answer</h4>
          <p className="mt-2 font-mono text-sm leading-relaxed">{answer}</p>
        </div>
      ) : null}
    </div>
  );
}
