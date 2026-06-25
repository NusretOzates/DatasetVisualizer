import { DatasetPageClient } from "@/components/DatasetPageClient";
import { CATALOG_DATASET_IDS } from "@/lib/catalog-ids";
import { fetchCatalog } from "@/lib/api";

export async function generateStaticParams() {
  try {
    const catalog = await fetchCatalog();
    const ids = catalog.categories.flatMap((category) =>
      category.datasets.map((dataset) => dataset.id),
    );
    if (ids.length) {
      return ids.map((id) => ({ id }));
    }
  } catch {
    // Backend unavailable during static export — fall back to committed catalog ids.
  }
  return CATALOG_DATASET_IDS.map((id) => ({ id }));
}

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function DatasetPage({ params }: PageProps) {
  const { id } = await params;
  return <DatasetPageClient datasetId={id} />;
}
