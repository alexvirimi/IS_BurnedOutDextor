"use client";

import { useState } from "react";
import { Filter, Search, X, Trash2 } from "lucide-react";
import { BUTTONS_COLORS } from "@/lib/styles/buttons-colors";

// Main view buttons → hr palette (#8795C7)
const C = BUTTONS_COLORS.hr;
// Modal buttons → hrModal palette (#E0D7F9)
const M = BUTTONS_COLORS.hrModal;

interface EncuestaActiva {
  id: number;
  nombre: string;
  respuestas: number;
}

interface EncuestaInactiva {
  id: number;
  nombre: string;
}

export function HRModificarEncuestas() {
  const [encuestasActivas, setEncuestasActivas] = useState<EncuestaActiva[]>([
    { id: 1, nombre: "Encuesta de seguimiento 2026-4-2", respuestas: 1234 },
    { id: 2, nombre: "Encuesta mensual 2026-4", respuestas: 1234 },
    {
      id: 3,
      nombre: "Encuesta de seguimiento 2026-4 - Grupo A",
      respuestas: 1234,
    },
  ]);

  const [encuestasInactivas, setEncuestasInactivas] = useState<
    EncuestaInactiva[]
  >([]);
  const [selectedEncuesta, setSelectedEncuesta] =
    useState<EncuestaActiva | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [encuestaToDelete, setEncuestaToDelete] =
    useState<EncuestaActiva | null>(null);

  const handleSelectEncuesta = (encuesta: EncuestaActiva) => {
    setSelectedEncuesta(encuesta);
    setShowModal(true);
  };

  const handleDeleteClick = (e: React.MouseEvent, encuesta: EncuestaActiva) => {
    e.stopPropagation();
    setEncuestaToDelete(encuesta);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = () => {
    if (encuestaToDelete) {
      setEncuestasInactivas([
        ...encuestasInactivas,
        { id: encuestaToDelete.id, nombre: encuestaToDelete.nombre },
      ]);
      setEncuestasActivas(
        encuestasActivas.filter((e) => e.id !== encuestaToDelete.id),
      );
      setShowDeleteModal(false);
      setEncuestaToDelete(null);
    }
  };

  return (
    <div className="p-8">
      {/* ── Encuestas activas ─────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-2xl font-bold text-foreground"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          ENCUESTAS
        </h2>
        <div className="flex items-center gap-2">
          {/* Filter button — hr palette */}
          <button className={`p-2 rounded-lg transition-colors ${C.button}`}>
            <Filter size={20} />
          </button>
          <div className="relative">
            <Search
              size={20}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <input
              type="text"
              placeholder="Buscar"
              className="pl-10 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>
      </div>

      {/* Encuesta list — hr palette */}
      <div className="space-y-3 mb-10">
        {encuestasActivas.map((encuesta) => (
          <div key={encuesta.id} className="flex items-center gap-2">
            <button
              onClick={() => handleSelectEncuesta(encuesta)}
              className={`flex-1 text-left px-4 py-3 rounded-lg transition-colors ${C.listItem}`}
            >
              {encuesta.nombre}
            </button>
            {/* Delete — destructive, intentionally kept red for clarity */}
            <button
              onClick={(e) => handleDeleteClick(e, encuesta)}
              className="p-3 border border-red-300 rounded-lg bg-background text-red-500 hover:bg-red-50 transition-colors"
              title="Eliminar encuesta"
            >
              <Trash2 size={20} />
            </button>
          </div>
        ))}
      </div>

      {/* ── Encuestas inactivas ───────────────────────────────────── */}
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-2xl font-bold text-foreground"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          ENCUESTAS INACTIVAS
        </h2>
        <div className="flex items-center gap-2">
          <button className={`p-2 rounded-lg transition-colors ${C.button}`}>
            <Filter size={20} />
          </button>
          <div className="relative">
            <Search
              size={20}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <input
              type="text"
              placeholder="Buscar"
              className="pl-10 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {encuestasInactivas.map((encuesta) => (
          <div
            key={encuesta.id}
            className="px-4 py-3 rounded-lg bg-accent text-foreground"
          >
            {encuesta.nombre}
          </div>
        ))}
      </div>

      {/* ── View modal ────────────────────────────────────────────── */}
      {showModal && selectedEncuesta && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto relative">
            {/* Modal close — hrModal palette */}
            <button
              onClick={() => setShowModal(false)}
              className={`absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center transition-colors ${M.button}`}
            >
              <X size={18} />
            </button>

            <h2
              className="text-2xl font-bold text-foreground mb-6"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              {selectedEncuesta.nombre.toUpperCase()}
            </h2>

            <div className="space-y-3">
              {Array.from({ length: 11 }, (_, i) => (
                <div
                  key={i}
                  className="px-4 py-3 border-2 border-foreground/30 rounded-full text-foreground"
                >
                  Pregunta {i + 1} · {selectedEncuesta.respuestas} respuestas
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Delete confirmation modal ─────────────────────────────── */}
      {showDeleteModal && encuestaToDelete && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-xl p-6 w-full max-w-md relative">
            {/* Modal close — hrModal palette */}
            <button
              onClick={() => {
                setShowDeleteModal(false);
                setEncuestaToDelete(null);
              }}
              className={`absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center transition-colors ${M.button}`}
            >
              <X size={18} />
            </button>

            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Trash2 size={32} className="text-red-500" />
              </div>

              <h2
                className="text-xl font-bold text-foreground mb-2"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                ELIMINAR ENCUESTA
              </h2>

              <p className="text-muted-foreground mb-6">
                ¿Estás seguro de que deseas eliminar la encuesta{" "}
                <strong className="text-foreground">
                  {encuestaToDelete.nombre}
                </strong>
                ? Esta acción moverá la encuesta a inactivas.
              </p>

              <div className="flex gap-3">
                {/* Cancel — hrModal palette */}
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setEncuestaToDelete(null);
                  }}
                  className={`flex-1 py-3 rounded-lg font-medium transition-colors ${M.button}`}
                >
                  Cancelar
                </button>
                {/* Destructive confirm — intentionally kept red */}
                <button
                  onClick={handleConfirmDelete}
                  className="flex-1 py-3 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
