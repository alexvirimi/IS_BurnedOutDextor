"use client";

import { useEffect, useState } from "react";
import { PowerBIPlaceholder } from "@/components/dashboard/shared/power-bi-placeholder";
import { ReporteList } from "@/components/dashboard/shared/reporte-list";
import type { GroupType } from "../sidebar";

interface Reporte {
  id: number;
  title: string;
  highlighted: boolean;
}

const REPORTES_BY_GROUP: Record<Exclude<GroupType, null>, Reporte[]> = {
  A: [
    { id: 1, title: "Reporte Mensual 2025-2 - Grupo A", highlighted: true },
    {
      id: 2,
      title: "Reporte Seguimiento 2025-1-4 - Grupo A",
      highlighted: false,
    },
    {
      id: 3,
      title: "Reporte Trimestral Q1 2025 - Grupo A",
      highlighted: false,
    },
  ],
  B: [
    { id: 1, title: "Reporte Mensual 2025-2 - Grupo B", highlighted: true },
    {
      id: 2,
      title: "Reporte Seguimiento 2025-1-4 - Grupo B",
      highlighted: false,
    },
    {
      id: 3,
      title: "Análisis de Desempeño 2025 - Grupo B",
      highlighted: false,
    },
    { id: 4, title: "Reporte Anual 2024 - Grupo B", highlighted: false },
  ],
  C: [
    { id: 1, title: "Reporte Mensual 2025-2 - Grupo C", highlighted: true },
    {
      id: 2,
      title: "Reporte Seguimiento 2025-1-4 - Grupo C",
      highlighted: false,
    },
  ],
};

interface PMHistoricosViewProps {
  group: GroupType;
}

export function PMHistoricosView({ group }: PMHistoricosViewProps) {
  const safeGroup = group ?? "A";

  // Reset search when group changes — handled inside ReporteList via key prop
  return (
    <div className="flex-1 p-8 lg:p-12 overflow-auto">
      <div className="max-w-3xl">
        <h1 className="font-heading font-bold text-foreground text-3xl lg:text-4xl uppercase tracking-tight">
          VISUALIZACIÓN
        </h1>
        <PowerBIPlaceholder label={`Power BI - Grupo ${safeGroup}`} />
        <ReporteList
          key={safeGroup}
          reportes={REPORTES_BY_GROUP[safeGroup]}
          title={`REPORTES - GRUPO ${safeGroup}`}
        />
      </div>
    </div>
  );
}
