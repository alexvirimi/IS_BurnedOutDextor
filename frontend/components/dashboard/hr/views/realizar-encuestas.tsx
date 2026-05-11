"use client";

import { useEffect } from "react";
import { X, ChevronLeft, ChevronRight, Check, Loader2 } from "lucide-react";
import { BUTTONS_COLORS } from "@/lib/styles/buttons-colors";
import { useEncuestas } from "@/hooks/useEncuestas";

const C = BUTTONS_COLORS.pm;

interface HRRealizarEncuestasViewProps {
  userName: string;
}

export function HRRealizarEncuestasView({
  userName,
}: HRRealizarEncuestasViewProps) {
  const {
    encuestas,
    loadingList,
    listError,
    loadEncuestas,
    selectedEncuesta,
    loadingQuestions,
    questionsError,
    handleSelectEncuesta,
    currentQuestion,
    currentPregunta,
    currentRespuesta,
    showCompletado,
    handleRespuesta,
    handleNext,
    handlePrev,
    handleClose,
  } = useEncuestas();

  useEffect(() => {
    loadEncuestas();
  }, [loadEncuestas]);

  return (
    <div className="flex-1 p-8 lg:p-12 overflow-auto">
      <div className="max-w-3xl">
        <h1 className="font-heading font-bold text-foreground text-3xl lg:text-4xl uppercase tracking-tight">
          {userName}, QUE LINDO VOLVER A VERTE
        </h1>

        <p className="font-sans text-foreground text-lg mt-6 leading-relaxed">
          Esta semana te esforzaste tanto que necesitas un respiro de tu
          ámbiente laboral.
        </p>
        <p className="text-foreground text-lg mb-12">Respira con nosotros.</p>

        {/* ── Survey list ─────────────────────────────────────────────── */}
        {loadingList ? (
          <div className="flex items-center gap-3 text-muted-foreground">
            <Loader2 size={18} className="animate-spin" />
            <span className="font-sans text-sm">Cargando encuestas...</span>
          </div>
        ) : listError ? (
          <div className="px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
            {listError}
          </div>
        ) : encuestas.length === 0 ? (
          <p className="text-muted-foreground font-sans text-sm">
            No tienes encuestas asignadas.
          </p>
        ) : (
          <div className="space-y-3 max-w-3xl">
            {encuestas.map((encuesta) => (
              <button
                key={encuesta.id}
                onClick={() => handleSelectEncuesta(encuesta)}
                disabled={encuesta.already_responded}
                className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                  encuesta.already_responded
                    ? "bg-secondary text-muted-foreground cursor-not-allowed opacity-60"
                    : `${C.listItem}`
                }`}
              >
                <span>{encuesta.nombre}</span>
                {encuesta.already_responded && (
                  <span className="ml-2 text-xs font-sans">✓ Completada</span>
                )}
              </button>
            ))}
          </div>
        )}

        {/* ── Error fetching questions ─────────────────────────────────── */}
        {questionsError && (
          <div className="mt-4 px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
            {questionsError}
          </div>
        )}

        {/* ── Survey modal ─────────────────────────────────────────────── */}
        {selectedEncuesta && !showCompletado && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-background rounded-xl p-6 w-full max-w-2xl relative">
              <button
                onClick={handleClose}
                className={`absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center transition-colors ${C.button}`}
              >
                <X size={18} />
              </button>

              <h2
                className="text-2xl font-bold text-foreground mb-2"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                {selectedEncuesta.nombre.toUpperCase()}
              </h2>

              {/* Loading questions */}
              {loadingQuestions ? (
                <div className="flex items-center justify-center gap-3 py-16 text-muted-foreground">
                  <Loader2 size={20} className="animate-spin" />
                  <span className="font-sans text-sm">
                    Cargando preguntas...
                  </span>
                </div>
              ) : (
                <>
                  <p className="text-muted-foreground mb-8">
                    Pregunta {currentQuestion + 1} de{" "}
                    {selectedEncuesta.preguntas.length}
                  </p>

                  {/* Progress bar */}
                  <div className="w-full h-2 bg-secondary rounded-full mb-8">
                    <div
                      className="h-full bg-primary rounded-full transition-all duration-300"
                      style={{
                        width:
                          selectedEncuesta.preguntas.length > 0
                            ? `${((currentQuestion + 1) / selectedEncuesta.preguntas.length) * 100}%`
                            : "0%",
                      }}
                    />
                  </div>

                  {/* Question */}
                  <div className="mb-8">
                    <p className="text-foreground text-lg mb-6">
                      {currentPregunta?.texto}
                    </p>

                    {/* Scale options — all questions are escala */}
                    <div className="flex justify-between gap-2">
                      {[1, 2, 3, 4, 5].map((value) => (
                        <button
                          key={value}
                          onClick={() => handleRespuesta(value)}
                          className={`flex-1 py-4 rounded-lg border-2 transition-all ${
                            currentRespuesta === value
                              ? `${C.buttonActive} border-2`
                              : "border-foreground/30 text-foreground hover:border-primary"
                          }`}
                        >
                          {value}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex justify-between text-sm text-muted-foreground mb-8">
                    <span>Muy en desacuerdo</span>
                    <span>Muy de acuerdo</span>
                  </div>

                  {/* Navigation */}
                  <div className="flex justify-between">
                    <button
                      onClick={handlePrev}
                      disabled={currentQuestion === 0}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                        currentQuestion === 0
                          ? "text-muted-foreground cursor-not-allowed"
                          : `${C.button}`
                      }`}
                    >
                      <ChevronLeft size={20} />
                      Anterior
                    </button>
                    <button
                      onClick={handleNext}
                      disabled={currentRespuesta === undefined}
                      className={`flex items-center gap-2 px-6 py-2 rounded-lg transition-colors ${
                        currentRespuesta === undefined
                          ? "bg-secondary text-muted-foreground cursor-not-allowed"
                          : `${C.button}`
                      }`}
                    >
                      {currentQuestion === selectedEncuesta.preguntas.length - 1
                        ? "Finalizar"
                        : "Siguiente"}
                      <ChevronRight size={20} />
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* ── Completion modal ─────────────────────────────────────────── */}
        {showCompletado && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-background rounded-xl p-8 w-full max-w-md text-center">
              <div
                className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 ${C.button}`}
              >
                <Check size={32} />
              </div>
              <h2
                className="text-2xl font-bold text-foreground mb-4"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                ENCUESTA COMPLETADA
              </h2>
              <p className="text-muted-foreground mb-6">
                Gracias por tomarte el tiempo de responder. Tus respuestas nos
                ayudan a mejorar tu experiencia laboral.
              </p>
              <button
                onClick={handleClose}
                className={`px-8 py-3 rounded-lg transition-colors ${C.button}`}
              >
                Cerrar
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
