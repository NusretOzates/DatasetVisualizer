"use client";

import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";

type MarkdownMathProps = {
  children: string;
  className?: string;
  inline?: boolean;
  /** Wrap bare LaTeX commands (e.g. `\frac{1}{2}`) in math delimiters. */
  autoWrapLatex?: boolean;
};

/** HLE prompts often indent numbered statements, which markdown treats as code blocks. */
function unwrapIndentedBlocks(text: string): string {
  return text
    .split("\n")
    .map((line) => (line.match(/^[ \t]{4,}\S/) ? line.replace(/^[ \t]{4}/, "") : line))
    .join("\n");
}

function wrapBareLatex(text: string): string {
  const trimmed = text.trim();
  if (!trimmed || trimmed.includes("$")) {
    return trimmed;
  }
  if (/\\[a-zA-Z]/.test(trimmed)) {
    return `$${trimmed}$`;
  }
  return trimmed;
}

export function MarkdownMath({
  children,
  className,
  inline = false,
  autoWrapLatex = false,
}: MarkdownMathProps) {
  let markdown = unwrapIndentedBlocks(children);
  if (autoWrapLatex) {
    markdown = wrapBareLatex(markdown);
  }

  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
        skipHtml
        components={{
          p: ({ children }) =>
            inline ? (
              <span className="leading-relaxed">{children}</span>
            ) : (
              <p className="mb-3 leading-relaxed last:mb-0">{children}</p>
            ),
          ul: ({ children }) => <ul className="mb-3 list-disc space-y-1 pl-5">{children}</ul>,
          ol: ({ children }) => <ol className="mb-3 list-decimal space-y-1 pl-5">{children}</ol>,
          li: ({ children }) => <li className="leading-relaxed">{children}</li>,
          code: ({ children, className: codeClassName }) =>
            codeClassName ? (
              <code className="font-mono text-inherit">{children}</code>
            ) : (
              <code className="rounded bg-muted px-1 py-0.5 font-mono text-sm">{children}</code>
            ),
          pre: ({ children }) => (
            <pre className="mb-3 overflow-x-auto rounded-lg border border-border bg-muted/50 p-4 font-mono text-[0.8125rem] leading-relaxed text-foreground [&_code]:bg-transparent [&_code]:p-0">
              {children}
            </pre>
          ),
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}
