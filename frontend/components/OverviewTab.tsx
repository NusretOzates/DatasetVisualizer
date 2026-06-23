import type { DataTable, Metric, OverviewPayload } from "@/lib/types";
import { ChartPanel } from "./ChartPanel";
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
};

function Metrics({ metrics }: { metrics: Metric[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {metrics.map((metric) => (
        <Card key={metric.label}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {metric.label}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold tracking-tight tabular-nums">{metric.value}</p>
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

export function OverviewTab({ overview }: OverviewTabProps) {
  return (
    <div className="space-y-6">
      <Metrics metrics={overview.metrics} />
      <div className="grid gap-6 xl:grid-cols-2">
        {overview.charts.map((chart, index) => (
          <ChartPanel key={`${chart.title}-${index}`} chart={chart} />
        ))}
      </div>
      {overview.tables.map((table) => (
        <DataTableView key={table.title} table={table} />
      ))}
    </div>
  );
}
