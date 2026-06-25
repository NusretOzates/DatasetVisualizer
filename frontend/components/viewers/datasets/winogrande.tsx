import { McqViewer } from "../McqViewer";
import type { SampleViewerProps } from "../types";

export function WinograndeViewer({ row }: SampleViewerProps) {
  return <McqViewer row={row} />;
}
