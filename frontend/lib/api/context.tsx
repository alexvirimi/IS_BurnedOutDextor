// ─── API helpers ──────────────────────────────────────────────────────────────
// credentials: "include" sends the HttpOnly cookie automatically.
// No auth header needed — the backend reads identity from the JWT cookie.

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { credentials: "include" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Error ${res.status}`);
  }
  return res.json();
}

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
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Error ${res.status}`);
  }
  return res.json();
}
