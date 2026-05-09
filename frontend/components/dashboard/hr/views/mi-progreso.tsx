"use client";

import { PowerBIPlaceholder } from "@/components/dashboard/shared/power-bi-placeholder";
import { ReporteList } from "@/components/dashboard/shared/reporte-list";

const REPORTES = [
  { id: 1, title: "Reporte Mensual 2025-2", highlighted: true },
  { id: 2, title: "Reporte Seguimiento 2025-1-4", highlighted: false },
];

export function HRMiProgreso() {
  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        TU PROGRESO
      </h1>
      <PowerBIPlaceholder />
      <ReporteList reportes={REPORTES} />
    </div>
  );
}
