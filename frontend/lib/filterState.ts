import type { DatasetMeta, FilterOptions } from "@/lib/types";

export type FilterValues = Record<string, unknown>;

export function defaultControlValues(meta: DatasetMeta): FilterValues {
  const values: FilterValues = {};
  for (const control of meta.controls) {
    values[control.name] = control.default;
  }
  return values;
}

export function defaultFilterValues(meta: DatasetMeta): FilterValues {
  const values: FilterValues = {};
  for (const filter of meta.filters) {
    if (filter.type === "radio") {
      values[filter.name] = filter.default ?? "All";
    }
    if (filter.type === "text") {
      values[filter.name] = "";
    }
  }
  return values;
}

export function buildInitialFilters(meta: DatasetMeta, options: FilterOptions): FilterValues {
  return reconcileFilters(meta, options, defaultFilterValues(meta));
}

/** Keep valid user selections when dataset controls change and filter options refresh. */
export function reconcileFilters(
  meta: DatasetMeta,
  options: FilterOptions,
  current: FilterValues,
): FilterValues {
  const next: FilterValues = { ...defaultFilterValues(meta) };

  for (const filter of meta.filters) {
    if (filter.type === "multiselect" && Array.isArray(options[filter.name])) {
      const available = (options[filter.name] as unknown[]).map(String);
      const previous = Array.isArray(current[filter.name])
        ? (current[filter.name] as unknown[]).map(String)
        : [];
      const kept = previous.filter((value) => available.includes(value));
      next[filter.name] = kept.length > 0 ? kept : available;
      continue;
    }

    if (filter.type === "radio") {
      const selected = current[filter.name];
      const optionsList = filter.options ?? [];
      if (typeof selected === "string" && optionsList.includes(selected)) {
        next[filter.name] = selected;
      }
      continue;
    }

    if (filter.type === "text" && typeof current[filter.name] === "string") {
      next[filter.name] = current[filter.name];
      continue;
    }

    if (filter.type === "date_range" && options[filter.name]) {
      const range = options[filter.name];
      const existing = current[filter.name];
      if (
        existing &&
        typeof existing === "object" &&
        "start" in existing &&
        "end" in existing
      ) {
        next[filter.name] = existing;
      } else if (range && typeof range === "object" && "min" in range) {
        next[filter.name] = { start: range.min, end: range.max };
      }
    }
  }

  return next;
}
