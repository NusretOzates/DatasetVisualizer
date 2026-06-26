import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  conversationWindow,
  parseMrcrExamples,
  parseMrcrMessages,
  previewText,
  type ChatMessage,
  type MrcrTurn,
} from "@/lib/mrcr";
import { cn } from "@/lib/utils";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

function TurnBlock({
  turn,
  compact = false,
}: {
  turn: MrcrTurn;
  compact?: boolean;
}) {
  const label = turn.speaker === "user" ? "User" : "Assistant";
  const text = compact ? previewText(turn.content, 320) : turn.content;

  return (
    <div className="rounded-md border bg-muted/20 p-3">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{text}</MarkdownMath>
    </div>
  );
}

function MessageBlock({
  message,
  index,
  highlighted = false,
}: {
  message: ChatMessage;
  index: number;
  highlighted?: boolean;
}) {
  return (
    <div
      className={cn(
        "rounded-md border p-3",
        highlighted ? "border-primary bg-primary/5 ring-1 ring-primary/30" : "bg-muted/20",
      )}
    >
      <div className="flex items-center gap-2">
        <Badge variant={highlighted ? "default" : "outline"} className="text-xs">
          {message.role}
        </Badge>
        <span className="text-xs text-muted-foreground tabular-nums">message {index}</span>
        {highlighted ? <Badge variant="secondary">recall target</Badge> : null}
      </div>
      <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
        {previewText(message.content, highlighted ? 1200 : 500)}
      </MarkdownMath>
    </div>
  );
}

export function MrcrViewer({ row }: SampleViewerProps) {
  const messages = parseMrcrMessages(row.prompt);
  const desiredIndex = Number(row.desired_msg_index);
  const intro = messages[0]?.content ?? "";
  const { header, examples } = parseMrcrExamples(intro);
  const conversation = messages.slice(1);
  const targetIndex = Number.isFinite(desiredIndex) ? desiredIndex : -1;
  const targetMessage = targetIndex >= 0 ? messages[targetIndex] : undefined;
  const window =
    targetIndex >= 0 ? conversationWindow(messages, targetIndex, 2) : { beforeOmitted: 0, afterOmitted: 0, window: [] };

  const prepend =
    typeof row.random_string_to_prepend === "string" ? row.random_string_to_prepend : "";
  const answer = typeof row.answer === "string" ? row.answer : "";

  if (!messages.length) {
    return <p className="text-sm text-muted-foreground">No prompt messages to display.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.sample_id != null ? (
          <Badge variant="outline">sample id: {String(row.sample_id)}</Badge>
        ) : null}
        {row.n_needles != null ? <Badge variant="secondary">needles: {String(row.n_needles)}</Badge> : null}
        {row.total_messages != null ? (
          <Badge variant="secondary">messages: {String(row.total_messages)}</Badge>
        ) : null}
        {row.n_chars != null ? (
          <Badge variant="secondary">chars: {Number(row.n_chars).toLocaleString()}</Badge>
        ) : null}
        {Number.isFinite(desiredIndex) ? (
          <Badge variant="outline">recall index: {desiredIndex}</Badge>
        ) : null}
      </div>

      {header ? <p className="text-sm leading-relaxed text-muted-foreground">{header}</p> : null}

      {examples.length ? (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground">Few-shot examples</h4>
          <Accordion type="multiple" className="w-full">
            {examples.map((example, exampleIndex) => (
              <AccordionItem key={exampleIndex} value={`example-${exampleIndex}`}>
                <AccordionTrigger className="text-sm">
                  Example {exampleIndex + 1}{" "}
                  <Badge variant="secondary" className="ml-2">
                    {example.turns.length} turns
                  </Badge>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-3">
                    {example.turns.map((turn, turnIndex) => (
                      <TurnBlock key={turnIndex} turn={turn} />
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      ) : null}

      {conversation.length ? (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-muted-foreground">
            Conversation ({conversation.length} turns)
          </h4>

          {targetMessage ? (
            <MessageBlock message={targetMessage} index={targetIndex} highlighted />
          ) : null}

          {window.window.length ? (
            <div className="space-y-2">
              {window.beforeOmitted > 0 ? (
                <p className="text-xs text-muted-foreground">
                  … {window.beforeOmitted} earlier messages omitted …
                </p>
              ) : null}
              {window.window
                .filter(({ index }) => index !== targetIndex)
                .map(({ index, message }) => (
                  <MessageBlock key={index} message={message} index={index} />
                ))}
              {window.afterOmitted > 0 ? (
                <p className="text-xs text-muted-foreground">
                  … {window.afterOmitted} later messages omitted …
                </p>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : null}

      {answer ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Expected answer</h4>
          {prepend ? (
            <p className="mt-1 text-xs text-muted-foreground">
              Must prepend <span className="font-mono">{prepend}</span>
            </p>
          ) : null}
          <MarkdownMath className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {previewText(answer, 1200)}
          </MarkdownMath>
        </div>
      ) : null}

      <Accordion type="single" collapsible>
        <AccordionItem value="raw-prompt">
          <AccordionTrigger className="text-sm">Full prompt (raw JSON)</AccordionTrigger>
          <AccordionContent>
            <pre className="code-block mt-1 whitespace-pre-wrap text-sm">
              {typeof row.prompt === "string" ? row.prompt : JSON.stringify(row.prompt, null, 2)}
            </pre>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
