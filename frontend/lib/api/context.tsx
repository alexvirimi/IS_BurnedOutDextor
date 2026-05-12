// ─── API helpers ──────────────────────────────────────────────────────────────
// credentials: "include" sends the HttpOnly cookie automatically.
// No auth header needed — the backend reads identity from the JWT cookie.

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

/**
 * POST with a multipart/form-data body (legacy — used for most endpoints
 * that declare FastAPI `as_form` dependencies).
 */
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

/**
 * POST with a JSON body.
 * Used for endpoints that accept a Pydantic model directly in the request body
 * (e.g. POST /answers/bulk).
 */
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
