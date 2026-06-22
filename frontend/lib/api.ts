import { Client } from "@gradio/client";
import type {
  Catalog,
  DatasetMeta,
  OverviewPayload,
  SamplePayload,
} from "./types";

let clientPromise: Promise<Client> | null = null;

function getApiUrl(): string {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL || window.location.origin;
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:7860";
}

async function getClient(): Promise<Client> {
  if (!clientPromise) {
    clientPromise = Client.connect(getApiUrl());
  }
  return clientPromise;
}

function unwrapPredictResult<T>(result: unknown): T {
  if (result === null || typeof result !== "object") {
    return result as T;
  }

  const payload = result as { data?: unknown };
  if (payload.data === undefined) {
    return result as T;
  }

  if (Array.isArray(payload.data)) {
    return payload.data[0] as T;
  }

  if (typeof payload.data === "object" && payload.data !== null && "0" in payload.data) {
    return (payload.data as Record<string, unknown>)["0"] as T;
  }

  return payload.data as T;
}

async function predict<T>(apiName: string, payload: Record<string, unknown>): Promise<T> {
  const client = await getClient();
  const result = await client.predict(apiName, payload);
  return unwrapPredictResult<T>(result);
}

export async function fetchCatalog(): Promise<Catalog> {
  return predict<Catalog>("/get_catalog", {});
}

export async function fetchDatasetMeta(datasetId: string): Promise<DatasetMeta> {
  return predict<DatasetMeta>("/get_dataset_meta", { dataset_id: datasetId });
}

export async function fetchFilterOptions(
  datasetId: string,
  params: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  return predict<Record<string, unknown>>("/get_filter_options", {
    dataset_id: datasetId,
    params_json: JSON.stringify(params),
  });
}

export async function fetchOverview(
  datasetId: string,
  params: Record<string, unknown>,
  filters: Record<string, unknown>,
): Promise<OverviewPayload> {
  return predict<OverviewPayload>("/get_overview", {
    dataset_id: datasetId,
    params_json: JSON.stringify(params),
    filters_json: JSON.stringify(filters),
  });
}

export async function fetchSample(
  datasetId: string,
  index: number,
  params: Record<string, unknown>,
  filters: Record<string, unknown>,
): Promise<SamplePayload> {
  return predict<SamplePayload>("/get_sample", {
    dataset_id: datasetId,
    index,
    params_json: JSON.stringify(params),
    filters_json: JSON.stringify(filters),
  });
}

export async function findSample(
  datasetId: string,
  idValue: string,
  params: Record<string, unknown>,
  filters: Record<string, unknown>,
): Promise<SamplePayload> {
  return predict<SamplePayload>("/find_sample", {
    dataset_id: datasetId,
    id_value: idValue,
    params_json: JSON.stringify(params),
    filters_json: JSON.stringify(filters),
  });
}

export async function decodePrivateTests(raw: string): Promise<{ cases: Record<string, unknown>[] }> {
  return predict<{ cases: Record<string, unknown>[] }>("/decode_private_tests", { raw });
}
