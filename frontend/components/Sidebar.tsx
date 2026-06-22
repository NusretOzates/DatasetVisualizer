"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home } from "lucide-react";
import type { Catalog } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

type SidebarProps = {
  catalog: Catalog;
};

export function Sidebar({ catalog }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-72 shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground">
      <div className="border-b border-sidebar-border px-5 py-4">
        <p className="text-xs font-medium uppercase tracking-wider text-sidebar-foreground/60">
          Hugging Face
        </p>
        <h1 className="mt-1 text-lg font-semibold tracking-tight">Dataset Visualizer</h1>
      </div>

      <ScrollArea className="flex-1 px-3 py-4">
        <Link
          href="/"
          className={cn(
            "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
            pathname === "/"
              ? "bg-sidebar-accent text-sidebar-accent-foreground"
              : "text-sidebar-foreground/80 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground",
          )}
        >
          <Home className="size-4" />
          Home
        </Link>

        {catalog.categories.map((category) => (
          <div className="mt-5" key={category.key}>
            <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-sidebar-foreground/50">
              {category.label}
            </p>
            <div className="space-y-0.5">
              {category.datasets.map((dataset) => {
                const href = `/dataset/${dataset.id}/`;
                const active = pathname.startsWith(`/dataset/${dataset.id}`);
                return (
                  <Link
                    key={dataset.id}
                    href={href}
                    className={cn(
                      "block rounded-lg px-3 py-2 text-sm transition-colors",
                      active
                        ? "bg-sidebar-primary text-sidebar-primary-foreground"
                        : "text-sidebar-foreground/80 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground",
                    )}
                  >
                    <span className="mr-2">{dataset.icon ?? "📊"}</span>
                    {dataset.label}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </ScrollArea>

      <div className="border-t border-sidebar-border px-5 py-3">
        <p className="text-xs text-sidebar-foreground/50">Gradio Server + Next.js</p>
      </div>
    </aside>
  );
}

export function AppShell({
  catalog,
  children,
}: {
  catalog?: Catalog | null;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-background">
      {catalog ? (
        <Sidebar catalog={catalog} />
      ) : (
        <aside className="flex h-screen w-72 shrink-0 flex-col border-r border-sidebar-border bg-sidebar px-5 py-4">
          <h1 className="text-lg font-semibold text-sidebar-foreground">Dataset Visualizer</h1>
        </aside>
      )}
      <main className="min-w-0 flex-1 overflow-auto">
        <div className="mx-auto max-w-7xl px-6 py-8 md:px-10">{children}</div>
      </main>
    </div>
  );
}
