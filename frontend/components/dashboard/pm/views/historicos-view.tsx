"use client";

import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import { BurnoutLineChart } from "@/components/dashboard/shared/burnout-line-chart";
import { ReporteList } from "@/components/dashboard/shared/reporte-list";
import { useHistoricoReportsPM } from "@/hooks/useReportes";
import type { Reporte } from "@/hooks/useReportes";

// GroupType kept for prop compatibility with PMDashboard/PMSidebar
interface PMHistoricosViewProps {
  group: "A" | "B" | "C" | null;
}

export function PMHistoricosView({ group }: PMHistoricosViewProps) {
  // The `group` prop is kept for sidebar compatibility but the actual
  // group ID comes from the auth token inside useHistoricoReportsPM.
  // PM leaders only ever see their own group.
  const { reportes, loading, error } = useHistoricoReportsPM();
  const [selectedReporte, setSelectedReporte] = useState<Reporte | null>(null);

  useEffect(() => {
    setSelectedReporte(reportes.length > 0 ? reportes[0] : null);
  }, [reportes]);

  return (
    <div className="p-8 max-w-5xl">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        VISUALIZACIÓN
      </h1>

      <BurnoutLineChart title={selectedReporte?.nombre} />

      {loading && (
        <div className="flex items-center gap-3 mt-8 text-muted-foreground">
          <Loader2 className="animate-spin w-4 h-4" />
          <span className="text-sm font-sans">Cargando reportes...</span>
        </div>
      )}

      {error && (
        <div className="mt-8 px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {error}
        </div>
      )}

      {!loading && !error && reportes.length === 0 && (
        <p className="mt-8 text-sm text-muted-foreground font-sans">
          No hay encuestas completadas por todos los miembros de tu grupo.
        </p>
      )}

      {!loading && reportes.length > 0 && (
        <ReporteList
          reportes={reportes}
          selectedReporte={selectedReporte ?? undefined}
          onSelectReporte={(r) => setSelectedReporte(r)}
          title="REPORTES - MI GRUPO"
        />
      )}
    </div>
  );
}
