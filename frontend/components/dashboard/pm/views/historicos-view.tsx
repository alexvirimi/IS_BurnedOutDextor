"use client";

import { useState } from "react";

import { PowerBIPlaceholder } from "@/components/dashboard/shared/power-bi-placeholder";
import {
  Reporte,
  ReporteList,
} from "@/components/dashboard/shared/reporte-list";

interface PMHistoricosViewProps {
  type: "areas" | "grupos" | "trabajadores";
}

const dataByType: Record<
  string,
  {
    title: string;
    subtitle: string;
    reportes: Reporte[];
  }
> = {
  areas: {
    title: "VISUALIZACIÓN",
    subtitle: "Áreas",
    reportes: [
      {
        id: 1,
        nombre: "Reporte Mensual 2025-2 - Área de Ventas",
        powerBiTitle: "Dashboard Ventas - Mayo 2025",
      },
      {
        id: 2,
        nombre: "Reporte Seguimiento 2025-1-4 Área de Ventas",
        powerBiTitle: "Seguimiento Ventas - Semana 4",
      },
      {
        id: 3,
        nombre: "Reporte Trimestral 2025-1 - Área de Marketing",
        powerBiTitle: "Dashboard Marketing - Q1 2025",
      },
      {
        id: 4,
        nombre: "Reporte Anual 2024 - Área de Finanzas",
        powerBiTitle: "Dashboard Finanzas - Anual 2024",
      },
    ],
  },

  grupos: {
    title: "VISUALIZACIÓN",
    subtitle: "Grupos",
    reportes: [
      {
        id: 1,
        nombre: "Reporte Mensual 2025-2 - Grupo A",
        powerBiTitle: "Dashboard Grupo A - Mayo 2025",
      },
      {
        id: 2,
        nombre: "Reporte Seguimiento 2025-1-4 - Grupo B",
        powerBiTitle: "Seguimiento Grupo B - Semana 4",
      },
      {
        id: 3,
        nombre: "Reporte Quincenal 2025-3 - Grupo C",
        powerBiTitle: "Dashboard Grupo C - Quincenal",
      },
    ],
  },

  trabajadores: {
    title: "VISUALIZACIÓN",
    subtitle: "Trabajadores",
    reportes: [
      {
        id: 1,
        nombre: "Reporte Individual 2025-2 - Juan Pérez",
        powerBiTitle: "Dashboard Juan Pérez - Mayo 2025",
      },
      {
        id: 2,
        nombre: "Reporte Individual 2025-1-4 - María García",
        powerBiTitle: "Dashboard María García - Semana 4",
      },
      {
        id: 3,
        nombre: "Reporte Individual 2025-1-3 - Carlos López",
        powerBiTitle: "Dashboard Carlos López - Semana 3",
      },
      {
        id: 4,
        nombre: "Reporte Individual 2025-1-2 - Ana Martínez",
        powerBiTitle: "Dashboard Ana Martínez - Semana 2",
      },
      {
        id: 5,
        nombre: "Reporte Individual 2025-1-1 - Roberto Sánchez",
        powerBiTitle: "Dashboard Roberto Sánchez - Semana 1",
      },
    ],
  },
};

export function PMHistoricosView({ type }: PMHistoricosViewProps) {
  const data = dataByType[type];

  const reportes = data.reportes;

  // ✅ SIEMPRE derivado del tipo actual
  const [selectedReporte, setSelectedReporte] = useState<Reporte>(
    () => reportes[0],
  );

  // 🔥 FIX CLAVE: cuando cambia el type, reinicia el estado
  useState(() => {
    setSelectedReporte(reportes[0]);
  });

  const selected = selectedReporte ?? reportes[0];

  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        {data.title}
      </h1>

      <PowerBIPlaceholder powerBiTitle={selected?.powerBiTitle || ""} />

      <ReporteList
        reportes={reportes}
        selectedReporte={selected}
        onSelectReporte={setSelectedReporte}
        title={`REPORTES - ${data.subtitle}`}
      />
    </div>
  );
}
