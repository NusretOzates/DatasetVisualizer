"use client";

import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";

type MarkdownMathProps = {
  children: string;
  className?: string;
  inline?: boolean;
};

export function MarkdownMath({ children, className, inline = false }: MarkdownMathProps) {
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
          ul: ({ children }) => <ul className="mb-3 list-disc pl-5">{children}</ul>,
          ol: ({ children }) => <ol className="mb-3 list-decimal pl-5">{children}</ol>,
          code: ({ children }) => (
            <code className="rounded bg-muted px-1 py-0.5 font-mono text-sm">{children}</code>
          ),
          pre: ({ children }) => <pre className="code-block mb-3">{children}</pre>,
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
