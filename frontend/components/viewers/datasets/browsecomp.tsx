import { Badge } from "@/components/ui/badge";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

export function BrowsecompViewer({ row }: SampleViewerProps) {
  const question = typeof row.question === "string" ? row.question : "";
  const answer = typeof row.answer === "string" ? row.answer : "";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.sample_id ? <Badge variant="outline">{String(row.sample_id)}</Badge> : null}
        {row.problem_topic ? <Badge variant="secondary">{String(row.problem_topic)}</Badge> : null}
        {row.split ? <Badge variant="outline">{String(row.split)}</Badge> : null}
      </div>

      {question ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Question</h4>
          <MarkdownMath className="mt-2 text-base leading-relaxed">{question}</MarkdownMath>
        </div>
      ) : null}

      {answer ? (
        <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          <strong>Reference answer:</strong> {answer}
        </div>
      ) : null}

      <p className="text-xs text-muted-foreground">
        BrowseComp questions require persistent web browsing to solve. Answers are short and
        verified against this reference string.
      </p>
    </div>
  );
}
