import type { Konflikt } from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const TOKEN_KEY = "schulplan_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  konflikte?: Konflikt[];

  constructor(status: number, message: string, konflikte?: Konflikt[]) {
    super(message);
    this.status = status;
    this.konflikte = konflikte;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (response.status === 204) {
    return undefined as T;
  }

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    if (response.status === 409 && body?.detail?.konflikte) {
      throw new ApiError(409, body.detail.detail ?? "Konflikt", body.detail.konflikte as Konflikt[]);
    }
    const message = typeof body?.detail === "string" ? body.detail : "Anfrage fehlgeschlagen.";
    throw new ApiError(response.status, message);
  }

  return body as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, data: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(data) }),
  delete: (path: string) => request<void>(path, { method: "DELETE" }),
};
