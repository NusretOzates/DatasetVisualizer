"use client";

import { CodeProblemViewer } from "./CodeProblemViewer";
import type { SampleViewerProps } from "./types";

export function CodeProblemSampleViewer({
  row,
  privateTests,
  privateTestsLoading,
}: SampleViewerProps) {
  return (
    <CodeProblemViewer
      row={row}
      privateTests={privateTests}
      privateTestsLoading={privateTestsLoading}
    />
  );
}
