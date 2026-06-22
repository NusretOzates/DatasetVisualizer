"use client";

import { useEffect, useState } from "react";
import type { Catalog } from "@/lib/types";
import { fetchCatalog } from "@/lib/api";
import { Sidebar } from "@/components/Sidebar";

export function HomePage() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCatalog()
      .then(setCatalog)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (!catalog) {
    return (
      <div className="app-shell">
        <aside className="sidebar">
          <h1>Dataset Visualizer</h1>
        </aside>
        <main className="main">
          {error ? <div className="error">{error}</div> : <p className="muted">Loading catalog…</p>}
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar catalog={catalog} />
      <main className="main">
        <h2>Dataset Visualizer</h2>
        <p className="muted">
          Explore Hugging Face benchmark datasets with interactive overviews and per-sample
          inspection.
        </p>
        <div className="panel table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Dataset</th>
                <th>HF Source</th>
                <th>Archetype</th>
                <th>Rows</th>
              </tr>
            </thead>
            <tbody>
              {catalog.home_rows.map((row) => (
                <tr key={`${row.category}-${row.dataset}`}>
                  <td>{row.category}</td>
                  <td>{row.dataset}</td>
                  <td>{row.hf_source}</td>
                  <td>{row.archetype}</td>
                  <td>{row.rows}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
