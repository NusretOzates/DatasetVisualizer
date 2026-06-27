import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { MarkdownContent } from "@/components/MarkdownContent";
import type { SampleViewerProps } from "./types";

export function TerminalBenchViewer({ row }: SampleViewerProps) {
  const expertMinutes = row.expert_time_estimate_min;
  const juniorMinutes = row.junior_time_estimate_min;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge>{String(row.task_id ?? row.instance_id ?? "—")}</Badge>
        {row.category ? <Badge variant="outline">{String(row.category)}</Badge> : null}
        {row.difficulty ? <Badge variant="secondary">{String(row.difficulty)}</Badge> : null}
        {row.allow_internet ? <Badge variant="outline">Internet allowed</Badge> : null}
      </div>

      {row.task_name ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Task name</h4>
          <p className="mt-2 text-sm leading-relaxed">{String(row.task_name)}</p>
        </div>
      ) : null}

      {row.description ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Description</h4>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {String(row.description)}
          </p>
        </div>
      ) : null}

      {row.instruction ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Instruction</h4>
          <div className="mt-2 rounded-lg border bg-muted/20 px-4 py-3 text-sm leading-relaxed">
            <MarkdownContent>{String(row.instruction)}</MarkdownContent>
          </div>
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2">
        {row.author_name ? (
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Author</h4>
            <p className="mt-2 text-sm">{String(row.author_name)}</p>
          </div>
        ) : null}
        {row.docker_image ? (
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Docker image</h4>
            <p className="mt-2 break-all font-mono text-xs">{String(row.docker_image)}</p>
          </div>
        ) : null}
        {expertMinutes != null ? (
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Expert estimate</h4>
            <p className="mt-2 text-sm">{String(expertMinutes)} min</p>
          </div>
        ) : null}
        {juniorMinutes != null ? (
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Junior estimate</h4>
            <p className="mt-2 text-sm">{String(juniorMinutes)} min</p>
          </div>
        ) : null}
        {row.cpus != null ? (
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">CPUs</h4>
            <p className="mt-2 text-sm">{String(row.cpus)}</p>
          </div>
        ) : null}
        {row.memory_mb != null ? (
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Memory</h4>
            <p className="mt-2 text-sm">{String(row.memory_mb)} MB</p>
          </div>
        ) : null}
      </div>

      {row.task_readme ? (
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="readme">
            <AccordionTrigger>Task README</AccordionTrigger>
            <AccordionContent>
              <MarkdownContent>{String(row.task_readme)}</MarkdownContent>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
