"use client";

import { useState } from "react";
import { DownloadIcon, FilterIcon, SearchIcon } from "@/components/icons";
import { BUTTONS_COLORS } from "@/lib/styles/buttons-colors";
// Single source of truth — Reporte is defined in useReportes and re-exported
// here so consumers can import from either location without a type mismatch.
export type { Reporte } from "@/hooks/useReportes";
import type { Reporte } from "@/hooks/useReportes";

const C = BUTTONS_COLORS.hr;

interface ReporteListProps {
  reportes: Reporte[];
  selectedReporte?: Reporte;
  onSelectReporte?: (reporte: Reporte) => void;
  title?: string;
  onDownload?: (reporte: Reporte) => void;
}

export function ReporteList({
  reportes,
  selectedReporte,
  onSelectReporte,
  onDownload,
  title = "REPORTES",
}: ReporteListProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = reportes.filter((r) => {
    const reporteName = r.nombre;
    return reporteName.toLowerCase().includes(searchQuery.toLowerCase());
  });

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4 gap-4">
        <h2 className="font-heading font-bold text-foreground text-xl uppercase">
          {title}
        </h2>

        <div className="flex items-center gap-2">
          <button className="p-2 border border-foreground/30 rounded-lg hover:bg-secondary transition-colors">
            <FilterIcon className="w-4 h-4 text-foreground" />
          </button>

          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Buscar"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-48 pl-10 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>
      </div>

      {filtered.length === 0 && (
        <p className="text-sm text-muted-foreground font-sans">
          {searchQuery
            ? "No se encontraron reportes con ese nombre."
            : "No hay reportes disponibles."}
        </p>
      )}

      <div className="space-y-3">
        {filtered.map((reporte) => {
          const isSelected = selectedReporte?.id === reporte.id;
          const reporteName = reporte.nombre;

          return (
            <button
              key={reporte.id}
              onClick={() => onSelectReporte?.(reporte)}
              className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors ${
                isSelected
                  ? `${C.button}`
                  : "border border-foreground/30 hover:bg-secondary"
              }`}
            >
              <span
                className={`font-medium text-sm text-left ${
                  isSelected ? "text-white" : "text-foreground"
                }`}
              >
                {reporteName}
              </span>

              <div
                onClick={(e) => {
                  e.stopPropagation();
                  onDownload?.(reporte);
                }}
                className="p-2 hover:bg-secondary/20 rounded transition-colors flex-shrink-0"
              >
                <DownloadIcon className="w-4 h-4 text-foreground" />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
