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
    <div>
      <h3>Question</h3>
      <p>{question}</p>
      {options.length === 0 ? (
        <p className="muted">No options available for this sample.</p>
      ) : (
        options.map((option) => (
          <div
            key={option.letter}
            className={`mcq-option${option.letter === correct ? " correct" : ""}`}
          >
            <strong>{option.letter}.</strong> {option.text}
          </div>
        ))
      )}
      {correct ? <p className="muted">Correct answer: {correct}</p> : null}
    </div>
  );
}
