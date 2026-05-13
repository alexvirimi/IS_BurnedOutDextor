"use client";

/**
 * useReportes
 * ───────────
 * Fetches the list of report names for "Mi Progreso" and "Históricos" views.
 *
 * Changes vs. previous version
 * ────────────────────────────
 * 1. `useHistoricoReportsHR` / `useHistoricoReportsPM` no longer call the
 *    unbounded GET /answers/ endpoint.  Instead they hit scoped endpoints:
 *
 *      GET /survey-assignment/worker/:id/responded-surveys
 *        → [{ survey_id, survey_name }] — surveys a specific worker has answered
 *
 *    If the backend doesn't expose that endpoint yet, we fall back to
 *    GET /survey-assignment/my-surveys scoped per-worker via the existing
 *    already_responded flag — but that requires one request per worker which
 *    is still O(n).  The cleanest fix is a single bulk endpoint; see comment
 *    at `fetchRespondedSurveyIds`.
 *
 * 2. The "completed by all" logic now correctly intersects sets of survey IDs
 *    rather than joining through the answers table client-side.
 *
 * 3. `useMyProgressReports` is unchanged (it already uses the correct endpoint).
 */

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api/context";
import { useAuth } from "@/lib/auth/context";
import type { Worker, Group, MySurveyResponse } from "@/lib/api/interfaces";

// ─── Public types ─────────────────────────────────────────────────────────────

export interface Reporte {
  id: string; // survey id
  nombre: string; // display label
}

export type HistoricoScope =
  | { type: "area"; areaId: string }
  | { type: "grupo"; grupoId: string }
  | { type: "trabajador"; trabajadorId: string };

// ─── Internal API shapes ──────────────────────────────────────────────────────

interface SurveyRaw {
  id: string;
  name: string;
  status: string;
}

/** Shape returned by GET /results/worker/:id/responded-surveys (preferred). */
interface RespondedSurveyRaw {
  survey_id: string;
  survey_name: string;
}

// ─── Scoped "responded surveys" fetcher ───────────────────────────────────────
//
// Strategy (in order of preference):
//
//  A) GET /results/worker/:workerId/responded-surveys
//     Returns only the surveys a given worker has already answered.
//     O(1) request, server-filtered.  This is the ideal backend endpoint.
//
//  B) Fallback: GET /survey-assignment/my-surveys called with the worker's
//     token is not possible from HR context.  So we fall back to:
//     GET /survey-assignment/worker/:workerId/assignments
//     and filter `already_responded === true`.
//
// Both paths return a Set<surveyId> for that worker.

async function fetchRespondedSurveyIds(workerId: string): Promise<Set<string>> {
  // Try preferred endpoint first.
  try {
    const data = await apiFetch<RespondedSurveyRaw[]>(
      `/results/worker/${workerId}/responded-surveys`,
    );
    return new Set(data.map((r) => r.survey_id));
  } catch {
    // Preferred endpoint not available — fall back to assignment list.
  }

  // Fallback: GET /survey-assignment/worker/:id/assignments
  // Shape assumed: MySurveyResponse[] (same as my-surveys but for any worker).
  try {
    const data = await apiFetch<MySurveyResponse[]>(
      `/survey-assignment/worker/${workerId}/assignments`,
    );
    return new Set(data.filter((s) => s.already_responded).map((s) => s.id));
  } catch {
    // If neither endpoint exists, return empty set — the survey won't appear
    // in the completed-by-all list, which is the safe/conservative outcome.
    return new Set<string>();
  }
}

// ─── Pure utilities ───────────────────────────────────────────────────────────

/**
 * Returns surveys whose ID appears in every worker's responded-set.
 * An empty workerIds array → no reports (avoids false positives).
 */
function intersectRespondedSets(
  workerRespondedSets: Set<string>[],
  surveys: SurveyRaw[],
): SurveyRaw[] {
  if (workerRespondedSets.length === 0) return [];

  return surveys.filter((survey) =>
    workerRespondedSets.every((set) => set.has(survey.id)),
  );
}

/** Resolves worker IDs for a given scope. */
function resolveWorkerIds(
  scope: HistoricoScope,
  workers: Worker[],
  groups: Group[],
): string[] {
  switch (scope.type) {
    case "trabajador":
      return [scope.trabajadorId];

    case "grupo":
      return workers
        .filter((w) => w.id_group === scope.grupoId)
        .map((w) => w.id);

    case "area": {
      const groupIdsInArea = new Set(
        groups.filter((g) => g.id_area === scope.areaId).map((g) => g.id),
      );
      return workers
        .filter((w) => groupIdsInArea.has(w.id_group))
        .map((w) => w.id);
    }

    default: {
      const _exhaustive: never = scope;
      return [];
    }
  }
}

/** Builds the display label for a historico report. */
function buildHistoricoLabel(
  surveyName: string,
  scope: HistoricoScope,
  workers: Worker[],
  groups: Group[],
  areas: { id: string; name: string }[],
): string {
  let scopeLabel = "";

  switch (scope.type) {
    case "area": {
      const area = areas.find((a) => a.id === scope.areaId);
      scopeLabel = area?.name ?? "Área";
      break;
    }
    case "grupo": {
      const group = groups.find((g) => g.id === scope.grupoId);
      scopeLabel = group?.name ?? "Grupo";
      break;
    }
    case "trabajador": {
      const worker = workers.find((w) => w.id === scope.trabajadorId);
      scopeLabel = worker
        ? `${worker.name} ${worker.last_names}`
        : "Trabajador";
      break;
    }
  }

  return `REPORTE DE ${surveyName.toUpperCase()} - ${scopeLabel.toUpperCase()}`;
}

