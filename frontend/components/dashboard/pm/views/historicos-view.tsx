"use client";

import { useState, useEffect } from "react";
import { PowerBIPlaceholder } from "@/components/dashboard/shared/power-bi-placeholder";
import {
  Reporte,
  ReporteList,
} from "@/components/dashboard/shared/reporte-list";

interface PMHistoricosViewProps {
  group: "A" | "B" | "C" | null;
}

const dataByGroup: Record<
  "A" | "B" | "C",
  {
    reportes: Reporte[];
  }
> = {
  A: {
    reportes: [
      {
        id: 1,
        nombre: "Reporte Mensual 2025-2 - Grupo A",
        powerBiTitle: "Dashboard Grupo A - Mayo 2025",
      },
      {
        id: 2,
        nombre: "Reporte Seguimiento 2025-1-4 - Grupo A",
        powerBiTitle: "Seguimiento Grupo A - Semana 4",
      },
    ],
  },
  B: {
    reportes: [
      {
        id: 1,
        nombre: "Reporte Mensual 2025-2 - Grupo B",
        powerBiTitle: "Dashboard Grupo B - Mayo 2025",
      },
      {
        id: 2,
        nombre: "Reporte Seguimiento 2025-1-4 - Grupo B",
        powerBiTitle: "Seguimiento Grupo B - Semana 4",
      },
      {
        id: 3,
        nombre: "Reporte Quincenal 2025-3 - Grupo B",
        powerBiTitle: "Dashboard Grupo B - Quincenal",
      },
    ],
  },
  C: {
    reportes: [
      {
        id: 1,
        nombre: "Reporte Mensual 2025-2 - Grupo C",
        powerBiTitle: "Dashboard Grupo C - Mayo 2025",
      },
      {
        id: 2,
        nombre: "Reporte Seguimiento 2025-1-4 - Grupo C",
        powerBiTitle: "Seguimiento Grupo C - Semana 4",
      },
    ],
  },
};

export function PMHistoricosView({ group }: PMHistoricosViewProps) {
  const safeGroup = group ?? "A";
  const reportes = dataByGroup[safeGroup].reportes;

  // Initialize with the first report of the current group
  const [selectedReporte, setSelectedReporte] = useState<Reporte>(reportes[0]);

  // Reset selection whenever group changes
  useEffect(() => {
    setSelectedReporte(dataByGroup[safeGroup].reportes[0]);
  }, [safeGroup]);

  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        VISUALIZACIÓN
      </h1>

      <PowerBIPlaceholder powerBiTitle={selectedReporte?.powerBiTitle || ""} />

      <ReporteList
        reportes={reportes}
        selectedReporte={selectedReporte}
        onSelectReporte={setSelectedReporte}
        title={`REPORTES - GRUPO ${safeGroup}`}
      />
    </div>
  );
}
