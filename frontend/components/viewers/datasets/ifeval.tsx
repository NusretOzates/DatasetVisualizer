import { InstructionViewer as ViewerPrimitive } from "../InstructionViewer";
import type { SampleViewerProps } from "../types";

export function IfevalViewer({ row }: SampleViewerProps) {
  return <ViewerPrimitive row={row} />;
}
