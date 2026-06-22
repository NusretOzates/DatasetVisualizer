"use client";

import dynamic from "next/dynamic";
import type { ChartSpec } from "@/lib/types";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

type ChartPanelProps = {
  chart: ChartSpec;
};

export function ChartPanel({ chart }: ChartPanelProps) {
  if (chart.type === "bar") {
    return (
      <div className="panel">
        <Plot
          data={[
            {
              type: "bar",
              x: chart.categories,
              y: chart.values,
            },
          ]}
          layout={{
            title: chart.title,
            xaxis: { title: chart.x_label, tickangle: -45 },
            yaxis: { title: chart.y_label },
            margin: { t: 48, b: 100 },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
          }}
          style={{ width: "100%", height: "420px" }}
          config={{ displayModeBar: false }}
        />
      </div>
    );
  }

  if (chart.type === "pie") {
    return (
      <div className="panel">
        <Plot
          data={[
            {
              type: "pie",
              labels: chart.labels,
              values: chart.values,
            },
          ]}
          layout={{
            title: chart.title,
            paper_bgcolor: "transparent",
          }}
          style={{ width: "100%", height: "420px" }}
          config={{ displayModeBar: false }}
        />
      </div>
    );
  }

  if (chart.type === "histogram") {
    return (
      <div className="panel">
        <Plot
          data={[
            {
              type: "histogram",
              x: chart.values,
            },
          ]}
          layout={{
            title: chart.title,
            xaxis: { title: chart.x_label },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
          }}
          style={{ width: "100%", height: "420px" }}
          config={{ displayModeBar: false }}
        />
      </div>
    );
  }

  if (chart.type === "stacked_bar") {
    return (
      <div className="panel">
        <Plot
          data={chart.series.map((series) => ({
            type: "bar",
            name: series.name,
            x: chart.categories,
            y: series.values,
          }))}
          layout={{
            title: chart.title,
            barmode: "stack",
            xaxis: { title: chart.x_label },
            yaxis: { title: chart.y_label },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
          }}
          style={{ width: "100%", height: "420px" }}
          config={{ displayModeBar: false }}
        />
      </div>
    );
  }

  if (chart.type === "timeline") {
    return (
      <div className="panel">
        <Plot
          data={[
            {
              type: "histogram",
              x: chart.values,
            },
          ]}
          layout={{
            title: chart.title,
            xaxis: { title: "Date" },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
          }}
          style={{ width: "100%", height: "420px" }}
          config={{ displayModeBar: false }}
        />
      </div>
    );
  }

  if (chart.type === "scatter") {
    return (
      <div className="panel">
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
            title: chart.title,
            xaxis: { title: chart.x_label },
            yaxis: { title: chart.y_label },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
          }}
          style={{ width: "100%", height: "420px" }}
          config={{ displayModeBar: false }}
        />
      </div>
    );
  }

  return null;
}
