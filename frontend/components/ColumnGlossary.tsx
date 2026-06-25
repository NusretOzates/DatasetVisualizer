import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type ColumnGlossaryProps = {
  glossary: Record<string, string>;
};

export function ColumnGlossary({ glossary }: ColumnGlossaryProps) {
  const entries = Object.entries(glossary).sort(([left], [right]) => left.localeCompare(right));

  if (!entries.length) {
    return null;
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Column glossary</CardTitle>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible>
          <AccordionItem value="columns">
            <AccordionTrigger className="text-sm">
              Field meanings <Badge variant="secondary">{entries.length}</Badge>
            </AccordionTrigger>
            <AccordionContent>
              <dl className="space-y-3">
                {entries.map(([column, description]) => (
                  <div key={column}>
                    <dt className="font-mono text-sm font-medium">{column}</dt>
                    <dd className="mt-1 text-sm text-muted-foreground leading-relaxed">
                      {description}
                    </dd>
                  </div>
                ))}
              </dl>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </CardContent>
    </Card>
  );
}
