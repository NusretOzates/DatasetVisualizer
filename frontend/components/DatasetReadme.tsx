import { MarkdownContent } from "@/components/MarkdownContent";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type DatasetReadmeProps = {
  readme: string;
};

export function DatasetReadme({ readme }: DatasetReadmeProps) {
  if (!readme.trim()) {
    return null;
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Dataset README</CardTitle>
      </CardHeader>
      <CardContent>
        <MarkdownContent>{readme}</MarkdownContent>
      </CardContent>
    </Card>
  );
}
