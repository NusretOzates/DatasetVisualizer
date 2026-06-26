import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { collapseRepeatedLines, parseChatML } from "@/lib/chatml";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

type RulerExtraInfo = {
  ground_truth?: {
    answers?: string | string[];
    length?: number;
    index?: number;
  };
  scoring_function?: string;
  ruler_config?: string;
  ruler_task?: string;
  context_length?: number;
  variant?: string;
};

function formatAnswers(answers: string | string[] | undefined): string {
  if (answers == null) return "";
  if (Array.isArray(answers)) return answers.join(", ");
  return String(answers);
}

function asExtraInfo(value: unknown): RulerExtraInfo | null {
  if (!value || typeof value !== "object") return null;
  return value as RulerExtraInfo;
}

export function RulerViewer({ row }: SampleViewerProps) {
  const prompt = typeof row.prompt === "string" ? row.prompt : "";
  const extra = asExtraInfo(row.extra_info);
  const sections = parseChatML(prompt);
  const system = sections.find((section) => section.role === "system");
  const user = sections.find((section) => section.role === "user");
  const userPreview = user ? collapseRepeatedLines(user.content) : "";
  const groundTruth = formatAnswers(extra?.ground_truth?.answers);

  if (!prompt && !extra) {
    return <p className="text-sm text-muted-foreground">No fields to display.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.category ? <Badge variant="outline">{String(row.category)}</Badge> : null}
        {extra?.ruler_task ? <Badge variant="secondary">Task: {extra.ruler_task}</Badge> : null}
        {extra?.context_length != null ? (
          <Badge variant="secondary">Context: {extra.context_length.toLocaleString()} tokens</Badge>
        ) : null}
        {extra?.variant ? <Badge variant="secondary">Variant: {extra.variant}</Badge> : null}
        {extra?.scoring_function ? (
          <Badge variant="outline">Scoring: {extra.scoring_function}</Badge>
        ) : null}
      </div>

      {groundTruth ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Ground truth</h4>
          <p className="mt-1 font-mono text-sm">{groundTruth}</p>
        </div>
      ) : null}

      {system?.content.trim() ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">System</h4>
          <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {system.content.trim()}
          </MarkdownMath>
        </div>
      ) : null}

      {userPreview ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">User prompt</h4>
          <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {userPreview}
          </MarkdownMath>
        </div>
      ) : null}

      <Accordion type="single" collapsible>
        {prompt ? (
          <AccordionItem value="full-prompt">
            <AccordionTrigger className="text-sm">Full prompt (raw ChatML)</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block mt-1 whitespace-pre-wrap text-sm">{prompt}</pre>
            </AccordionContent>
          </AccordionItem>
        ) : null}
        {extra ? (
          <AccordionItem value="extra-info">
            <AccordionTrigger className="text-sm">Task metadata</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block mt-1 whitespace-pre-wrap text-sm">
                {JSON.stringify(extra, null, 2)}
              </pre>
            </AccordionContent>
          </AccordionItem>
        ) : null}
      </Accordion>
    </div>
  );
}
