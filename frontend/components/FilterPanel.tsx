"use client";

import type { ControlSpec } from "@/lib/types";

type ControlPanelProps = {
  controls: ControlSpec[];
  values: Record<string, unknown>;
  onChange: (name: string, value: unknown) => void;
};

export function ControlPanel({ controls, values, onChange }: ControlPanelProps) {
  if (!controls.length) return null;

  return (
    <div className="panel">
      <h3>Dataset controls</h3>
      <div className="filters-grid">
        {controls.map((control) => {
          if (control.type !== "select") return null;
          const labels = "labels" in control ? control.labels : undefined;
          return (
            <div className="field" key={control.name}>
              <label htmlFor={control.name}>{control.label}</label>
              <select
                id={control.name}
                value={String(values[control.name] ?? control.default)}
                onChange={(event) => onChange(control.name, event.target.value)}
              >
                {control.options.map((option) => (
                  <option key={option} value={option}>
                    {labels?.[option] ?? option}
                  </option>
                ))}
              </select>
            </div>
          );
        })}
      </div>
    </div>
  );
}

type FilterPanelProps = {
  filters: ControlSpec[];
  options: Record<string, unknown>;
  values: Record<string, unknown>;
  onChange: (name: string, value: unknown) => void;
};

export function FilterPanel({ filters, options, values, onChange }: FilterPanelProps) {
  if (!filters.length) return null;

  return (
    <div className="panel">
      <h3>Filters</h3>
      <div className="filters-grid">
        {filters.map((filter) => {
          if (filter.type === "multiselect") {
            const available = Array.isArray(options[filter.name])
              ? (options[filter.name] as unknown[]).map(String)
              : [];
            const selected = Array.isArray(values[filter.name])
              ? (values[filter.name] as string[])
              : available;
            return (
              <div className="field" key={filter.name}>
                <label>{filter.label}</label>
                <select
                  multiple
                  value={selected}
                  onChange={(event) =>
                    onChange(
                      filter.name,
                      Array.from(event.target.selectedOptions).map((option) => option.value),
                    )
                  }
                  size={Math.min(8, Math.max(3, available.length))}
                >
                  {available.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
            );
          }
          if (filter.type === "text") {
            return (
              <div className="field" key={filter.name}>
                <label>{filter.label}</label>
                <input
                  value={String(values[filter.name] ?? "")}
                  onChange={(event) => onChange(filter.name, event.target.value)}
                />
              </div>
            );
          }
          if (filter.type === "radio") {
            const radioOptions = filter.options ?? [];
            return (
              <div className="field" key={filter.name}>
                <label>{filter.label}</label>
                <div>
                  {radioOptions.map((option) => (
                    <label key={option} style={{ display: "block" }}>
                      <input
                        type="radio"
                        name={filter.name}
                        checked={String(values[filter.name] ?? filter.default ?? "All") === option}
                        onChange={() => onChange(filter.name, option)}
                      />{" "}
                      {option}
                    </label>
                  ))}
                </div>
              </div>
            );
          }
          if (filter.type === "date_range") {
            const range = (options[filter.name] as { min?: string; max?: string }) ?? {};
            const current = (values[filter.name] as { start?: string; end?: string }) ?? {
              start: range.min,
              end: range.max,
            };
            return (
              <div className="field" key={filter.name}>
                <label>{filter.label}</label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
                  <input
                    type="date"
                    value={current.start ?? ""}
                    min={range.min}
                    max={range.max}
                    onChange={(event) =>
                      onChange(filter.name, { ...current, start: event.target.value })
                    }
                  />
                  <input
                    type="date"
                    value={current.end ?? ""}
                    min={range.min}
                    max={range.max}
                    onChange={(event) =>
                      onChange(filter.name, { ...current, end: event.target.value })
                    }
                  />
                </div>
              </div>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
}
