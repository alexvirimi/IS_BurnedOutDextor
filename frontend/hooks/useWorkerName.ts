"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth/context";
import { apiFetch } from "@/lib/api/context";

interface WorkerDetails {
  name: string;
  last_names: string;
}

interface UseWorkerNameResult {
  fullName: string;
  isLoading: boolean;
}

/**
 * Fetches the authenticated worker's full name from /worker/{worker_id}/details.
 *
 * The endpoint is public (no auth required), so no cookie or header is needed.
 * Falls back to the rank_name stored in the session cookie if the fetch fails,
 * so the sidebar never shows an empty string.
 */
export function useWorkerName(): UseWorkerNameResult {
  const { session } = useAuth();
  const [fullName, setFullName] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!session) {
      setIsLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchName() {
      try {
        const data: WorkerDetails = await apiFetch<WorkerDetails>(
          `/worker/${session!.worker_id}/details`,
        );

        if (!cancelled) {
          setFullName(`${data.name} ${data.last_names}`.trim());
        }
      } catch {
        // Graceful fallback: show the rank name stored in the session cookie.
        // session.rank_name is still present even though auth_user_id was removed.
        if (!cancelled) {
          setFullName(session!.rank_name ?? "");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    fetchName();

    return () => {
      cancelled = true;
    };
  }, [session]);

  return { fullName, isLoading };
}
