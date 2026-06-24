import type { SourceLink } from "@/lib/types";
import { ExternalLink } from "lucide-react";
import { GitHubIcon, HuggingFaceIcon } from "@/components/icons/BrandIcons";

type DatasetSourceLinkProps = {
  source: SourceLink;
  className?: string;
};

function sourceLabel(kind: SourceLink["kind"]) {
  if (kind === "huggingface") return "Hugging Face dataset";
  if (kind === "github") return "GitHub repository";
  return "Dataset source";
}

function SourceIcon({ kind }: { kind: SourceLink["kind"] }) {
  if (kind === "huggingface") {
    return <HuggingFaceIcon />;
  }
  if (kind === "github") {
    return <GitHubIcon />;
  }
  return <ExternalLink className="size-3.5 shrink-0" aria-hidden="true" />;
}

export function DatasetSourceLink({ source, className }: DatasetSourceLinkProps) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className={className}
      title={sourceLabel(source.kind)}
    >
      <SourceIcon kind={source.kind} />
      <span className="font-mono text-xs">{source.label}</span>
      <span className="sr-only"> (opens in a new tab)</span>
    </a>
  );
}
