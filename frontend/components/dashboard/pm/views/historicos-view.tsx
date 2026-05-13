"use client";

/**
 * PMHistoricosView — UPDATED
 * ───────────────────────────
 * PM sees their own group's aggregated burnout data.
 * Chart updates when a report is selected from the list.
 *
 * Key change: useBurnoutChart with scope { type: "group", groupId } from session.
 */

import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import { BurnoutLineChart } from "@/components/dashboard/shared/burnout-line-chart";
import { ReporteList } from "@/components/dashboard/shared/reporte-list";
import { useHistoricoReportsPM } from "@/hooks/useReportes";
import { useBurnoutChart } from "@/hooks/useBurnoutChart";
import { useAuth } from "@/lib/auth/context";
import type { Reporte } from "@/hooks/useReportes";

interface PMHistoricosViewProps {
  group: "A" | "B" | "C" | null;
}

export function PMHistoricosView({ group }: PMHistoricosViewProps) {
  const { session } = useAuth();
  const groupId = session?.id_group ?? null;

  const {
    reportes,
    loading: listLoading,
    error: listError,
  } = useHistoricoReportsPM();

  const [selectedReporte, setSelectedReporte] = useState<Reporte | null>(null);

  useEffect(() => {
    setSelectedReporte(reportes.length > 0 ? reportes[0] : null);
  }, [reportes]);

  // Group aggregated chart — scope is always the PM's own group
  const {
    data: chartData,
    loading: chartLoading,
    error: chartError,
  } = useBurnoutChart(
    groupId ? { type: "group", groupId } : { type: "self" },
    // Use selectedReporte.id as the trigger; null when nothing selected yet
    groupId ? (selectedReporte?.id ?? null) : null,
  );

  return (
    <div className="p-8 max-w-5xl">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        VISUALIZACIÓN
      </h1>

      <BurnoutLineChart
        dataSource={chartData}
        mode="group"
        title={selectedReporte?.nombre}
        loading={chartLoading}
      />

      {chartError && (
        <div className="mt-4 px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {chartError}
        </div>
      )}

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
          No hay encuestas completadas por todos los miembros de tu grupo.
        </p>
      )}

      {!listLoading && reportes.length > 0 && (
        <ReporteList
          reportes={reportes}
          selectedReporte={selectedReporte ?? undefined}
          onSelectReporte={setSelectedReporte}
          title="REPORTES - MI GRUPO"
        />
      )}
    </div>
  );
}
