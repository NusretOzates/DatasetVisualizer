"use client";

import Link from "next/link";
import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import { AppShell } from "@/components/Sidebar";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { FAQ_ITEMS } from "@/lib/faq";
import { useCatalog } from "@/lib/useCatalog";
import { cn } from "@/lib/utils";
import { AlertCircle, HelpCircle } from "lucide-react";

const markdownComponents: Components = {
  p: ({ children }) => (
    <p className="mb-2 leading-relaxed text-muted-foreground last:mb-0">{children}</p>
  ),
  ul: ({ children }) => (
    <ul className="mb-2 list-disc space-y-1.5 pl-4 text-muted-foreground">{children}</ul>
  ),
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
  a: ({ href, children }) => {
    const className = "font-medium text-primary underline underline-offset-4 hover:text-primary/80";
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

export function FaqPage() {
  const { catalog, error } = useCatalog();

  if (!catalog) {
    return (
      <AppShell>
        {error ? (
          <Alert variant="destructive">
            <AlertCircle className="size-4" />
            <AlertTitle>Failed to load catalog</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : (
          <div className="space-y-4">
            <Skeleton className="h-10 w-64" />
            <Skeleton className="h-5 w-96" />
            <Skeleton className="h-80 w-full" />
          </div>
        )}
      </AppShell>
    );
  }

  return (
    <AppShell catalog={catalog}>
      <div className="space-y-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-muted-foreground">
            <HelpCircle className="size-5" />
            <p className="text-sm font-medium uppercase tracking-wider">Help</p>
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">Frequently Asked Question</h1>
          <p className="max-w-3xl text-muted-foreground">
            Common questions about benchmark families in this catalog — how they differ, when to use
            each, and how they relate to composite scores such as the Artificial Analysis Intelligence
            Index.
          </p>
        </div>

        <Accordion type="single" collapsible className="space-y-3">
          {FAQ_ITEMS.map((item) => (
            <AccordionItem
              key={item.id}
              value={item.id}
              className="overflow-hidden rounded-lg border border-border bg-card"
            >
              <AccordionTrigger
                className={cn(
                  "px-5 py-4 text-left text-base font-medium hover:no-underline",
                  "[&[data-state=open]]:border-b [&[data-state=open]]:border-border",
                )}
              >
                {item.question}
              </AccordionTrigger>
              <AccordionContent className="px-5 pb-5 pt-1 text-sm">
                <ReactMarkdown components={markdownComponents}>{item.answer}</ReactMarkdown>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </AppShell>
  );
}
