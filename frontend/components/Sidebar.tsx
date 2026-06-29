"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { ChevronDown, Home, Search } from "lucide-react";
import type { Catalog, CategoryGroup, DatasetSummary } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SidebarFaq } from "@/components/SidebarFaq";

type SidebarProps = {
  catalog: Catalog;
};

type FilteredCategory = CategoryGroup & {
  datasets: DatasetSummary[];
};

function matchesQuery(dataset: DatasetSummary, query: string): boolean {
  const haystack = `${dataset.label} ${dataset.id} ${dataset.archetype ?? ""}`.toLowerCase();
  return haystack.includes(query);
}

function filterCatalog(catalog: Catalog, query: string): FilteredCategory[] {
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    return catalog.categories;
  }

  return catalog.categories
    .map((category) => ({
      ...category,
      datasets: category.datasets.filter((dataset) => matchesQuery(dataset, normalized)),
    }))
    .filter((category) => category.datasets.length > 0);
}

function CategorySection({
  category,
  pathname,
  forceOpen,
}: {
  category: FilteredCategory;
  pathname: string;
  forceOpen: boolean;
}) {
  const hasActiveDataset = category.datasets.some((dataset) =>
    pathname.startsWith(`/dataset/${dataset.id}`),
  );
  const [open, setOpen] = useState(hasActiveDataset);

  useEffect(() => {
    if (hasActiveDataset) {
      setOpen(true);
    }
  }, [hasActiveDataset]);

  const isOpen = forceOpen || open;

  return (
    <div className="mt-3">
      <button
        type="button"
        aria-expanded={isOpen}
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center gap-2 rounded-md px-3 py-1.5 text-left text-[11px] font-semibold uppercase tracking-wider text-sidebar-foreground/55 transition-colors hover:bg-sidebar-accent/40 hover:text-sidebar-foreground/80"
      >
        <ChevronDown
          className={cn(
            "size-3.5 shrink-0 transition-transform",
            isOpen ? "rotate-0" : "-rotate-90",
          )}
        />
        <span className="flex-1 truncate">{category.label}</span>
        <span className="rounded-full bg-sidebar-accent px-1.5 py-0.5 text-[10px] font-medium normal-case tracking-normal text-sidebar-foreground/70">
          {category.datasets.length}
        </span>
      </button>

      {isOpen ? (
        <div className="mt-1 space-y-0.5 pl-2">
          {category.datasets.map((dataset) => {
            const href = `/dataset/${dataset.id}/`;
            const active = pathname.startsWith(`/dataset/${dataset.id}`);
            return (
              <Link
                key={dataset.id}
                href={href}
                className={cn(
                  "block rounded-lg px-3 py-1.5 text-sm transition-colors",
                  active
                    ? "bg-sidebar-primary text-sidebar-primary-foreground"
                    : "text-sidebar-foreground/80 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground",
                )}
              >
                <span className="mr-2">{dataset.icon ?? "📊"}</span>
                <span className="leading-snug">{dataset.label}</span>
              </Link>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}

export function Sidebar({ catalog }: SidebarProps) {
  const pathname = usePathname();
  const [query, setQuery] = useState("");
  const totalDatasets = useMemo(
    () => catalog.categories.reduce((count, category) => count + category.datasets.length, 0),
    [catalog],
  );
  const filteredCategories = useMemo(() => filterCatalog(catalog, query), [catalog, query]);
  const isSearching = query.trim().length > 0;

  return (
    <aside className="flex h-screen w-72 shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground">
      <div className="border-b border-sidebar-border px-5 py-4">
        <p className="text-xs font-medium uppercase tracking-wider text-sidebar-foreground/60">
          Hugging Face
        </p>
        <h1 className="mt-1 text-lg font-semibold tracking-tight">Dataset Visualizer</h1>
        <p className="mt-1 text-xs text-sidebar-foreground/50">
          {totalDatasets} datasets · {catalog.categories.length} categories
        </p>
      </div>

      <div className="border-b border-sidebar-border px-3 py-3">
        <div className="relative">
          <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-sidebar-foreground/40" />
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search datasets…"
            className="border-sidebar-border bg-sidebar-accent/30 pl-8 text-sidebar-foreground placeholder:text-sidebar-foreground/40"
          />
        </div>
      </div>

      <ScrollArea className="min-h-0 flex-1 px-2 py-3">
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

        {filteredCategories.length === 0 ? (
          <p className="px-3 py-6 text-sm text-sidebar-foreground/50">No datasets match your search.</p>
        ) : (
          filteredCategories.map((category) => (
            <CategorySection
              key={category.key}
              category={category}
              pathname={pathname}
              forceOpen={isSearching}
            />
          ))
        )}
      </ScrollArea>

      <SidebarFaq />

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
