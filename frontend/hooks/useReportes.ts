"use client";

/**
 * useReportes
 * ───────────
 * Fetches and derives the list of report names to display in
 * "Mi Progreso" and "Históricos" views across all roles (HR, PM, WKR).
 *
 * Public API
 * ──────────
 * useMyProgressReports()
 *   → surveys the current user has already answered
 *
 * useHistoricoReports(scope)
 *   → surveys where EVERY member of the scope has answered completely
 *
 * Neither hook fires actual Power BI requests — they only derive names.
 */

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api/context";
import { useAuth } from "@/lib/auth/context";
import type { Worker, Group, MySurveyResponse } from "@/lib/api/interfaces";

// ─── Local types ──────────────────────────────────────────────────────────────

export interface Reporte {
  id: string; // survey id — stable key for React lists
  nombre: string; // display label shown in ReporteList
}

// Scope discriminated union — extensible for future filter types
export type HistoricoScope =
  | { type: "area"; areaId: string }
  | { type: "grupo"; grupoId: string }
  | { type: "trabajador"; trabajadorId: string };

// Raw shapes we need from the API (only the fields we use)
interface AnswerRaw {
  id: string;
  id_worker: string;
  id_question_survey: string;
}

interface QuestionSurveyRaw {
  id: string;
  id_survey: string;
}

interface SurveyRaw {
  id: string;
  name: string;
  status: string;
}

// ─── Pure utilities ───────────────────────────────────────────────────────────

/**
 * Builds a Map<surveyId, Set<workerId>> representing which workers
 * have answered at least one question in each survey.
 *
 * Uses answers + question_surveys to bridge the gap between
 * "which answer" and "which survey".
 */
function buildSurveyResponderMap(
  answers: AnswerRaw[],
  questionSurveys: QuestionSurveyRaw[],
): Map<string, Set<string>> {
  // id_question_survey → id_survey
  const qsToSurvey = new Map<string, string>(
    questionSurveys.map((qs) => [qs.id, qs.id_survey]),
  );

  const map = new Map<string, Set<string>>();

  for (const answer of answers) {
    const surveyId = qsToSurvey.get(answer.id_question_survey);
    if (!surveyId) continue;
    if (!map.has(surveyId)) map.set(surveyId, new Set());
    map.get(surveyId)!.add(answer.id_worker);
  }

  return map;
}

/**
 * Returns the surveys where EVERY worker in `workerIds` has responded.
 *
 * "Responded" is defined as: the worker appears in the responder set
 * for that survey (i.e. answered at least one question).
 *
 * An empty `workerIds` set → no reports (avoids false positives).
 */
function surveysCompletedByAll(
  workerIds: string[],
  surveys: SurveyRaw[],
  surveyResponderMap: Map<string, Set<string>>,
): SurveyRaw[] {
  if (workerIds.length === 0) return [];

  return surveys.filter((survey) => {
    const responders = surveyResponderMap.get(survey.id);
    if (!responders) return false;
    return workerIds.every((wid) => responders.has(wid));
  });
}

/**
 * Resolves the worker IDs that belong to a given scope.
 */
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

/**
 * Builds the display label for a historico report.
 *
 * Format: "REPORTE DE {survey_name} - {scope label}"
 */
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

// ─── Shared data loader ───────────────────────────────────────────────────────
// Both historico hooks need the same 4 endpoints. We fetch them in parallel
// once and pass the results down to avoid duplicate requests.

interface SharedHistoricoData {
  surveys: SurveyRaw[];
  answers: AnswerRaw[];
  questionSurveys: QuestionSurveyRaw[];
  workers: Worker[];
  groups: Group[];
  areas: { id: string; name: string }[];
}

async function fetchSharedHistoricoData(): Promise<SharedHistoricoData> {
  const [surveys, answers, questionSurveys, workers, groups, areas] =
    await Promise.all([
      apiFetch<SurveyRaw[]>("/survey/"),
      apiFetch<AnswerRaw[]>("/answers/"),
      apiFetch<QuestionSurveyRaw[]>("/question_survey/"),
      apiFetch<Worker[]>("/worker/"),
      apiFetch<Group[]>("/group/"),
      apiFetch<{ id: string; name: string }[]>("/areas/"),
    ]);

  return { surveys, answers, questionSurveys, workers, groups, areas };
}

// ─── Hook: Mi Progreso ────────────────────────────────────────────────────────

/**
 * Returns reports for surveys the current user has personally answered.
 * Hits only one endpoint: GET /survey-assignment/my-surveys
 *
 * Format: "REPORTE DE {survey_name}"
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
        // Only surveys the user has actually answered
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
 * Returns reports for a given HR scope (area / grupo / trabajador).
 * A survey appears only if ALL members of the scope have answered it.
 *
 * Re-fetches automatically when `scope` changes.
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
      const { surveys, answers, questionSurveys, workers, groups, areas } =
        await fetchSharedHistoricoData();

      const surveyResponderMap = buildSurveyResponderMap(
        answers,
        questionSurveys,
      );
      const workerIds = resolveWorkerIds(scope, workers, groups);
      const completed = surveysCompletedByAll(
        workerIds,
        surveys,
        surveyResponderMap,
      );

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
 * Returns reports for the PM's own group (read from auth session).
 * A survey appears only if ALL members of the group have answered it.
 */
export function useHistoricoReportsPM(): {
  reportes: Reporte[];
  loading: boolean;
  error: string | null;
  reload: () => void;
} {
  const { session } = useAuth();

  // PM's group id comes from the JWT stored in auth context
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
      const { surveys, answers, questionSurveys, workers, groups, areas } =
        await fetchSharedHistoricoData();

      const surveyResponderMap = buildSurveyResponderMap(
        answers,
        questionSurveys,
      );
      const workerIds = resolveWorkerIds(scope, workers, groups);
      const completed = surveysCompletedByAll(
        workerIds,
        surveys,
        surveyResponderMap,
      );

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
  }, [scope?.type === "grupo" ? scope.grupoId : null]);

  useEffect(() => {
    setReportes([]);
    load();
  }, [load]);

  return { reportes, loading, error, reload: load };
}
