"use client";

/**
 * HRMiProgreso / WKRProgresoView / PMProgresoView — UPDATED
 * ──────────────────────────────────────────────────────────
 * The chart now reacts to which Reporte the user has selected.
 * Replace the existing component body with this pattern.
 * (Shown here as HRMiProgreso; WKR/PM are identical — same pattern.)
 *
 * Key changes vs original:
 *   1. Removed the self-fetching from <BurnoutLineChart />.
 *      The chart now receives `dataSource` instead.
 *   2. Added `useBurnoutChart` with scope = { type: "self" } for Mi Progreso.
 *   3. Clicking a Reporte in <ReporteList> calls setSelectedReporte,
 *      which triggers useBurnoutChart to refetch for that reporteId.
 *
 * The approach is identical for all three roles' Mi Progreso views.
 */

import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import { BurnoutLineChart } from "@/components/dashboard/shared/burnout-line-chart";
import { ReporteList } from "@/components/dashboard/shared/reporte-list";
import { useMyProgressReports } from "@/hooks/useReportes";
import { useBurnoutChart } from "@/hooks/useBurnoutChart";
import type { Reporte } from "@/hooks/useReportes";

export function WKRProgresoView() {
  const {
    reportes,
    loading: listLoading,
    error: listError,
  } = useMyProgressReports();
  const [selectedReporte, setSelectedReporte] = useState<Reporte | null>(null);

  // Auto-select the first report once data loads
  useEffect(() => {
    if (reportes.length > 0 && !selectedReporte) {
      setSelectedReporte(reportes[0]);
    }
  }, [reportes]);

  // Fetch chart data for the selected report — always "self" scope for Mi Progreso
  const {
    data: chartData,
    loading: chartLoading,
    error: chartError,
  } = useBurnoutChart(
    { type: "self" },
    selectedReporte?.id ?? null, // null clears the chart when nothing is selected
  );

  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        TU PROGRESO
      </h1>

      {/* Chart — data driven by selected report */}
      <BurnoutLineChart
        dataSource={chartData}
        mode="self"
        title={selectedReporte?.nombre}
        loading={chartLoading}
      />

      {chartError && (
        <div className="mt-4 px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {chartError}
        </div>
      )}

      {/* Report list */}
      {listLoading && (
        <div className="flex items-center gap-3 mt-8 text-muted-foreground">
          <Loader2 className="animate-spin w-4 h-4" />
          <span className="text-sm font-sans">Cargando reportes...</span>
        </div>
      )}

      {listError && (
        <div className="mt-8 px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {listError}
        </div>
      )}

      {!listLoading && !listError && reportes.length === 0 && (
        <p className="mt-8 text-sm text-muted-foreground font-sans">
          Aún no has respondido ninguna encuesta.
        </p>
      )}

      {!listLoading && reportes.length > 0 && (
        <ReporteList
          reportes={reportes}
          selectedReporte={selectedReporte ?? undefined}
          onSelectReporte={setSelectedReporte} // ← triggers chart update
        />
      )}
    </div>
  );
}
