"use client";

import { useState } from "react";
import { X, ChevronLeft, ChevronRight, Check } from "lucide-react";

interface Encuesta {
  id: number;
  nombre: string;
  preguntas: {
    id: number;
    texto: string;
    tipo: "escala" | "texto" | "opcion";
    opciones?: string[];
  }[];
}

const encuestasPendientes: Encuesta[] = [
  {
    id: 1,
    nombre: "Realizar encuesta de seguimiento 2026-4-2",
    preguntas: [
      {
        id: 1,
        texto: "¿Cómo calificarías tu nivel de energía esta semana?",
        tipo: "escala",
      },
      {
        id: 2,
        texto: "¿Te has sentido apoyado por tu equipo?",
        tipo: "escala",
      },
      {
        id: 3,
        texto: "¿Qué tan satisfecho estás con tu carga de trabajo actual?",
        tipo: "escala",
      },
      {
        id: 4,
        texto: "¿Has experimentado estrés relacionado con el trabajo?",
        tipo: "escala",
      },
      {
        id: 5,
        texto: "¿Cómo describirías tu motivación laboral?",
        tipo: "escala",
      },
      { id: 6, texto: "¿Tienes algún comentario adicional?", tipo: "texto" },
    ],
  },
  {
    id: 2,
    nombre: "Realizar encuesta mensual 2026-4",
    preguntas: [
      {
        id: 1,
        texto: "¿Cómo calificarías el ambiente laboral este mes?",
        tipo: "escala",
      },
      { id: 2, texto: "¿Te sientes valorado por tu trabajo?", tipo: "escala" },
      {
        id: 3,
        texto: "¿Cómo calificarías la comunicación con tu supervisor?",
        tipo: "escala",
      },
      {
        id: 4,
        texto:
          "¿Has podido mantener un equilibrio entre trabajo y vida personal?",
        tipo: "escala",
      },
      {
        id: 5,
        texto: "¿Qué aspectos mejorarías de tu entorno laboral?",
        tipo: "texto",
      },
    ],
  },
];

interface WKREncuestasViewProps {
  userName: string;
}

export function WKREncuestasView({ userName }: WKREncuestasViewProps) {
  const [selectedEncuesta, setSelectedEncuesta] = useState<Encuesta | null>(
    null,
  );
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [respuestas, setRespuestas] = useState<Record<number, number | string>>(
    {},
  );
  const [showCompletado, setShowCompletado] = useState(false);

  const handleSelectEncuesta = (encuesta: Encuesta) => {
    setSelectedEncuesta(encuesta);
    setCurrentQuestion(0);
    setRespuestas({});
    setShowCompletado(false);
  };

  const handleRespuesta = (value: number | string) => {
    if (!selectedEncuesta) return;
    setRespuestas({
      ...respuestas,
      [selectedEncuesta.preguntas[currentQuestion].id]: value,
    });
  };

  const handleNext = () => {
    if (!selectedEncuesta) return;
    if (currentQuestion < selectedEncuesta.preguntas.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      setShowCompletado(true);
    }
  };

  const handlePrev = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleClose = () => {
    setSelectedEncuesta(null);
    setCurrentQuestion(0);
    setRespuestas({});
    setShowCompletado(false);
  };

  const currentPregunta = selectedEncuesta?.preguntas[currentQuestion];
  const currentRespuesta = currentPregunta
    ? respuestas[currentPregunta.id]
    : undefined;

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

        {/* Pending Surveys */}
        <div className="space-y-3 max-w-3xl">
          {encuestasPendientes.map((encuesta) => (
            <button
              key={encuesta.id}
              onClick={() => handleSelectEncuesta(encuesta)}
              className="w-full text-left px-4 py-3 rounded-lg bg-accent text-foreground hover:bg-accent/80 transition-colors"
            >
              {encuesta.nombre}
            </button>
          ))}
        </div>

        {/* Survey Modal */}
        {selectedEncuesta && !showCompletado && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-background rounded-xl p-6 w-full max-w-2xl relative">
              <button
                onClick={handleClose}
                className="absolute top-4 right-4 w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                <X size={18} />
              </button>

              <h2
                className="text-2xl font-bold text-foreground mb-2"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                {selectedEncuesta.nombre.replace("Realizar ", "").toUpperCase()}
              </h2>

              <p className="text-muted-foreground mb-8">
                Pregunta {currentQuestion + 1} de{" "}
                {selectedEncuesta.preguntas.length}
              </p>

              {/* Progress Bar */}
              <div className="w-full h-2 bg-secondary rounded-full mb-8">
                <div
                  className="h-full bg-primary rounded-full transition-all duration-300"
                  style={{
                    width: `${((currentQuestion + 1) / selectedEncuesta.preguntas.length) * 100}%`,
                  }}
                />
              </div>

              {/* Question */}
              <div className="mb-8">
                <p className="text-foreground text-lg mb-6">
                  {currentPregunta?.texto}
                </p>

                {currentPregunta?.tipo === "escala" && (
                  <div className="flex justify-between gap-2">
                    {[1, 2, 3, 4, 5].map((value) => (
                      <button
                        key={value}
                        onClick={() => handleRespuesta(value)}
                        className={`flex-1 py-4 rounded-lg border-2 transition-all ${
                          currentRespuesta === value
                            ? "bg-primary text-primary-foreground border-primary"
                            : "border-foreground/30 text-foreground hover:border-primary"
                        }`}
                      >
                        {value}
                      </button>
                    ))}
                  </div>
                )}

                {currentPregunta?.tipo === "texto" && (
                  <textarea
                    value={(currentRespuesta as string) || ""}
                    onChange={(e) => handleRespuesta(e.target.value)}
                    placeholder="Escribe tu respuesta aquí..."
                    className="w-full p-4 border-2 border-foreground/30 rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary resize-none h-32"
                  />
                )}
              </div>

              {/* Scale Labels */}
              {currentPregunta?.tipo === "escala" && (
                <div className="flex justify-between text-sm text-muted-foreground mb-8">
                  <span>Muy en desacuerdo</span>
                  <span>Muy de acuerdo</span>
                </div>
              )}

              {/* Navigation */}
              <div className="flex justify-between">
                <button
                  onClick={handlePrev}
                  disabled={currentQuestion === 0}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    currentQuestion === 0
                      ? "text-muted-foreground cursor-not-allowed"
                      : "text-foreground hover:bg-secondary"
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
                      : "bg-primary text-primary-foreground hover:bg-primary/90"
                  }`}
                >
                  {currentQuestion === selectedEncuesta.preguntas.length - 1
                    ? "Finalizar"
                    : "Siguiente"}
                  <ChevronRight size={20} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Completion Modal */}
        {showCompletado && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-background rounded-xl p-8 w-full max-w-md text-center">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-6">
                <Check size={32} className="text-primary-foreground" />
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
                className="px-8 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
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
