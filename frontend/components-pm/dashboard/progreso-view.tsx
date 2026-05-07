"use client"

import { useState } from "react"
import { DownloadIcon, MicrosoftIcon, SearchIcon, FilterIcon } from "@/components/icons"

const reportes = [
  { id: 1, title: "Reporte Mensual 2025-2", highlighted: true },
  { id: 2, title: "Reporte Seguimiento 2025-1-4", highlighted: false },
]

export function ProgresoView() {
  const [searchQuery, setSearchQuery] = useState("")

  const filteredReportes = reportes.filter((reporte) =>
    reporte.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="flex-1 p-8 lg:p-12 overflow-auto">
      <div className="max-w-3xl">
        {/* Title */}
        <h1 className="font-heading font-bold text-foreground text-3xl lg:text-4xl uppercase tracking-tight">
          TU PROGRESO
        </h1>

        {/* Power BI Embed Placeholder */}
        <div className="mt-6 bg-muted rounded-lg aspect-video flex items-center justify-center">
          <div className="flex items-center gap-2 text-muted-foreground">
            <MicrosoftIcon className="w-5 h-5" />
            <span className="font-sans font-medium">Power BI</span>
          </div>
        </div>

        {/* Reports Section */}
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4 gap-4">
            <h2 className="font-heading font-bold text-foreground text-xl uppercase">
              REPORTES
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

          {/* Reports List */}
          <div className="flex flex-col gap-3">
            {filteredReportes.map((reporte) => (
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
      </div>
    </div>
  )
}
