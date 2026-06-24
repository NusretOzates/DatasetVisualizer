import { PaperBenchViewer as ViewerPrimitive } from "../PaperBenchViewer";
import type { SampleViewerProps } from "../types";

export function PaperbenchViewer(props: SampleViewerProps) {
  return <ViewerPrimitive {...props} />;
}
