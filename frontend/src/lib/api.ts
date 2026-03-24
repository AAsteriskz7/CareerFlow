/**
 * Typed API client for the CareerFlow backend.
 */

import type { OrchestrationRequest, OrchestrationResponse } from "@/types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return res.json() as Promise<T>;
}

/** Run the full orchestration pipeline. */
export async function orchestrate(
  request: OrchestrationRequest
): Promise<OrchestrationResponse> {
  return apiFetch<OrchestrationResponse>("/orchestrate", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/** Trigger an index rebuild on the backend. */
export async function rebuildIndex(): Promise<{ status: string; message: string }> {
  return apiFetch("/index/rebuild", { method: "POST" });
}

/** Health check. */
export async function healthCheck(): Promise<{ status: string; version: string }> {
  return apiFetch("/health");
}
