"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth/context";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface WorkerDetails {
  name: string;
  last_names: string;
}

interface UseWorkerNameResult {
  fullName: string;
  isLoading: boolean;
}

/**
 * Fetches the authenticated worker's full name.
 *
 * Strategy:
 *   1. session.worker_id is already in context from login — use it directly.
 *   2. GET /worker/{worker_id}/details with the auth-user-id header.
 *   3. Returns "name last_names" as a single string.
 *
 * Falls back to rank_name if the fetch fails, so the sidebar
 * never shows an empty string.
 */
export function useWorkerName(): UseWorkerNameResult {
  const { session } = useAuth();
  const [fullName, setFullName] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Nothing to fetch if there is no session
    if (!session) {
      setIsLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchName() {
      try {
        // worker_id is already available from login response —
        // no need to call /auth/me first.
        const res = await fetch(
          `${API_BASE}/worker/${session!.worker_id}/details`,
          {
            headers: {
              "auth-user-id": session!.auth_user_id,
            },
          },
        );

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data: WorkerDetails = await res.json();

        if (!cancelled) {
          setFullName(`${data.name} ${data.last_names}`.trim());
        }
      } catch {
        // Graceful fallback: show rank name so the sidebar is never blank
        if (!cancelled) {
          setFullName(session!.rank_name);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    fetchName();

    // Cleanup: if the component unmounts before the fetch resolves,
    // discard the result to avoid a state update on an unmounted component.
    return () => {
      cancelled = true;
    };
  }, [session]);

  return { fullName, isLoading };
}
