"use client"

import { Filter, Search } from "lucide-react"
import { DownloadIcon } from "../icons/DownloadIcon"

export default function MiProgreso() {
  const reportes = [
    { id: 1, nombre: "Reporte Mensual 2025-2", highlighted: true },
    { id: 2, nombre: "Reporte Seguimiento 2025-1-4", highlighted: false },
  ]

  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold text-foreground mb-8" style={{ fontFamily: 'var(--font-heading)' }}>
        TU PROGRESO
      </h1>

      {/* Power BI Placeholder */}
      <div className="bg-gray-200 rounded-xl h-[400px] flex items-center justify-center mb-8">
        <span className="text-foreground font-medium text-lg">Power BI</span>
      </div>

      {/* Reportes Section */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-foreground" style={{ fontFamily: 'var(--font-heading)' }}>
          REPORTES
        </h2>
        <div className="flex items-center gap-2">
          <button className="p-2 border border-foreground/30 rounded-lg hover:bg-secondary transition-colors">
            <Filter size={20} className="text-foreground" />
          </button>
          <div className="relative">
            <Search size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Buscar"
              className="pl-10 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="space-y-3">
        {reportes.map((reporte) => (
          <div
            key={reporte.id}
            className={`flex items-center justify-between px-4 py-3 rounded-lg ${
              reporte.highlighted
                ? "bg-accent text-foreground"
                : "bg-background border border-foreground/30"
            }`}
          >
            <span className="font-medium text-foreground">
              {reporte.nombre}
            </span>
            <button className="p-2 hover:bg-secondary/20 rounded transition-colors">
              <DownloadIcon className="text-foreground" />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
