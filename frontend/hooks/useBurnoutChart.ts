"use client";

/**
 * useBurnoutChart
 * ────────────────
 * Fetches the right burnout-progress endpoint based on the selected Reporte.
 *
 * Accepts a `Reporte` (from useReportes) and a `scope` that tells it which
 * entity to fetch data for.  Returns `{ data, loading, error }` ready to
 * pass directly to <BurnoutLineChart dataSource={data} />.
 *
 * Scope variants:
 *   { type: "self" }                          → GET /results/my-progress
 *   { type: "worker",     workerId: string }  → GET /results/worker/:id/progress
 *   { type: "group",      groupId: string }   → GET /results/group/:id/progress
 *   { type: "area",       areaId: string }    → GET /results/area/:id/progress
 *
 * The hook re-fetches automatically whenever `scope` or `reporteId` changes.
 * Pass `reporteId: null` to clear the chart (dataSource becomes null).
 */

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api/context";
import type { ProgressPoint } from "@/components/dashboard/shared/burnout-line-chart";
import type { ChartMode } from "@/components/dashboard/shared/burnout-line-chart";

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

  const fetch = useCallback(async () => {
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
  }, [scope, reporteId]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, loading, error, reload: fetch };
}
