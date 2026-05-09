"use client";

import { useState } from "react";
import { ChevronDownIcon, SearchIcon, FilterIcon } from "@/components/icons";

interface Encuesta {
  id: number;
  nombre: string;
  preguntas: string[];
}

const ENCUESTAS: Encuesta[] = [
  {
    id: 1,
    nombre: "Encuesta 1",
    preguntas: Array.from({ length: 11 }, (_, i) => `Pregunta ${i + 1}`),
  },
  {
    id: 2,
    nombre: "Encuesta 2",
    preguntas: [
      "Pregunta A",
      "Pregunta B",
      "Pregunta C",
      "Pregunta D",
      "Pregunta E",
    ],
  },
];

function DropdownOption({ label }: { label: string }) {
  return (
    <button className="w-full flex items-center justify-between px-4 py-3 border border-foreground/30 rounded-lg bg-background text-foreground hover:bg-secondary transition-colors">
      <span>{label}</span>
      <ChevronDownIcon className="w-5 h-5" />
    </button>
  );
}

export function HRCrearEncuesta() {
  const [selected, setSelected] = useState<Encuesta | null>(null);

  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        CREAR ENCUESTA
      </h1>

      {/* Encuestas header */}
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-2xl font-bold text-foreground"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          ENCUESTAS
        </h2>
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
      </div>

      {/* Encuesta grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {ENCUESTAS.map((enc) => (
          <button
            key={enc.id}
            onClick={() => setSelected(enc)}
            className={`p-8 rounded-xl border-2 transition-all text-center ${
              selected?.id === enc.id
                ? "bg-accent border-accent text-foreground"
                : "bg-background border-foreground/30 text-foreground hover:border-primary"
            }`}
          >
            <span className="font-medium text-lg">{enc.nombre}</span>
          </button>
        ))}
      </div>

      {/* Dirigida A */}
      <h2
        className="text-2xl font-bold text-foreground mb-4"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        DIRIGIDA A
      </h2>
      <div className="space-y-3 max-w-2xl">
        <div className="px-4 py-3 border border-foreground/30 rounded-lg bg-background text-foreground">
          Toda la empresa
        </div>
        <DropdownOption label="Área particular" />
        <DropdownOption label="Grupo particular" />
        <DropdownOption label="Trabajador particular" />
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
            <div className="space-y-3 mb-6">
              {selected.preguntas.map((pregunta, i) => (
                <div
                  key={i}
                  className="px-4 py-3 border-2 border-foreground/30 rounded-full text-foreground"
                >
                  {pregunta}
                </div>
              ))}
            </div>
            <button className="w-full bg-accent/50 text-foreground py-3 rounded-lg font-medium hover:bg-accent/70 transition-colors">
              Elegir Encuesta
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
