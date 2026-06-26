import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { MarkdownMath } from "./MarkdownMath";

type McqViewerProps = {
  row: Record<string, unknown>;
  questionCol?: string;
  choicesCol?: string;
  answerCol?: string;
  /** When true, skip the question heading (caller already rendered it). */
  hideQuestion?: boolean;
};

const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

function resolveCorrectLetter(row: Record<string, unknown>, answerCol: string): string {
  const answerLetter = row[answerCol];
  if (answerLetter != null && answerLetter !== "") {
    const asStr = String(answerLetter).toUpperCase().trim();
    if (asStr.length === 1 && LETTERS.includes(asStr)) {
      return asStr;
    }
    const idx = Number(asStr);
    if (!Number.isNaN(idx) && idx >= 0 && idx < LETTERS.length) {
      return LETTERS[idx];
    }
    return asStr;
  }
  const answerKey = row.answerKey;
  if (answerKey != null && answerKey !== "") {
    return String(answerKey).toUpperCase();
  }
  const answer = row.answer;
  if (answer != null && answer !== "") {
    const idx = Number(answer);
    if (!Number.isNaN(idx) && idx >= 0 && idx < LETTERS.length) {
      return LETTERS[idx];
    }
    return String(answer).toUpperCase();
  }
  const answerIndex = row.answer_index;
  if (answerIndex != null) {
    const idx = Number(answerIndex);
    if (!Number.isNaN(idx) && idx >= 0 && idx < LETTERS.length) {
      return LETTERS[idx];
    }
  }
  return "";
}

function sequenceValues(value: unknown): unknown[] | null {
  if (Array.isArray(value)) return value;
  if (value && typeof value === "object" && "length" in value && typeof value.length === "number") {
    return Array.from(value as ArrayLike<unknown>);
  }
  return null;
}

function parseQuotedTokens(fragment: string): string[] {
  const tokens: string[] = [];
  const pattern = /'([^']*)'/g;
  let match = pattern.exec(fragment);
  while (match) {
    const token = match[1].trim();
    if (token) tokens.push(token);
    match = pattern.exec(fragment);
  }
  return tokens;
}

function isLegacyNumpyArrayString(value: unknown): value is string {
  return typeof value === "string" && value.trim().startsWith("['");
}

function legacyChoiceTextsFromString(choices: string): string[] | null {
  if (choices.includes("'], ['")) {
    const tail = choices.split("'], ['").slice(1).join("'], ['");
    const parsed = parseQuotedTokens(tail);
    if (parsed.length > 0) return parsed;
  }
  if (choices.startsWith("['")) {
    const parsed = parseQuotedTokens(choices);
    if (parsed.length > 0) return parsed;
  }
  return null;
}

function coerceChoiceTexts(choices: unknown): string[] {
  if (choices == null || choices === "") return [];
  if (typeof choices === "string") {
    const legacy = legacyChoiceTextsFromString(choices);
    if (legacy) return legacy;
    if (choices.includes(", ")) {
      return choices.split(", ").map((part) => part.trim()).filter(Boolean);
    }
    return [choices];
  }
  const seq = sequenceValues(choices);
  if (seq) {
    const legacyParts = seq.filter(isLegacyNumpyArrayString);
    if (legacyParts.length >= 2) {
      return coerceChoiceTexts(legacyParts[legacyParts.length - 1]);
    }
    if (legacyParts.length === 1) {
      const legacy = legacyChoiceTextsFromString(legacyParts[0]);
      if (legacy) return legacy;
    }
    if (seq.every((item) => typeof item === "string" && !isLegacyNumpyArrayString(item))) {
      return seq.map((text) => String(text).trim()).filter(Boolean);
    }
    return seq.flatMap((item) => coerceChoiceTexts(item)).map((text) => text.trim()).filter(Boolean);
  }
  if (typeof choices === "object" && choices !== null) {
    const record = choices as Record<string, unknown>;
    const textSeq = sequenceValues(record.text);
    if (textSeq) {
      return textSeq.map((text) => String(text).trim()).filter(Boolean);
    }
    if (typeof record.text === "string") {
      const legacy = legacyChoiceTextsFromString(record.text);
      if (legacy) return legacy;
      if (record.text.includes(", ")) {
        return record.text.split(", ").map((part) => part.trim()).filter(Boolean);
      }
    }
  }
  const text = String(choices).trim();
  return text ? [text] : [];
}

function formatOptions(choices: unknown): { letter: string; text: string }[] {
  const options: { letter: string; text: string }[] = [];
  let letterIdx = 0;
  for (const text of coerceChoiceTexts(choices)) {
    if (!text || text.toUpperCase() === "N/A") continue;
    options.push({ letter: LETTERS[letterIdx], text });
    letterIdx += 1;
  }
  return options;
}

export function McqViewer({
  row,
  questionCol = "question",
  choicesCol = "choices",
  answerCol = "answer_letter",
  hideQuestion = false,
}: McqViewerProps) {
  const question = String(row[questionCol] ?? "");
  const correct = resolveCorrectLetter(row, answerCol);
  const options = formatOptions(row[choicesCol] ?? row.options);

  return (
    <div className="space-y-4">
      {!hideQuestion ? (
        <div>
          <h3 className="text-sm font-medium text-muted-foreground">Question</h3>
          <MarkdownMath className="mt-2 text-base">{question}</MarkdownMath>
        </div>
      ) : null}

      {options.length === 0 ? (
        <p className="text-sm text-muted-foreground">No options available for this sample.</p>
      ) : (
        <div className="space-y-2">
          {options.map((option) => (
            <div
              key={option.letter}
              className={cn(
                "rounded-lg border px-4 py-3 text-sm",
                option.letter === correct
                  ? "border-emerald-300 bg-emerald-50 text-emerald-900"
                  : "border-border bg-muted/30",
              )}
            >
              <span className="font-semibold">{option.letter}.</span>{" "}
              <MarkdownMath className="inline" inline>
                {option.text}
              </MarkdownMath>
            </div>
          ))}
        </div>
      )}

      {correct ? (
        <Badge variant="outline" className="border-emerald-300 text-emerald-700">
          Correct answer: {correct}
        </Badge>
      ) : null}
    </div>
  );
}
