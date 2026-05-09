"use client";

import { useState } from "react";
import { SearchIcon, FilterIcon } from "@/components/icons";

interface EncuestaActiva {
  id: number;
  nombre: string;
  respuestas: number;
}

interface EncuestaInactiva {
  id: number;
  nombre: string;
}

const ENCUESTAS_ACTIVAS: EncuestaActiva[] = [
  { id: 1, nombre: "Encuesta de seguimiento 2026-4-2", respuestas: 1234 },
  { id: 2, nombre: "Encuesta mensual 2026-4", respuestas: 1234 },
  {
    id: 3,
    nombre: "Encuesta de seguimiento 2026-4 - Grupo A",
    respuestas: 1234,
  },
];

const ENCUESTAS_INACTIVAS: EncuestaInactiva[] = [
  { id: 1, nombre: "Encuesta inactiva" },
];

function SearchBar() {
  return (
    <div className="flex items-center gap-2">
      <button className="p-2 border border-foreground/30 rounded-lg hover:bg-secondary transition-colors">
        <FilterIcon className="w-5 h-5 text-foreground" />
      </button>
      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <input
          type="text"
          placeholder="Buscar"
          className="pl-10 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>
    </div>
  );
}

export function HRModificarEncuestas() {
  const [selected, setSelected] = useState<EncuestaActiva | null>(null);

  return (
    <div className="p-8">
      {/* Activas */}
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-2xl font-bold text-foreground"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          ENCUESTAS
        </h2>
        <SearchBar />
      </div>

      <div className="space-y-3 mb-10">
        {ENCUESTAS_ACTIVAS.map((enc) => (
          <button
            key={enc.id}
            onClick={() => setSelected(enc)}
            className="w-full text-left px-4 py-3 border border-foreground/30 rounded-lg bg-background text-foreground hover:bg-secondary transition-colors"
          >
            {enc.nombre}
          </button>
        ))}
      </div>

      {/* Inactivas */}
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-2xl font-bold text-foreground"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          ENCUESTAS INACTIVAS
        </h2>
        <SearchBar />
      </div>

      <div className="space-y-3">
        {ENCUESTAS_INACTIVAS.map((enc) => (
          <div
            key={enc.id}
            className="px-4 py-3 rounded-lg bg-accent text-foreground"
          >
            {enc.nombre}
          </div>
        ))}
      </div>

      {/* Modal */}
      {selected && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto relative">
            <button
              onClick={() => setSelected(null)}
              className="absolute top-4 right-4 w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              ✕
            </button>
            <h2
              className="text-2xl font-bold text-foreground mb-6"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              {selected.nombre.toUpperCase()}
            </h2>
            <div className="space-y-3">
              {Array.from({ length: 11 }, (_, i) => (
                <div
                  key={i}
                  className="px-4 py-3 border-2 border-foreground/30 rounded-full text-foreground"
                >
                  Pregunta {i + 1} · {selected.respuestas} respuestas
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
