"use client";

import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import { PowerBIPlaceholder } from "@/components/dashboard/shared/power-bi-placeholder";
import { ReporteList } from "@/components/dashboard/shared/reporte-list";
import { useMyProgressReports } from "@/hooks/useReportes";
import type { Reporte } from "@/hooks/useReportes";

export function WKRProgresoView() {
  const { reportes, loading, error } = useMyProgressReports();
  const [selectedReporte, setSelectedReporte] = useState<Reporte | null>(null);

  useEffect(() => {
    if (reportes.length > 0 && !selectedReporte) {
      setSelectedReporte(reportes[0]);
    }
  }, [reportes]);

  return (
    <div className="p-8 max-w-5xl">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        TU PROGRESO
      </h1>

      <PowerBIPlaceholder powerBiTitle={selectedReporte?.nombre ?? ""} />

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
          Aún no has respondido ninguna encuesta.
        </p>
      )}

      {!loading && reportes.length > 0 && (
        <ReporteList
          reportes={reportes}
          selectedReporte={selectedReporte ?? undefined}
          onSelectReporte={(r) => setSelectedReporte(r)}
        />
      )}
    </div>
  );
}
