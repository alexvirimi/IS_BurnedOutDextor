"use client";

import { useState } from "react";
import { DownloadIcon, FilterIcon, SearchIcon } from "@/components/icons";

interface Reporte {
  id: number;
  title: string;
  highlighted: boolean;
}

interface ReporteListProps {
  reportes: Reporte[];
  title?: string;
}

export function ReporteList({
  reportes,
  title = "REPORTES",
}: ReporteListProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = reportes.filter((r) =>
    r.title.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4 gap-4">
        <h2 className="font-heading font-bold text-foreground text-xl uppercase">
          {title}
        </h2>
        <div className="flex items-center gap-2">
          <button className="p-2 border border-border rounded-lg hover:bg-muted transition-colors">
            <FilterIcon className="w-4 h-4 text-foreground" />
          </button>
          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Buscar"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-48 pl-10 pr-4 py-2 bg-background border border-border rounded-lg font-sans text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {filtered.map((reporte) => (
          <div
            key={reporte.id}
            className={`flex items-center justify-between px-6 py-4 rounded-lg border ${
              reporte.highlighted
                ? "bg-secondary border-secondary"
                : "bg-background border-border"
            }`}
          >
            <span
              className={`font-sans text-sm ${
                reporte.highlighted
                  ? "text-secondary-foreground font-medium"
                  : "text-foreground"
              }`}
            >
              {reporte.title}
            </span>
            <button className="p-2 hover:bg-muted rounded-lg transition-colors">
              <DownloadIcon className="w-4 h-4 text-foreground" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
