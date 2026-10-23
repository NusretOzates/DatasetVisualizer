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
  index?: number;
  criterion?: string;
  type?: string;
  severity?: string;
};

function rubricItems(value: unknown): RubricItem[] {
  if (!Array.isArray(value)) return [];
  return value.filter(
    (item): item is RubricItem => Boolean(item) && typeof item === "object",
  );
}

export function GdpPdfViewer({ row }: SampleViewerProps) {
  const prompt = typeof row.prompt === "string" ? row.prompt : "";
  const pdfUrl = typeof row.pdf_url === "string" ? row.pdf_url : "";
  const items = rubricItems(row.rubric_items);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.task_id ? <Badge variant="outline">task id: {String(row.task_id)}</Badge> : null}
        {row.domain ? <Badge variant="secondary">{String(row.domain)}</Badge> : null}
        {items.length ? (
          <Badge variant="outline">{items.length} rubric criteria</Badge>
        ) : null}
      </div>

      {prompt ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Prompt</h4>
          <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {prompt}
          </MarkdownMath>
        </div>
      ) : null}

      {pdfUrl ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Source PDF</h4>
          <p className="mt-2 text-sm">
            <a
              href={pdfUrl}
              target="_blank"
              rel="noreferrer"
              className="font-medium text-primary hover:underline"
            >
              Open source PDF
            </a>
          </p>
        </div>
      ) : null}

      {items.length ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="rubric">
            <AccordionTrigger className="text-sm">
              Grading rubric{" "}
              <Badge variant="secondary" className="ml-2">
                {items.length} criteria
              </Badge>
            </AccordionTrigger>
            <AccordionContent>
              <ol className="space-y-3 text-sm">
                {items.map((item, position) => (
                  <li
                    key={`${item.index ?? position}-${item.criterion ?? ""}`}
                    className="rounded-md border px-3 py-2"
                  >
                    <div className="mb-2 flex flex-wrap gap-2">
                      {item.type ? <Badge variant="outline">{item.type}</Badge> : null}
                      {item.severity ? (
                        <Badge variant="secondary">{item.severity}</Badge>
                      ) : null}
                    </div>
                    <p className="leading-relaxed">{item.criterion}</p>
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
