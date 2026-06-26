export type ChatMLSection = {
  role: string;
  content: string;
};

const CHATML_SECTION_RE = /<\|im_start\|>(\w+)\n([\s\S]*?)<\|im_end\|>/g;

/** Split a ChatML-formatted prompt into role/content sections. */
export function parseChatML(text: string): ChatMLSection[] {
  const sections: ChatMLSection[] = [];
  for (const match of text.matchAll(CHATML_SECTION_RE)) {
    const role = match[1];
    const content = match[2];
    if (role && content !== undefined) {
      sections.push({ role, content });
    }
  }
  return sections;
}

/** Collapse long runs of identical lines for readable long-context previews. */
export function collapseRepeatedLines(text: string, minRun = 3): string {
  const lines = text.split("\n");
  const result: string[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    let runLength = 1;
    while (index + runLength < lines.length && lines[index + runLength] === line) {
      runLength += 1;
    }

    if (runLength >= minRun && line.trim()) {
      result.push(line);
      result.push(`… (${runLength - 1} identical lines omitted)`);
    } else {
      for (let offset = 0; offset < runLength; offset += 1) {
        result.push(lines[index + offset]);
      }
    }
    index += runLength;
  }

  return result.join("\n");
}
