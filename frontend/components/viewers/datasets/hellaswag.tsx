import { McqViewer } from "../McqViewer";
import type { SampleViewerProps } from "../types";

export function HellaswagViewer({ row }: SampleViewerProps) {
  return <McqViewer row={row} />;
}
