"use client";

import { McqViewer } from "./McqViewer";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { MarkdownMath } from "./MarkdownMath";

type HleViewerProps = {
  row: Record<string, unknown>;
};

export function HleViewer({ row }: HleViewerProps) {
  const hasImage = Boolean(row.has_image);
  const answerType = String(row.answer_type ?? "—");
  const modality = hasImage ? "Multimodal" : "Text only";
  const isMultipleChoice = answerType === "multipleChoice";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">ID: {String(row.id ?? "—")}</Badge>
        <Badge variant="outline">{String(row.category ?? "—")}</Badge>
        <Badge variant="outline">{modality}</Badge>
        <Badge variant="secondary">{answerType}</Badge>
      </div>
      <div>
        <h3 className="text-sm font-medium text-muted-foreground">Question</h3>
        <MarkdownMath className="mt-2 text-base">{String(row.question ?? "")}</MarkdownMath>
      </div>
      {hasImage && row.image ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={String(row.image)}
          alt="Question"
          className="max-h-96 rounded-lg border object-contain"
        />
      ) : null}
      {isMultipleChoice ? (
        <McqViewer row={row} answerCol="answer" hideQuestion />
      ) : null}
      {row.answer && !isMultipleChoice ? (
        <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          <strong>Exact answer:</strong> {String(row.answer)}
        </div>
      ) : null}
      {row.author_name ? (
        <p className="text-sm text-muted-foreground">Contributor: {String(row.author_name)}</p>
      ) : null}
      {row.rationale ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="rationale">
            <AccordionTrigger>Rationale</AccordionTrigger>
            <AccordionContent className="space-y-3">
              <MarkdownMath className="text-sm">{String(row.rationale)}</MarkdownMath>
              {row.rationale_image ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={String(row.rationale_image)}
                  alt="Rationale"
                  className="max-h-64 rounded-lg border object-contain"
                />
              ) : null}
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
