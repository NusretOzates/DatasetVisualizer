"use client";

import dynamic from "next/dynamic";
import type { ChartSpec } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

const plotLayout = {
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  font: { family: "Inter, system-ui, sans-serif", color: "#334155" },
  margin: { t: 20, r: 20, b: 60, l: 50 },
};

const PLOT_STYLE = { width: "100%", height: "360px" } as const;
const PLOT_CONFIG = { displayModeBar: false, responsive: true } as const;

type ChartPanelProps = {
  chart: ChartSpec;
};

export function ChartPanel({ chart }: ChartPanelProps) {
  let plot = null;

  if (chart.type === "bar") {
    plot = (
      <Plot
        data={[{ type: "bar", x: chart.categories, y: chart.values, marker: { color: "#4f46e5" } }]}
        layout={{
          ...plotLayout,
          xaxis: { title: chart.x_label, tickangle: -45 },
          yaxis: { title: chart.y_label },
        }}
        style={PLOT_STYLE}
        config={PLOT_CONFIG}
      />
    );
  } else if (chart.type === "pie") {
    plot = (
      <Plot
        data={[{ type: "pie", labels: chart.labels, values: chart.values, hole: 0.35 }]}
        layout={plotLayout}
        style={PLOT_STYLE}
        config={PLOT_CONFIG}
      />
    );
  } else if (chart.type === "histogram") {
    plot = (
      <Plot
        data={[{ type: "histogram", x: chart.values, marker: { color: "#0ea5e9" } }]}
        layout={{ ...plotLayout, xaxis: { title: chart.x_label } }}
        style={PLOT_STYLE}
        config={PLOT_CONFIG}
      />
    );
  } else if (chart.type === "stacked_bar") {
    plot = (
      <Plot
        data={chart.series.map((series) => ({
          type: "bar",
          name: series.name,
          x: chart.categories,
          y: series.values,
        }))}
        layout={{
          ...plotLayout,
          barmode: "stack",
          xaxis: { title: chart.x_label },
          yaxis: { title: chart.y_label },
        }}
        style={PLOT_STYLE}
        config={PLOT_CONFIG}
      />
    );
  } else if (chart.type === "timeline") {
    plot = (
      <Plot
        data={[{ type: "histogram", x: chart.values, marker: { color: "#8b5cf6" } }]}
        layout={{ ...plotLayout, xaxis: { title: "Date" } }}
        style={PLOT_STYLE}
        config={PLOT_CONFIG}
      />
    );
  } else if (chart.type === "scatter") {
    plot = (
      <Plot
        data={[
          {
            type: "scatter",
            mode: "markers",
            x: chart.points.map((point) => point.x),
            y: chart.points.map((point) => point.y),
            marker: {
              color: chart.points.map((point) => point.color ?? 0),
              colorscale: "RdYlGn",
              showscale: Boolean(chart.color_label),
            },
          },
        ]}
        layout={{
          ...plotLayout,
          xaxis: { title: chart.x_label },
          yaxis: { title: chart.y_label },
        }}
        style={PLOT_STYLE}
        config={PLOT_CONFIG}
      />
    );
  }

  if (!plot) return null;

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-2">
        <CardTitle className="text-base">{chart.title}</CardTitle>
      </CardHeader>
      <CardContent>{plot}</CardContent>
    </Card>
  );
}
