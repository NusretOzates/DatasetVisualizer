export type Metric = { label: string; value: string };

export type ChartSpec =
  | {
      type: "bar";
      title: string;
      x_label?: string;
      y_label?: string;
      categories: string[];
      values: number[];
    }
  | {
      type: "pie";
      title: string;
      labels: string[];
      values: number[];
    }
  | {
      type: "histogram";
      title: string;
      x_label?: string;
      values: number[];
    }
  | {
      type: "stacked_bar";
      title: string;
      x_label?: string;
      y_label?: string;
      categories: string[];
      series: { name: string; values: number[] }[];
    }
  | {
      type: "timeline";
      title: string;
      values: string[];
    }
  | {
      type: "scatter";
      title: string;
      x_label?: string;
      y_label?: string;
      color_label?: string | null;
      points: { x: number | string | null; y: number | string | null; color?: number | string | null }[];
    };

export type DataTable = {
  title: string;
  columns: string[];
  rows: Record<string, unknown>[];
};

export type OverviewPayload = {
  metrics: Metric[];
  charts: ChartSpec[];
  tables: DataTable[];
};

export type DatasetSummary = {
  id: string;
  label: string;
  icon?: string | null;
  archetype?: string | null;
  description: string;
  hf_source: string;
  row_count: string;
};

export type CategoryGroup = {
  key: string;
  label: string;
  datasets: DatasetSummary[];
};

export type Catalog = {
  categories: CategoryGroup[];
  home_rows: {
    category: string;
    dataset: string;
    hf_source: string;
    archetype: string;
    rows: string;
  }[];
};

export type SelectControlSpec = {
  name: string;
  label: string;
  type: "select";
  options: string[];
  labels?: Record<string, string>;
  default: string;
};

export type FilterControlSpec =
  | {
      name: string;
      label: string;
      type: "multiselect";
      column?: string;
    }
  | {
      name: string;
      label: string;
      type: "text";
      column?: string;
    }
  | {
      name: string;
      label: string;
      type: "radio";
      options: string[];
      default?: string;
      column?: string;
    }
  | {
      name: string;
      label: string;
      type: "date_range";
      column?: string;
    };

export type DatasetMeta = {
  id: string;
  label: string;
  description: string;
  archetype?: string | null;
  viewer?: string | null;
  supports_private_tests?: boolean;
  icon?: string | null;
  id_column: string;
  controls: SelectControlSpec[];
  filters: FilterControlSpec[];
};

export type SamplePayload = {
  total: number;
  index: number;
  row: Record<string, unknown> | null;
  extras: Record<string, unknown>;
};
