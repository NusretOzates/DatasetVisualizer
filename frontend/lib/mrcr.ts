export type ChatMessage = {
  role: string;
  content: string;
};

export type MrcrTurn = {
  speaker: "user" | "assistant";
  content: string;
};

export type MrcrExample = {
  turns: MrcrTurn[];
};

const USER_ASSISTANT_TURN_RE = /\n(?=User:|Assistant:)/;

/** Parse the MRCR `prompt` field into chat messages. */
export function parseMrcrMessages(prompt: unknown): ChatMessage[] {
  if (Array.isArray(prompt)) {
    return prompt.filter(
      (message): message is ChatMessage =>
        Boolean(message) &&
        typeof message === "object" &&
        typeof (message as ChatMessage).role === "string" &&
        typeof (message as ChatMessage).content === "string",
    );
  }
  if (typeof prompt !== "string" || !prompt.trim()) {
    return [];
  }
  try {
    const parsed: unknown = JSON.parse(prompt);
    return parseMrcrMessages(parsed);
  } catch {
    return [];
  }
}

/** Split an MRCR few-shot block into User/Assistant turns. */
export function parseUserAssistantTurns(text: string): MrcrTurn[] {
  return text
    .split(USER_ASSISTANT_TURN_RE)
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => {
      if (part.startsWith("User:")) {
        return { speaker: "user" as const, content: part.slice("User:".length).trim() };
      }
      if (part.startsWith("Assistant:")) {
        return {
          speaker: "assistant" as const,
          content: part.slice("Assistant:".length).trim(),
        };
      }
      return { speaker: "user" as const, content: part };
    });
}

/** Parse few-shot examples embedded in the first MRCR prompt message. */
export function parseMrcrExamples(introContent: string): { header: string; examples: MrcrExample[] } {
  const marker = "======EXAMPLE======";
  const endMarker = "======END EXAMPLE======";
  const headerEnd = introContent.indexOf(marker);
  const header = headerEnd >= 0 ? introContent.slice(0, headerEnd).trim() : introContent.trim();

  const examples = introContent
    .split(marker)
    .slice(1)
    .map((block) => block.split(endMarker)[0].trim())
    .filter(Boolean)
    .map((block) => ({ turns: parseUserAssistantTurns(block) }));

  return { header, examples };
}

/** Return a small window of messages around a target index for long threads. */
export function conversationWindow(
  messages: ChatMessage[],
  centerIndex: number,
  radius = 3,
): { beforeOmitted: number; window: Array<{ index: number; message: ChatMessage }>; afterOmitted: number } {
  const start = Math.max(0, centerIndex - radius);
  const end = Math.min(messages.length - 1, centerIndex + radius);
  return {
    beforeOmitted: start,
    afterOmitted: messages.length - end - 1,
    window: messages.slice(start, end + 1).map((message, offset) => ({
      index: start + offset,
      message,
    })),
  };
}

export function previewText(text: string, maxLength = 500): string {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}…`;
}
