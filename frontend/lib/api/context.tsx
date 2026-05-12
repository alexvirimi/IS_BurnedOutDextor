// ─── lib/api/context.tsx ─────────────────────────────────────────────────────
// Añade apiPostJson para endpoints que esperan application/json (no FormData).
// Mantiene todos los helpers existentes sin modificación.

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

let _token: string | null = null;
export function setApiToken(token: string | null) {
  _token = token;
}

function authHeaders(): HeadersInit {
  return _token ? { Authorization: `Bearer ${_token}` } : {};
}

export async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: authHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Error ${res.status}`);
  }
  return res.json();
}

/** POST con FormData — para endpoints que usan Depends(Schema.as_form) */
export async function apiPost<T>(
  path: string,
  body: Record<string, string>,
): Promise<T> {
  const formData = new FormData();
  for (const [k, v] of Object.entries(body)) formData.append(k, v);
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData,
    credentials: "include",
    headers: authHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Error ${res.status}`);
  }
  return res.json();
}

/** POST con JSON — para endpoints que reciben application/json (ej. survey-assignment/assign) */
export async function apiPostJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(body),
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Error ${res.status}`);
  }
  return res.json();
}

export async function apiPatch<T>(
  path: string,
  body: Record<string, string>,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(body),
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Error ${res.status}`);
  }
  return res.json();
}

export async function apiDelete(path: string): Promise<void> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    credentials: "include",
    headers: authHeaders(),
  });
  if (!res.ok && res.status !== 204) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Error ${res.status}`);
  }
}
