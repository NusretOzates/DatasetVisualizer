"use client";

import Link from "next/link";
import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import { HelpCircle } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { SIDEBAR_FAQ } from "@/lib/faq";
import { cn } from "@/lib/utils";

const markdownComponents: Components = {
  p: ({ children }) => (
    <p className="mb-2 leading-relaxed text-sidebar-foreground/75 last:mb-0">{children}</p>
  ),
  ul: ({ children }) => (
    <ul className="mb-2 list-disc space-y-1.5 pl-4 text-sidebar-foreground/75">{children}</ul>
  ),
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  strong: ({ children }) => (
    <strong className="font-semibold text-sidebar-foreground/90">{children}</strong>
  ),
  a: ({ href, children }) => {
    const className =
      "font-medium text-sidebar-primary underline underline-offset-2 hover:text-sidebar-primary-foreground/90";
    if (href?.startsWith("/")) {
      return (
        <Link href={href} className={className}>
          {children}
        </Link>
      );
    }
    return (
      <a href={href} className={className} target="_blank" rel="noreferrer">
        {children}
      </a>
    );
  },
};

export function SidebarFaq() {
  return (
    <section className="border-t border-sidebar-border px-3 py-3" aria-label="FAQ">
      <div className="mb-2 flex items-center gap-2 px-1">
        <HelpCircle className="size-3.5 text-sidebar-foreground/50" />
        <h2 className="text-[11px] font-semibold uppercase tracking-wider text-sidebar-foreground/55">
          FAQ
        </h2>
      </div>

      <div className="max-h-72 overflow-y-auto pr-1">
        <Accordion type="single" collapsible className="space-y-2">
          {SIDEBAR_FAQ.map((item) => (
            <AccordionItem key={item.id} value={item.id} className="space-y-0 border-0">
              <AccordionTrigger
                className={cn(
                  "rounded-lg border border-sidebar-border bg-sidebar-accent/25 px-3 py-2.5 text-xs font-medium text-sidebar-foreground/90",
                  "hover:bg-sidebar-accent/45 hover:no-underline",
                  "[&[data-state=open]]:rounded-b-none [&[data-state=open]]:border-b-0",
                )}
              >
                <span className="pr-2 text-left leading-snug">{item.question}</span>
              </AccordionTrigger>
              <AccordionContent className="rounded-b-lg border border-t-0 border-sidebar-border bg-sidebar-accent/15 px-3 pb-3 text-xs">
                <ReactMarkdown components={markdownComponents}>{item.answer}</ReactMarkdown>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
}
