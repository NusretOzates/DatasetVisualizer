import type { DataTable, Metric, OverviewPayload } from "@/lib/types";
import { ChartPanel } from "./ChartPanel";

type OverviewTabProps = {
  overview: OverviewPayload;
};

function Metrics({ metrics }: { metrics: Metric[] }) {
  return (
    <div className="metrics">
      {metrics.map((metric) => (
        <div className="metric-card" key={metric.label}>
          <span>{metric.label}</span>
          <strong>{metric.value}</strong>
        </div>
      ))}
    </div>
  );
}

function DataTableView({ table }: { table: DataTable }) {
  return (
    <div className="panel">
      <h3>{table.title}</h3>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              {table.columns.map((column) => (
                <th key={column}>{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row, index) => (
              <tr key={index}>
                {table.columns.map((column) => (
                  <td key={column}>{String(row[column] ?? "")}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function OverviewTab({ overview }: OverviewTabProps) {
  return (
    <div>
      <Metrics metrics={overview.metrics} />
      {overview.charts.map((chart, index) => (
        <ChartPanel key={`${chart.title}-${index}`} chart={chart} />
      ))}
      {overview.tables.map((table) => (
        <DataTableView key={table.title} table={table} />
      ))}
    </div>
  );
}
