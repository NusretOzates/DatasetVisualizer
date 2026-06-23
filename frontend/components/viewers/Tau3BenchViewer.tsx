import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import type { SampleViewerProps } from "./types";

export function Tau3BenchViewer({ row }: SampleViewerProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge>{String(row.instance_id ?? row.task_id ?? "—")}</Badge>
        <Badge variant="outline">{String(row.domain ?? "—")}</Badge>
        <Badge variant="outline">{String(row.task_split ?? "base")}</Badge>
        {row.evaluation_action_count ? (
          <Badge variant="secondary">
            {String(row.evaluation_action_count)} expected actions
          </Badge>
        ) : null}
      </div>

      {row.purpose ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Purpose</h4>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{String(row.purpose)}</p>
        </div>
      ) : null}

      {row.reason_for_call ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Reason for call</h4>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {String(row.reason_for_call)}
          </p>
        </div>
      ) : null}

      {row.task_instructions ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">User instructions</h4>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
            {String(row.task_instructions)}
          </p>
        </div>
      ) : null}

      {row.known_info || row.unknown_info || row.persona ? (
        <div className="grid gap-4 md:grid-cols-2">
          {row.persona ? (
            <div>
              <h4 className="text-sm font-medium text-muted-foreground">Persona</h4>
              <p className="mt-2 whitespace-pre-wrap text-sm">{String(row.persona)}</p>
            </div>
          ) : null}
          {row.known_info ? (
            <div>
              <h4 className="text-sm font-medium text-muted-foreground">Known info</h4>
              <p className="mt-2 whitespace-pre-wrap text-sm">{String(row.known_info)}</p>
            </div>
          ) : null}
          {row.unknown_info ? (
            <div>
              <h4 className="text-sm font-medium text-muted-foreground">Unknown info</h4>
              <p className="mt-2 whitespace-pre-wrap text-sm">{String(row.unknown_info)}</p>
            </div>
          ) : null}
        </div>
      ) : null}

      {row.evaluation_criteria || row.ticket || row.initial_state ? (
        <Accordion type="multiple" className="w-full">
          {row.evaluation_criteria ? (
            <AccordionItem value="evaluation">
              <AccordionTrigger>Evaluation criteria</AccordionTrigger>
              <AccordionContent>
                <pre className="code-block">
                  {JSON.stringify(row.evaluation_criteria, null, 2)}
                </pre>
              </AccordionContent>
            </AccordionItem>
          ) : null}
          {row.ticket ? (
            <AccordionItem value="ticket">
              <AccordionTrigger>Support ticket</AccordionTrigger>
              <AccordionContent>
                <pre className="code-block">{JSON.stringify(row.ticket, null, 2)}</pre>
              </AccordionContent>
            </AccordionItem>
          ) : null}
          {row.initial_state ? (
            <AccordionItem value="initial-state">
              <AccordionTrigger>Initial state</AccordionTrigger>
              <AccordionContent>
                <pre className="code-block">{JSON.stringify(row.initial_state, null, 2)}</pre>
              </AccordionContent>
            </AccordionItem>
          ) : null}
        </Accordion>
      ) : null}
    </div>
  );
}
