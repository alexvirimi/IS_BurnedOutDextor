"use client";

import { useState } from "react";
import { PowerBIPlaceholder } from "@/components/dashboard/shared/power-bi-placeholder";
import {
  ReporteList,
  type Reporte,
} from "@/components/dashboard/shared/reporte-list";

const REPORTES: Reporte[] = [
  {
    id: 1,
    nombre: "Reporte Mensual 2025-2",
    powerBiTitle: "Dashboard Mensual - Mayo 2025",
  },
  {
    id: 2,
    nombre: "Reporte Seguimiento 2025-1-4",
    powerBiTitle: "Seguimiento Semana 4 - Enero 2025",
  },
];

export function WKRProgresoView() {
  const [selectedReporte, setSelectedReporte] = useState<Reporte>(REPORTES[0]);

  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        TU PROGRESO
      </h1>

      <PowerBIPlaceholder powerBiTitle={selectedReporte.powerBiTitle || ""} />

      <ReporteList
        reportes={REPORTES}
        selectedReporte={selectedReporte}
        onSelectReporte={setSelectedReporte}
      />
    </div>
  );
}
