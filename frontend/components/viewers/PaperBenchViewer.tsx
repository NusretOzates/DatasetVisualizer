import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { ExternalLink } from "lucide-react";
import type { SampleViewerProps } from "./types";

function parseList(value: unknown): string[] {
  if (value == null) return [];
  if (Array.isArray(value)) {
    return value.map(String).map((item) => item.trim()).filter(Boolean);
  }
  const text = String(value).trim();
  if (!text) return [];
  return text.split(", ").map((item) => item.trim()).filter(Boolean);
}

function LinkList({ items, label }: { items: string[]; label: string }) {
  if (!items.length) return null;

  return (
    <div>
      <h4 className="text-sm font-medium text-muted-foreground">{label}</h4>
      <ul className="mt-2 space-y-2 text-sm">
        {items.map((item) => (
          <li key={item}>
            {item.startsWith("http://") || item.startsWith("https://") || item.startsWith("hf://") ? (
              <a
                href={item.startsWith("hf://") ? undefined : item}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 break-all text-primary underline-offset-4 hover:underline"
              >
                <ExternalLink className="size-3.5 shrink-0" aria-hidden="true" />
                <span>{item}</span>
              </a>
            ) : (
              <span className="break-all font-mono text-xs">{item}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function PaperBenchViewer({ row }: SampleViewerProps) {
  const rubricMetrics = [
    { key: "rubric_total_nodes", label: "Total nodes" },
    { key: "rubric_leaf_nodes", label: "Leaf nodes" },
    { key: "rubric_code_development", label: "Code development" },
    { key: "rubric_code_execution", label: "Code execution" },
    { key: "rubric_result_analysis", label: "Result analysis" },
  ] as const;

  const referenceFiles = parseList(row.reference_files);
  const referenceUrls = parseList(row.reference_file_urls);
  const referenceHfUris = parseList(row.reference_file_hf_uris);
  const blacklistedSites = parseList(row.blacklisted_sites);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge>{String(row.id ?? row.sample_id ?? "—")}</Badge>
        {row.split ? <Badge variant="outline">{String(row.split)}</Badge> : null}
      </div>

      {row.title ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Title</h4>
          <p className="mt-2 text-sm font-medium leading-relaxed">{String(row.title)}</p>
        </div>
      ) : null}

      {rubricMetrics.some(({ key }) => row[key] != null) ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Rubric metrics</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {rubricMetrics.map(({ key, label }) =>
              row[key] != null ? (
                <Badge key={key} variant="secondary">
                  {label}: {String(row[key])}
                </Badge>
              ) : null,
            )}
          </div>
        </div>
      ) : null}

      {row.rubric_requirements ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Rubric requirements</h4>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {String(row.rubric_requirements)}
          </p>
        </div>
      ) : null}

      <LinkList items={referenceFiles} label="Reference files" />
      <LinkList items={referenceUrls} label="Reference file URLs" />

      {referenceHfUris.length ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="hf-uris">
            <AccordionTrigger>Hugging Face file URIs</AccordionTrigger>
            <AccordionContent>
              <ul className="space-y-2 text-sm">
                {referenceHfUris.map((uri) => (
                  <li key={uri} className="break-all font-mono text-xs">
                    {uri}
                  </li>
                ))}
              </ul>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}

      <LinkList items={blacklistedSites} label="Blacklisted sites" />
    </div>
  );
}
