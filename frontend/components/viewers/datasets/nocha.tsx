import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

type ModelResponse = {
  model?: string;
  response?: string;
  skipped?: boolean;
};

function asModelResponses(value: unknown): ModelResponse[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is ModelResponse => typeof item === "object" && item != null);
}

export function NochaViewer({ row, extras }: SampleViewerProps) {
  const claim = typeof row.claim === "string" ? row.claim : "";
  const pairedClaim = typeof row.paired_claim === "string" ? row.paired_claim : "";
  const falseExplanation =
    typeof row.false_claim_explanation === "string" ? row.false_claim_explanation : "";
  const bookPreview = typeof extras.book_text_preview === "string" ? extras.book_text_preview : "";
  const bookChars =
    typeof extras.book_char_count === "number" ? extras.book_char_count : Number(row.length ?? 0);
  const omittedChars =
    typeof extras.book_text_omitted_chars === "number" ? extras.book_text_omitted_chars : 0;
  const modelResponses = asModelResponses(row.model_responses);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.book_title ? <Badge variant="outline">{String(row.book_title)}</Badge> : null}
        {row.claim_type ? <Badge variant="secondary">{String(row.claim_type)} claim</Badge> : null}
        {row.pair_index != null ? (
          <Badge variant="outline">pair {String(row.pair_index)}</Badge>
        ) : null}
        {row.length_group ? <Badge variant="secondary">{String(row.length_group)}</Badge> : null}
        {row.genre ? <Badge variant="outline">{String(row.genre)}</Badge> : null}
      </div>

      {claim ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Claim</h4>
          <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {claim}
          </MarkdownMath>
        </div>
      ) : null}

      {pairedClaim ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">
            Paired {String(row.paired_claim_type ?? "claim")}
          </h4>
          <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {pairedClaim}
          </MarkdownMath>
        </div>
      ) : null}

      {falseExplanation ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">False-claim explanation</h4>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{falseExplanation}</p>
        </div>
      ) : null}

      {bookPreview ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Book context</h4>
          <p className="mt-1 text-xs text-muted-foreground">
            Showing preview of {bookPreview.length.toLocaleString()} characters
            {bookChars ? ` (${bookChars.toLocaleString()} total)` : ""}
            {omittedChars > 0
              ? ` — ${omittedChars.toLocaleString()} characters omitted from API payload`
              : ""}
            .
          </p>
          <MarkdownMath className="mt-2 max-h-[28rem] overflow-y-auto whitespace-pre-wrap rounded-lg border bg-muted/20 p-4 text-sm leading-relaxed">
            {bookPreview}
          </MarkdownMath>
        </div>
      ) : null}

      {modelResponses.length ? (
        <Accordion type="multiple" className="w-full">
          <AccordionItem value="model-responses">
            <AccordionTrigger className="text-sm">
              Published model responses ({modelResponses.length})
            </AccordionTrigger>
            <AccordionContent>
              <div className="space-y-3">
                {modelResponses.map((item, index) => (
                  <div key={`${item.model ?? "model"}-${index}`} className="rounded-md border p-3">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{item.model ?? "model"}</Badge>
                      {item.skipped ? <Badge variant="secondary">skipped</Badge> : null}
                    </div>
                    {item.response && !item.skipped ? (
                      <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
                        {item.response}
                      </MarkdownMath>
                    ) : null}
                  </div>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
