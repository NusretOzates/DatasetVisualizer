import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MarkdownMath } from "./MarkdownMath";

type ProblemCardProps = {
  problem: string;
  answer: string;
  solution?: string;
};

export function ProblemCard({ problem, answer, solution }: ProblemCardProps) {
  const goldAnswer = answer.trim();
  const working = solution?.trim() ?? "";

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Problem</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <MarkdownMath className="text-sm">{problem}</MarkdownMath>
        {goldAnswer ? (
          <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
            <p className="mb-1 text-xs font-medium uppercase tracking-wide text-emerald-700">
              Gold answer
            </p>
            <MarkdownMath autoWrapLatex inline>
              {goldAnswer}
            </MarkdownMath>
          </div>
        ) : null}
        {working ? (
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Solution / working
            </p>
            <div className="rounded-lg border bg-muted/20 px-4 py-3 text-sm leading-relaxed">
              <MarkdownMath autoWrapLatex className="text-sm">
                {working}
              </MarkdownMath>
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
