// ─── Config ───────────────────────────────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface LoginPayload {
  username: string;
  password: string;
}

export interface LoginResponse {
  auth_user_id: string;
  worker_id: string;
  rank_level: 1 | 2 | 3;
  rank_name: string;
}

// ─── Core fetch wrapper ───────────────────────────────────────────────────────

/**
 * Sends a multipart/form-data POST (matching the backend's Form(...) params).
 * Pass `authUserId` to include the `auth-user-id` header on authenticated calls.
 */
async function postForm<T>(
  path: string,
  body: Record<string, string>,
  authUserId?: string,
): Promise<T> {
  const formData = new FormData();
  for (const [key, value] of Object.entries(body)) {
    formData.append(key, value);
  }

  const headers: HeadersInit = {};
  if (authUserId) headers["auth-user-id"] = authUserId;

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    // Surface the backend detail message when available
    let detail = `HTTP ${res.status}`;
    try {
      const json = await res.json();
      detail = json.detail ?? detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }

  return res.json() as Promise<T>;
}

// ─── Auth endpoints ───────────────────────────────────────────────────────────

export const authApi = {
  login(payload: LoginPayload): Promise<LoginResponse> {
    return postForm<LoginResponse>("/auth/login", {
      username: payload.username,
      password: payload.password,
    });
  },

  logout(): Promise<void> {
    return fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      credentials: "include", // sends the HttpOnly cookie automatically
    }).then(() => undefined);
  },
};
