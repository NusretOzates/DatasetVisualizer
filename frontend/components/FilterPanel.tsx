"use client";

import type { FilterControlSpec, FilterOptions, SelectControlSpec } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type ControlPanelProps = {
  controls: SelectControlSpec[];
  values: Record<string, unknown>;
  onChange: (name: string, value: unknown) => void;
};

export function ControlPanel({ controls, values, onChange }: ControlPanelProps) {
  if (!controls.length) return null;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Dataset controls</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {controls.map((control) => (
          <div className="space-y-2" key={control.name}>
            <Label htmlFor={control.name}>{control.label}</Label>
            <Select
              value={String(values[control.name] ?? control.default)}
              onValueChange={(value) => onChange(control.name, value)}
            >
              <SelectTrigger id={control.name} className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {control.options.map((option) => (
                  <SelectItem key={option} value={option}>
                    {control.labels?.[option] ?? option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

type FilterPanelProps = {
  filters: FilterControlSpec[];
  options: FilterOptions;
  values: Record<string, unknown>;
  onChange: (name: string, value: unknown) => void;
};

function MultiSelectFilter({
  label,
  available,
  selected,
  onChange,
}: {
  label: string;
  available: string[];
  selected: string[];
  onChange: (values: string[]) => void;
}) {
  function toggle(option: string) {
    if (selected.includes(option)) {
      onChange(selected.filter((value) => value !== option));
    } else {
      onChange([...selected, option]);
    }
  }

  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <ScrollArea className="h-40 rounded-md border p-3">
        <div className="space-y-2">
          {available.map((option) => (
            <label key={option} className="flex cursor-pointer items-center gap-2 text-sm">
              <Checkbox
                checked={selected.includes(option)}
                onCheckedChange={() => toggle(option)}
              />
              <span className="truncate">{option}</span>
            </label>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

export function FilterPanel({ filters, options, values, onChange }: FilterPanelProps) {
  if (!filters.length) return null;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Filters</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filters.map((filter) => {
          if (filter.type === "multiselect") {
            const available = Array.isArray(options[filter.name])
              ? (options[filter.name] as unknown[]).map(String)
              : [];
            const selected = Array.isArray(values[filter.name])
              ? (values[filter.name] as string[])
              : available;
            return (
              <MultiSelectFilter
                key={filter.name}
                label={filter.label}
                available={available}
                selected={selected}
                onChange={(next) => onChange(filter.name, next)}
              />
            );
          }
          if (filter.type === "text") {
            return (
              <div className="space-y-2" key={filter.name}>
                <Label htmlFor={filter.name}>{filter.label}</Label>
                <Input
                  id={filter.name}
                  value={String(values[filter.name] ?? "")}
                  onChange={(event) => onChange(filter.name, event.target.value)}
                />
              </div>
            );
          }
          if (filter.type === "radio") {
            const radioOptions = filter.options ?? [];
            return (
              <div className="space-y-2" key={filter.name}>
                <Label>{filter.label}</Label>
                <RadioGroup
                  value={String(values[filter.name] ?? filter.default ?? "All")}
                  onValueChange={(value) => onChange(filter.name, value)}
                  className="space-y-2"
                >
                  {radioOptions.map((option) => (
                    <div key={option} className="flex items-center gap-2">
                      <RadioGroupItem value={option} id={`${filter.name}-${option}`} />
                      <Label htmlFor={`${filter.name}-${option}`} className="font-normal">
                        {option}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
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
              <div className="space-y-2" key={filter.name}>
                <Label>{filter.label}</Label>
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    type="date"
                    value={current.start ?? ""}
                    min={range.min}
                    max={range.max}
                    onChange={(event) =>
                      onChange(filter.name, { ...current, start: event.target.value })
                    }
                  />
                  <Input
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
      </CardContent>
    </Card>
  );
}
