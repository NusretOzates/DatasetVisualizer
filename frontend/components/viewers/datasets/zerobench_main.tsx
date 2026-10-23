import { Badge } from "@/components/ui/badge";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item)).filter(Boolean);
}

export function ZerobenchMainViewer({ row }: SampleViewerProps) {
  const images = asStringList(row.media_images);
  const question = typeof row.question === "string" ? row.question : "";
  const answer = row.answer != null ? String(row.answer) : "";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.id != null ? <Badge variant="outline">id: {String(row.id)}</Badge> : null}
        {row.question_type ? (
          <Badge variant="secondary">question type: {String(row.question_type)}</Badge>
        ) : null}
        <Badge variant="outline">media count: {images.length}</Badge>
      </div>

      {images.map((src, index) => (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          key={`${src.slice(0, 32)}-${index}`}
          src={src}
          alt={`ZeroBench media ${index + 1}`}
          className="max-h-[32rem] w-full rounded-lg border object-contain"
        />
      ))}

      {question ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Question</h4>
          <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {question}
          </MarkdownMath>
        </div>
      ) : null}

      {answer ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Answer</h4>
          <p className="mt-2 text-sm leading-relaxed">{answer}</p>
        </div>
      ) : null}
    </div>
  );
}
