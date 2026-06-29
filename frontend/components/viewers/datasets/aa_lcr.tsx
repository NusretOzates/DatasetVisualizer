import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

type DocumentPreview = {
  filename?: string;
  preview?: string;
  word_count?: number;
  truncated?: boolean;
  missing?: boolean;
};

function asStringList(value: unknown): string[] {
  if (value == null) return [];
  if (Array.isArray(value)) {
    return value.flatMap((item) => asStringList(item));
  }
  const text = String(value).trim();
  if (!text) return [];
  if (text.includes(";")) {
    return text.split(";").map((item) => item.trim()).filter(Boolean);
  }
  return [text];
}

function asDocumentPreviews(value: unknown): DocumentPreview[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is DocumentPreview => Boolean(item) && typeof item === "object");
}

function fileName(path: string): string {
  const parts = path.split("/");
  return parts[parts.length - 1] || path;
}

export function AaLcrViewer({ row }: SampleViewerProps) {
  const question = typeof row.question === "string" ? row.question.trim() : "";
  const answer = typeof row.answer === "string" ? row.answer.trim() : "";
  const filenames = asStringList(row.source_filenames ?? row.data_source_filenames);
  const urls = asStringList(row.source_urls ?? row.data_source_urls);
  const documentPreviews = asDocumentPreviews(row.document_previews);
  const combinedPreview =
    typeof row.document_preview === "string" ? row.document_preview.trim() : "";
  const combinedTruncated = Boolean(row.document_preview_truncated);

  if (!question && !answer && !combinedPreview) {
    return <p className="text-sm text-muted-foreground">No fields to display.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.document_set_id ? (
          <Badge variant="outline">Set: {String(row.document_set_id)}</Badge>
        ) : null}
        {row.document_category ? (
          <Badge variant="secondary">{String(row.document_category)}</Badge>
        ) : null}
        {row.input_tokens != null ? (
          <Badge variant="outline">{Number(row.input_tokens).toLocaleString()} input tokens</Badge>
        ) : null}
        {row.source_file_count != null ? (
          <Badge variant="secondary">{String(row.source_file_count)} source files</Badge>
        ) : null}
      </div>

      {question ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Question</h4>
          <MarkdownMath className="mt-2 text-sm leading-relaxed">{question}</MarkdownMath>
        </div>
      ) : null}

      {combinedPreview ? (
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h4 className="text-sm font-medium text-muted-foreground">Document preview</h4>
            <Badge variant="outline">First 500 words</Badge>
            {combinedTruncated ? <Badge variant="secondary">Truncated</Badge> : null}
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            Combined source documents in filename order. Full context averages ~100k tokens per
            question.
          </p>
          <pre className="code-block mt-2 max-h-96 overflow-y-auto whitespace-pre-wrap text-sm leading-relaxed">
            {combinedPreview}
          </pre>
        </div>
      ) : null}

      {answer ? (
        <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          <strong>Reference answer:</strong>
          <pre className="mt-2 whitespace-pre-wrap font-mono text-sm">{answer}</pre>
        </div>
      ) : null}

      {documentPreviews.length || filenames.length || urls.length ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="sources">
            <AccordionTrigger className="text-sm">
              Source documents ({documentPreviews.length || filenames.length || urls.length})
            </AccordionTrigger>
            <AccordionContent className="space-y-3">
              {documentPreviews.length
                ? documentPreviews.map((doc, index) => {
                    const label = fileName(String(doc.filename ?? `document-${index + 1}`));
                    const url = urls[index] ?? urls[0];
                    return (
                      <div key={`${label}-${index}`} className="rounded-md border px-3 py-3">
                        <div className="flex flex-wrap items-center gap-2">
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
                          {doc.missing ? <Badge variant="destructive">Missing</Badge> : null}
                          {doc.truncated ? <Badge variant="secondary">500-word preview</Badge> : null}
                          {doc.word_count != null && doc.word_count > 0 ? (
                            <Badge variant="outline">{doc.word_count.toLocaleString()} words total</Badge>
                          ) : null}
                        </div>
                        {doc.preview ? (
                          <pre className="code-block mt-2 max-h-64 overflow-y-auto whitespace-pre-wrap text-sm leading-relaxed">
                            {doc.preview}
                          </pre>
                        ) : null}
                      </div>
                    );
                  })
                : filenames.map((path, index) => {
                    const url = urls[index] ?? urls[0];
                    const label = fileName(path);
                    return (
                      <div key={`${path}-${index}`} className="rounded-md border px-3 py-2 text-sm">
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
                        <p className="mt-1 break-all font-mono text-xs text-muted-foreground">
                          {path}
                        </p>
                      </div>
                    );
                  })}
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
