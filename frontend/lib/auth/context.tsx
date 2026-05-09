"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

export type UserRole = "worker" | "pm" | "hr";

interface SessionData {
  worker_id: string;
  rank_level: 1 | 2 | 3;
  rank_name: string;
  // auth_user_id removed — the HttpOnly cookie handles authentication
}

interface AuthContextValue {
  session: SessionData | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  login: (data: SessionData) => void;
  logout: () => void;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const COOKIE_NAME = "bud_session";

function rankToRole(level: number): UserRole {
  if (level === 3) return "hr";
  if (level === 2) return "pm";
  return "worker";
}

function saveSession(data: SessionData): void {
  // SameSite=Strict prevents the cookie from being sent on cross-site requests.
  // Not HttpOnly because JS needs to read it for context rehydration —
  // move to an HttpOnly cookie set by the server when the backend supports it.
  const value = encodeURIComponent(JSON.stringify(data));
  document.cookie = `${COOKIE_NAME}=${value}; path=/; SameSite=Strict`;
}

function loadSession(): SessionData | null {
  if (typeof window === "undefined") return null;
  try {
    const match = document.cookie
      .split("; ")
      .find((row) => row.startsWith(`${COOKIE_NAME}=`));
    if (!match) return null;
    const raw = decodeURIComponent(match.split("=").slice(1).join("="));
    return JSON.parse(raw) as SessionData;
  } catch {
    return null;
  }
}

function clearSession(): void {
  // Expire the cookie immediately
  document.cookie = `${COOKIE_NAME}=; path=/; max-age=0; SameSite=Strict`;
}

// ─── Context ──────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<SessionData | null>(null);

  // Rehydrate from the cookie on first client render
  useEffect(() => {
    const stored = loadSession();
    if (stored) setSession(stored);
  }, []);

  const login = useCallback((data: SessionData) => {
    saveSession(data); // sets the cookie the middleware reads
    setSession(data);
  }, []);

  const logout = useCallback(() => {
    clearSession(); // expires the cookie
    setSession(null);
  }, []);

  const role = session ? rankToRole(session.rank_level) : null;

  return (
    <AuthContext.Provider
      value={{
        session,
        role,
        isAuthenticated: session !== null,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
