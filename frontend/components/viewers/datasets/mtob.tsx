import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

const DIRECTION_LABELS: Record<string, { source: string; target: string; label: string }> = {
  English_to_Kalamang: {
    label: "English → Kalamang",
    source: "English (source)",
    target: "Kalamang (reference translation)",
  },
  Kalamang_to_English: {
    label: "Kalamang → English",
    source: "Kalamang (source)",
    target: "English (reference translation)",
  },
};

function directionMeta(subtask: string | undefined) {
  if (subtask && subtask in DIRECTION_LABELS) {
    return DIRECTION_LABELS[subtask];
  }
  return {
    label: subtask?.replace(/_/g, " ") ?? "Translation",
    source: "Source text",
    target: "Reference translation",
  };
}

export function MtobViewer({ row }: SampleViewerProps) {
  const subtask = typeof row.subtask === "string" ? row.subtask : undefined;
  const direction = directionMeta(subtask);
  const sourceText = typeof row.source_text === "string" ? row.source_text : "";
  const targetText = typeof row.target_text === "string" ? row.target_text : "";

  if (!sourceText && !targetText) {
    return (
      <p className="text-sm text-muted-foreground">
        MTOB text could not be decrypted. Set <code className="text-xs">MTOB_KEY</code> on the
        backend (default public eval key: <code className="text-xs">mtob-eval-encode</code>) and
        reload the dataset.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">{direction.label}</Badge>
        {row.original_id != null ? (
          <Badge variant="secondary">example id: {String(row.original_id)}</Badge>
        ) : null}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border bg-muted/10 p-4">
          <h4 className="text-sm font-medium text-muted-foreground">{direction.source}</h4>
          <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {sourceText}
          </MarkdownMath>
        </div>
        <div className="rounded-lg border border-primary/20 bg-primary/5 p-4">
          <h4 className="text-sm font-medium text-muted-foreground">{direction.target}</h4>
          <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {targetText}
          </MarkdownMath>
        </div>
      </div>

      <Accordion type="single" collapsible>
        <AccordionItem value="encryption">
          <AccordionTrigger className="text-sm">Encrypted Hub fields</AccordionTrigger>
          <AccordionContent>
            <p className="mb-3 text-xs text-muted-foreground">
              Groq/mtob stores AES-CTR ciphertext on Hugging Face. The viewer decrypts rows at load
              time using <code>MTOB_KEY</code>.
            </p>
            <dl className="grid gap-2 text-sm sm:grid-cols-2">
              {(
                [
                  ["original_ciphertext", row.original_ciphertext],
                  ["original_nonce", row.original_nonce],
                  ["ground_truth_ciphertext", row.ground_truth_ciphertext],
                  ["ground_truth_nonce", row.ground_truth_nonce],
                ] as const
              )
                .filter(([, value]) => value != null && String(value).trim())
                .map(([label, value]) => (
                  <div key={label} className="rounded-md border px-3 py-2">
                    <dt className="text-xs font-medium text-muted-foreground">{label}</dt>
                    <dd className="mt-1 break-all font-mono text-xs">{String(value)}</dd>
                  </div>
                ))}
            </dl>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
