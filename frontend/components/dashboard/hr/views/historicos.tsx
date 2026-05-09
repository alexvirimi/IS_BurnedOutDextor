"use client";

import { useState, useEffect } from "react";
import { PowerBIPlaceholder } from "@/components/dashboard/shared/power-bi-placeholder";
import { ReporteList } from "@/components/dashboard/shared/reporte-list";

type HistoricoType = "areas" | "grupos" | "trabajadores";

interface Reporte {
  id: number;
  title: string;
  highlighted: boolean;
}

const REPORTES_BY_TYPE: Record<HistoricoType, Reporte[]> = {
  areas: [
    {
      id: 1,
      title: "Reporte Mensual 2025-2 - Área de Ventas",
      highlighted: true,
    },
    {
      id: 2,
      title: "Reporte Seguimiento 2025-1-4 Área de Ventas",
      highlighted: false,
    },
    {
      id: 3,
      title: "Reporte Trimestral 2025-1 - Área de Marketing",
      highlighted: false,
    },
    {
      id: 4,
      title: "Reporte Anual 2024 - Área de Finanzas",
      highlighted: false,
    },
  ],
  grupos: [
    { id: 1, title: "Reporte Mensual 2025-2 - Grupo A", highlighted: true },
    {
      id: 2,
      title: "Reporte Seguimiento 2025-1-4 - Grupo B",
      highlighted: false,
    },
    { id: 3, title: "Reporte Quincenal 2025-3 - Grupo C", highlighted: false },
  ],
  trabajadores: [
    {
      id: 1,
      title: "Reporte Individual 2025-2 - Juan Pérez",
      highlighted: true,
    },
    {
      id: 2,
      title: "Reporte Individual 2025-1-4 - María García",
      highlighted: false,
    },
    {
      id: 3,
      title: "Reporte Individual 2025-1-3 - Carlos López",
      highlighted: false,
    },
    {
      id: 4,
      title: "Reporte Individual 2025-1-2 - Ana Martínez",
      highlighted: false,
    },
    {
      id: 5,
      title: "Reporte Individual 2025-1-1 - Roberto Sánchez",
      highlighted: false,
    },
  ],
};

const SUBTITLES: Record<HistoricoType, string> = {
  areas: "Áreas",
  grupos: "Grupos",
  trabajadores: "Trabajadores",
};

interface HRHistoricosProps {
  type: HistoricoType;
}

export function HRHistoricos({ type }: HRHistoricosProps) {
  const reportes = REPORTES_BY_TYPE[type];

  // Initialize with the first report of the current type
  const [selectedReporte, setSelectedReporte] = useState<Reporte>(reportes[0]);

  // Reset selection whenever type changes
  useEffect(() => {
    setSelectedReporte(REPORTES_BY_TYPE[type][0]);
  }, [type]);

  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        VISUALIZACIÓN
      </h1>
      <PowerBIPlaceholder label={`Power BI · ${SUBTITLES[type]}`} powerBiTitle={selectedReporte.title} />
      <ReporteList
        reportes={reportes}
        selectedReporte={selectedReporte}
        onSelectReporte={(reporte) => {
          const selected = reportes.find((item) => item.id === reporte.id);
          if (selected) setSelectedReporte(selected);
        }}
        title={`REPORTES · ${SUBTITLES[type].toUpperCase()}`}
      />
    </div>
  );
}