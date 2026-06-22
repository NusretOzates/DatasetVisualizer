"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { Catalog } from "@/lib/types";

type SidebarProps = {
  catalog: Catalog;
};

export function Sidebar({ catalog }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <h1>Dataset Visualizer</h1>
      <Link
        href="/"
        className={`sidebar-link${pathname === "/" ? " active" : ""}`}
      >
        🏠 Home
      </Link>
      {catalog.categories.map((category) => (
        <div className="sidebar-section" key={category.key}>
          <h2>{category.label}</h2>
          {category.datasets.map((dataset) => {
            const href = `/dataset/${dataset.id}/`;
            const active = pathname.startsWith(`/dataset/${dataset.id}`);
            return (
              <Link
                key={dataset.id}
                href={href}
                className={`sidebar-link${active ? " active" : ""}`}
              >
                {dataset.icon ? `${dataset.icon} ` : ""}
                {dataset.label}
              </Link>
            );
          })}
        </div>
      ))}
    </aside>
  );
}
