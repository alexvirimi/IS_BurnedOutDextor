"use client"

import { useState } from "react"
import { Filter, Search, ChevronDown, X } from "lucide-react"

interface Encuesta {
  id: number
  nombre: string
  preguntas: string[]
}

const encuestasData: Encuesta[] = [
  {
    id: 1,
    nombre: "Encuesta 1",
    preguntas: [
      "Pregunta 1",
      "Pregunta 2",
      "Pregunta 3",
      "Pregunta 4",
      "Pregunta 5",
      "Pregunta 6",
      "Pregunta 7",
      "Pregunta 8",
      "Pregunta 9",
      "Pregunta 10",
      "Pregunta 11",
    ],
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
]

export default function CrearEncuesta() {
  const [selectedEncuesta, setSelectedEncuesta] = useState<Encuesta | null>(null)
  const [showModal, setShowModal] = useState(false)

  const handleSelectEncuesta = (encuesta: Encuesta) => {
    setSelectedEncuesta(encuesta)
    setShowModal(true)
  }

  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold text-foreground mb-8" style={{ fontFamily: 'var(--font-heading)' }}>
        CREAR ENCUESTA
      </h1>

      {/* Encuestas Section */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-foreground" style={{ fontFamily: 'var(--font-heading)' }}>
          ENCUESTAS
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

      {/* Encuestas Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {encuestasData.map((encuesta) => (
          <button
            key={encuesta.id}
            onClick={() => handleSelectEncuesta(encuesta)}
            className={`p-8 rounded-xl border-2 transition-all text-center ${
              selectedEncuesta?.id === encuesta.id
                ? "bg-accent border-accent text-foreground"
                : "bg-background border-foreground/30 text-foreground hover:border-primary"
            }`}
          >
            <span className="font-medium text-lg">{encuesta.nombre}</span>
          </button>
        ))}
      </div>

      {/* Dirigida A Section */}
      <h2 className="text-2xl font-bold text-foreground mb-4" style={{ fontFamily: 'var(--font-heading)' }}>
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
      {showModal && selectedEncuesta && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto relative">
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <X size={18} />
            </button>

            <h2 className="text-2xl font-bold text-foreground mb-6" style={{ fontFamily: 'var(--font-heading)' }}>
              {selectedEncuesta.nombre.toUpperCase()}
            </h2>

            <div className="space-y-3 mb-6">
              {selectedEncuesta.preguntas.map((pregunta, index) => (
                <div
                  key={index}
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
  )
}

function DropdownOption({ label }: { label: string }) {
  return (
    <button className="w-full flex items-center justify-between px-4 py-3 border border-foreground/30 rounded-lg bg-background text-foreground hover:bg-secondary transition-colors">
      <span>{label}</span>
      <ChevronDown size={20} />
    </button>
  )
}
