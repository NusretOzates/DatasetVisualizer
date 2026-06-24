import { InstructionViewer as ViewerPrimitive } from "../InstructionViewer";
import type { SampleViewerProps } from "../types";

export function IfbenchViewer({ row }: SampleViewerProps) {
  return <ViewerPrimitive row={row} />;
}
