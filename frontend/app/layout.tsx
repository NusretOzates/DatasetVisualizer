import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dataset Visualizer",
  description: "Explore Hugging Face benchmark datasets",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
