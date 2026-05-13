"use client";

/**
 * useBurnoutChart
 * ────────────────
 * Fetches the right burnout-progress endpoint based on scope.
 *
 * FIX 1: scope is serialized to a string key for stable comparison —
 *         passing { type: "self" } inline was creating a new object
 *         every render, causing useCallback to see a changed dependency
 *         and triggering an infinite fetch → state update → re-render loop.
 *
 * FIX 2: reporteId is kept as a trigger so the chart refetches when the
 *         user selects a different report, but null still clears the chart
 *         without fetching.
 *
 * Scope variants:
 *   { type: "self" }                          → GET /results/my-progress
 *   { type: "worker",  workerId: string }     → GET /results/worker/:id/progress
 *   { type: "group",   groupId: string }      → GET /results/group/:id/progress
 *   { type: "area",    areaId: string }       → GET /results/area/:id/progress
 */

import { useState, useEffect, useCallback, useMemo } from "react";
import { apiFetch } from "@/lib/api/context";
import type {
  ProgressPoint,
  ChartMode,
} from "@/components/dashboard/shared/burnout-line-chart";

// ─── Scope discriminated union ────────────────────────────────────────────────

export type ChartScope =
  | { type: "self" }
  | { type: "worker"; workerId: string }
  | { type: "group"; groupId: string }
  | { type: "area"; areaId: string };

// Maps scope type → ChartMode prop for BurnoutLineChart
export function scopeToMode(scope: ChartScope): ChartMode {
  switch (scope.type) {
    case "self":
      return "self";
    case "worker":
      return "individual";
    case "group":
      return "group";
    case "area":
      return "area";
  }
}

// Builds the API path for each scope
function buildPath(scope: ChartScope): string | null {
  switch (scope.type) {
    case "self":
      return "/results/my-progress";
    case "worker":
      return `/results/worker/${scope.workerId}/progress`;
    case "group":
      return `/results/group/${scope.groupId}/progress`;
    case "area":
      return `/results/area/${scope.areaId}/progress`;
    default:
      return null;
  }
}

/**
 * Serializes a ChartScope to a stable string for use as a useEffect dependency.
 * This avoids the infinite-loop caused by inline object literals like
 * { type: "self" } which are recreated on every render.
 */
function scopeKey(scope: ChartScope): string {
  switch (scope.type) {
    case "self":
      return "self";
    case "worker":
      return `worker:${scope.workerId}`;
    case "group":
      return `group:${scope.groupId}`;
    case "area":
      return `area:${scope.areaId}`;
  }
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

interface UseBurnoutChartResult {
  /** null = no reporte selected yet; [] = selected but no data */
  data: ProgressPoint[] | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

export function useBurnoutChart(
  scope: ChartScope,
  /** Pass null to clear chart without fetching */
  reporteId: string | null,
): UseBurnoutChartResult {
  const [data, setData] = useState<ProgressPoint[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Stable key — does NOT change when the caller passes a new object literal
  // with the same logical value (e.g. { type: "self" } every render).
  const key = scopeKey(scope);

  const fetchData = useCallback(async () => {
    if (reporteId === null) {
      setData(null);
      return;
    }

    const path = buildPath(scope);
    if (!path) return;

    setLoading(true);
    setError(null);

    try {
      const points = await apiFetch<ProgressPoint[]>(path);
      setData(points);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error cargando datos del gráfico",
      );
      setData([]);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, reporteId]); // key instead of scope — prevents infinite loops

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, reload: fetchData };
}
