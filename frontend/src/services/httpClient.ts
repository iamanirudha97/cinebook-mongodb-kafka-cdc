import { API_BASE_URL } from "../config/env";
import type { ApiResult } from "../types/cinebook";

export async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<ApiResult<T>> {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const body = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      typeof body?.detail === "string"
        ? body.detail
        : Array.isArray(body?.detail)
          ? body.detail.map((d: { msg?: string }) => d.msg).join(", ")
          : `Request failed (HTTP ${response.status})`;

    return { ok: false, status: response.status, error: detail };
  }

  return { ok: true, status: response.status, data: body as T };
}

