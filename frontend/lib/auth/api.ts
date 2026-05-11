// ─── Config ───────────────────────────────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface LoginPayload {
  username: string;
  password: string;
}

export interface LoginResponse {
  worker_id: string;
  rank_level: 1 | 2 | 3;
  rank_name: string;
  // The backend returns the raw JWT in the JSON body so the frontend can use
  // it as a Bearer fallback for cross-origin PATCH / DELETE requests where
  // samesite="lax" prevents the HttpOnly cookie from being forwarded.
  // This field matches the "access_token" key in the login JSON response.
  access_token: string;
}

// ─── Core fetch wrapper ───────────────────────────────────────────────────────

async function postForm<T>(
  path: string,
  body: Record<string, string>,
): Promise<T> {
  const formData = new FormData();
  for (const [key, value] of Object.entries(body)) {
    formData.append(key, value);
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData,
    credentials: "include", // sends the HttpOnly cookie if already set
  });

  if (!res.ok) {
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
      credentials: "include",
    }).then(() => undefined);
  },
};
