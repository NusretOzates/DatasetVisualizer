import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type McqViewerProps = {
  row: Record<string, unknown>;
  questionCol?: string;
  choicesCol?: string;
  answerCol?: string;
};

const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

function resolveCorrectLetter(row: Record<string, unknown>, answerCol: string): string {
  const answerLetter = row[answerCol];
  if (answerLetter != null && answerLetter !== "") {
    return String(answerLetter).toUpperCase();
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

function formatOptions(choices: unknown): { letter: string; text: string }[] {
  if (!choices) return [];
  const list = Array.isArray(choices) ? choices : [choices];
  const options: { letter: string; text: string }[] = [];
  let letterIdx = 0;
  for (const item of list) {
    const text = String(item).trim();
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
}: McqViewerProps) {
  const question = String(row[questionCol] ?? "");
  const correct = resolveCorrectLetter(row, answerCol);
  const options = formatOptions(row[choicesCol] ?? row.options);

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-medium text-muted-foreground">Question</h3>
        <p className="mt-2 text-base leading-relaxed">{question}</p>
      </div>

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
              <span className="font-semibold">{option.letter}.</span> {option.text}
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
