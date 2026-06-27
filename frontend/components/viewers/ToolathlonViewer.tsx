import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { MarkdownContent } from "@/components/MarkdownContent";
import type { SampleViewerProps } from "./types";

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item)).filter(Boolean);
}

export function ToolathlonViewer({ row }: SampleViewerProps) {
  const instruction = row.instruction ?? row.question;
  const mcpServers = asStringList(row.needed_mcp_servers);
  const localTools = asStringList(row.needed_local_tools);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge>{String(row.task_name ?? row.task_id ?? row.sample_id ?? "—")}</Badge>
        {row.task_pool ? <Badge variant="outline">{String(row.task_pool)}</Badge> : null}
        {row.mcp_server_count != null ? (
          <Badge variant="secondary">{String(row.mcp_server_count)} MCP servers</Badge>
        ) : null}
        {row.local_tool_count != null ? (
          <Badge variant="outline">{String(row.local_tool_count)} local tools</Badge>
        ) : null}
      </div>

      {instruction ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Task</h4>
          <div className="mt-2 rounded-lg border bg-muted/20 px-4 py-3 text-sm leading-relaxed">
            <MarkdownContent>{String(instruction)}</MarkdownContent>
          </div>
        </div>
      ) : null}

      {mcpServers.length ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">MCP servers</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {mcpServers.map((server) => (
              <Badge key={server} variant="outline" className="font-mono text-xs">
                {server}
              </Badge>
            ))}
          </div>
        </div>
      ) : null}

      {localTools.length ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="local-tools">
            <AccordionTrigger className="text-sm">Local tools</AccordionTrigger>
            <AccordionContent>
              <div className="flex flex-wrap gap-2">
                {localTools.map((tool) => (
                  <Badge key={tool} variant="secondary" className="font-mono text-xs">
                    {tool}
                  </Badge>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
