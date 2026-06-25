import { McqViewer } from "../McqViewer";
import type { SampleViewerProps } from "../types";

export function CommonsenseqaViewer({ row }: SampleViewerProps) {
  return <McqViewer row={row} />;
}
