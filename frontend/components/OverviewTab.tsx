import type { DataTable, Metric, OverviewPayload } from "@/lib/types";
import { DatasetReadme } from "./DatasetReadme";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type OverviewTabProps = {
  overview: OverviewPayload;
  readme?: string;
};

function Metrics({ metrics }: { metrics: Metric[] }) {
  return (
    <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
      {metrics.map((metric) => (
        <Card key={metric.label} className="gap-1 py-3 shadow-none">
          <CardContent className="px-4 py-0">
            <p className="text-xs font-medium text-muted-foreground">{metric.label}</p>
            <p className="mt-0.5 text-lg font-semibold tracking-tight tabular-nums">{metric.value}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function DataTableView({ table }: { table: DataTable }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{table.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              {table.columns.map((column) => (
                <TableHead key={column}>{column}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {table.rows.map((row, index) => (
              <TableRow key={index}>
                {table.columns.map((column) => (
                  <TableCell key={column} className="max-w-md truncate">
                    {String(row[column] ?? "")}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

export function OverviewTab({ overview, readme = "" }: OverviewTabProps) {
  return (
    <div className="space-y-6">
      <Metrics metrics={overview.metrics} />
      {overview.tables.map((table) => (
        <DataTableView key={table.title} table={table} />
      ))}
      <DatasetReadme readme={readme} />
    </div>
  );
}
