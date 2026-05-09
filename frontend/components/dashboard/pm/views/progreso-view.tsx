"use client";

import { PowerBIPlaceholder } from "@/components/dashboard/shared/power-bi-placeholder";
import { ReporteList } from "@/components/dashboard/shared/reporte-list";

const REPORTES = [
  { id: 1, title: "Reporte Mensual 2025-2", highlighted: true },
  { id: 2, title: "Reporte Seguimiento 2025-1-4", highlighted: false },
];

export function PMProgresoView() {
  return (
    <div className="flex-1 p-8 lg:p-12 overflow-auto">
      <div className="max-w-3xl">
        <h1 className="font-heading font-bold text-foreground text-3xl lg:text-4xl uppercase tracking-tight">
          TU PROGRESO
        </h1>
        <PowerBIPlaceholder />
        <ReporteList reportes={REPORTES} />
      </div>
    </div>
  );
}