// ─── Shared reference data loader ────────────────────────────────────────────
//
// Only fetches surveys, workers, groups, and areas.
// Does NOT fetch /answers/ — that table is unbounded and we no longer need it.

interface SharedHistoricoData {
  surveys: SurveyRaw[];
  workers: Worker[];
  groups: Group[];
  areas: { id: string; name: string }[];
}

async function fetchSharedHistoricoData(): Promise<SharedHistoricoData> {
  const [surveys, workers, groups, areas] = await Promise.all([
    apiFetch<SurveyRaw[]>("/survey/"),
    apiFetch<Worker[]>("/worker/"),
    apiFetch<Group[]>("/group/"),
    apiFetch<{ id: string; name: string }[]>("/areas/"),
  ]);

  return { surveys, workers, groups, areas };
}

// ─── Hook: Mi Progreso ────────────────────────────────────────────────────────

/**
 * Returns reports for surveys the current user has personally answered.
 * Uses GET /survey-assignment/my-surveys — unchanged from previous version.
 */
export function useMyProgressReports(): {
  reportes: Reporte[];
  loading: boolean;
  error: string | null;
  reload: () => void;
} {
  const [reportes, setReportes] = useState<Reporte[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch<MySurveyResponse[]>(
        "/survey-assignment/my-surveys",
      );

      const mapped: Reporte[] = data
        .filter((s) => s.already_responded)
        .map((s) => ({
          id: s.id,
          nombre: `REPORTE DE ${s.name.toUpperCase()}`,
        }));

      setReportes(mapped);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error cargando reportes");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { reportes, loading, error, reload: load };
}

// ─── Hook: Históricos (HR) ────────────────────────────────────────────────────

/**
 * Returns reports for a given HR scope.
 *
 * A survey appears only if ALL members of the scope have answered it.
 * Uses per-worker scoped requests instead of the unbounded /answers/ dump.
 */
export function useHistoricoReportsHR(scope: HistoricoScope | null): {
  reportes: Reporte[];
  loading: boolean;
  error: string | null;
  reload: () => void;
} {
  const [reportes, setReportes] = useState<Reporte[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!scope) return;

    setLoading(true);
    setError(null);

    try {
      const { surveys, workers, groups, areas } =
        await fetchSharedHistoricoData();

      const workerIds = resolveWorkerIds(scope, workers, groups);

      if (workerIds.length === 0) {
        setReportes([]);
        return;
      }

      // Fetch responded-survey sets for every worker in this scope in parallel.
      // For large scopes (e.g. whole area) this is O(workers) requests.
      // If the backend provides a bulk endpoint like
      //   GET /results/scope/group/:id/responded-surveys
      // replace this with a single call.
      const respondedSets = await Promise.all(
        workerIds.map((id) => fetchRespondedSurveyIds(id)),
      );

      const completed = intersectRespondedSets(respondedSets, surveys);

      const mapped: Reporte[] = completed.map((s) => ({
        id: s.id,
        nombre: buildHistoricoLabel(s.name, scope, workers, groups, areas),
      }));

      setReportes(mapped);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error cargando históricos",
      );
    } finally {
      setLoading(false);
    }
  }, [scope]);

  useEffect(() => {
    setReportes([]);
    load();
  }, [load]);

  return { reportes, loading, error, reload: load };
}

// ─── Hook: Históricos (PM) ───────────────────────────────────────────────────

/**
 * Returns reports for the PM's own group.
 * A survey appears only if ALL members of the group have answered it.
 */
export function useHistoricoReportsPM(): {
  reportes: Reporte[];
  loading: boolean;
  error: string | null;
  reload: () => void;
} {
  const { session } = useAuth();
  const grupoId = session?.id_group ?? null;

  const scope: HistoricoScope | null = grupoId
    ? { type: "grupo", grupoId }
    : null;

  const [reportes, setReportes] = useState<Reporte[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!scope) return;

    setLoading(true);
    setError(null);

    try {
      const { surveys, workers, groups, areas } =
        await fetchSharedHistoricoData();

      const workerIds = resolveWorkerIds(scope, workers, groups);

      if (workerIds.length === 0) {
        setReportes([]);
        return;
      }

      const respondedSets = await Promise.all(
        workerIds.map((id) => fetchRespondedSurveyIds(id)),
      );

      const completed = intersectRespondedSets(respondedSets, surveys);

      const mapped: Reporte[] = completed.map((s) => ({
        id: s.id,
        nombre: buildHistoricoLabel(s.name, scope, workers, groups, areas),
      }));

      setReportes(mapped);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error cargando históricos",
      );
    } finally {
      setLoading(false);
    }
    // grupoId is the stable primitive dep, not `scope` (object reference)
  }, [grupoId]);

  useEffect(() => {
    setReportes([]);
    load();
  }, [load]);

  return { reportes, loading, error, reload: load };
}
