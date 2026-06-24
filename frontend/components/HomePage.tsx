"use client";

import { AppShell } from "@/components/Sidebar";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useCatalog } from "@/lib/useCatalog";
import { AlertCircle, Database } from "lucide-react";
import { DatasetSourceLink } from "@/components/DatasetSourceLink";

export function HomePage() {
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

  const categoryCount = catalog.categories.length;

  return (
    <AppShell catalog={catalog}>
      <div className="space-y-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Database className="size-6 text-primary" />
            <h2 className="text-3xl font-semibold tracking-tight">Dataset Visualizer</h2>
          </div>
          <p className="max-w-3xl text-muted-foreground">
            Explore Hugging Face benchmark datasets with interactive overviews and per-sample
            inspection.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Registered datasets</CardTitle>
            <CardDescription>
              {catalog.home_rows.length} datasets across {categoryCount} benchmark categories.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Category</TableHead>
                  <TableHead>Dataset</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Archetype</TableHead>
                  <TableHead className="text-right">Rows</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {catalog.home_rows.map((row) => (
                  <TableRow key={`${row.category}-${row.dataset}`}>
                    <TableCell>
                      <Badge variant="secondary">{row.category}</Badge>
                    </TableCell>
                    <TableCell className="font-medium">{row.dataset}</TableCell>
                    <TableCell>
                      {row.source_link ? (
                        <DatasetSourceLink
                          source={row.source_link}
                          className="inline-flex items-center gap-1.5 text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
                        />
                      ) : (
                        <span className="font-mono text-xs text-muted-foreground">
                          {row.hf_source}
                        </span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{row.archetype}</Badge>
                    </TableCell>
                    <TableCell className="text-right tabular-nums">{row.rows}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
