"use client";

import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import { cn } from "@/lib/utils";

type MarkdownContentProps = {
  children: string;
  className?: string;
};

const components: Components = {
  h1: ({ children }) => (
    <h1 className="mb-4 text-2xl font-semibold tracking-tight">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="mb-3 mt-8 text-xl font-semibold tracking-tight first:mt-0">{children}</h2>
  ),
  h3: ({ children }) => <h3 className="mb-2 mt-6 text-lg font-semibold">{children}</h3>,
  p: ({ children }) => <p className="mb-3 leading-relaxed last:mb-0">{children}</p>,
  ul: ({ children }) => <ul className="mb-3 list-disc space-y-1 pl-5">{children}</ul>,
  ol: ({ children }) => <ol className="mb-3 list-decimal space-y-1 pl-5">{children}</ol>,
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  a: ({ href, children }) => (
    <a
      href={href}
      className="font-medium text-primary underline underline-offset-4"
      target="_blank"
      rel="noreferrer"
    >
      {children}
    </a>
  ),
  blockquote: ({ children }) => (
    <blockquote className="mb-3 border-l-4 border-border pl-4 text-muted-foreground">
      {children}
    </blockquote>
  ),
  code: ({ children, className }) =>
    className ? (
      <code className="font-mono text-inherit">{children}</code>
    ) : (
      <code className="rounded bg-muted px-1 py-0.5 font-mono text-sm">{children}</code>
    ),
  pre: ({ children }) => (
    <pre className="mb-3 overflow-x-auto rounded-lg border border-border bg-muted/50 p-4 font-mono text-[0.8125rem] leading-relaxed text-foreground [&_code]:bg-transparent [&_code]:p-0">
      {children}
    </pre>
  ),
  table: ({ children }) => (
    <div className="mb-4 overflow-x-auto">
      <table className="w-full border-collapse text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-muted/50">{children}</thead>,
  th: ({ children }) => (
    <th className="border border-border px-3 py-2 text-left font-medium">{children}</th>
  ),
  td: ({ children }) => <td className="border border-border px-3 py-2 align-top">{children}</td>,
  img: ({ src, alt }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={src} alt={alt ?? ""} className="my-4 max-h-96 max-w-full rounded-lg border object-contain" />
  ),
  hr: () => <hr className="my-6 border-border" />,
};

export function MarkdownContent({ children, className }: MarkdownContentProps) {
  return (
    <div className={cn("markdown-content text-sm", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        skipHtml
        components={components}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
