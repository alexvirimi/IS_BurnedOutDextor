"use client";

/**
 * useEncuestas
 * ────────────
 * Shared hook for WKREncuestasView and PMEncuestasView.
 *
 * Responsibilities:
 *  1. Fetch the authenticated user's assigned surveys from
 *     GET /survey-assignment/my-surveys
 *  2. When the user selects a survey, fetch its questions from
 *     GET /survey/{survey_id}/questions
 *  3. Normalise the API shapes into the internal `Encuesta` type used by
 *     the existing modal UI — all questions are treated as tipo: "escala".
 *  4. Expose handlers that the view components wire up to their buttons.
 */

import { useState, useCallback } from "react";
import { apiFetch } from "@/lib/api/context";
import type {
  MySurveyResponse,
  SurveyWithQuestions,
} from "@/lib/api/interfaces";

// ─── Internal types (consumed by the view) ────────────────────────────────────

export interface EncuestaPregunta {
  id: string;
  texto: string;
  tipo: "escala"; // backend only returns scale questions
}

export interface Encuesta {
  id: string;
  nombre: string;
  already_responded: boolean;
  /** Populated lazily when the user opens the survey */
  preguntas: EncuestaPregunta[];
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useEncuestas() {
  // Survey list state
  const [encuestas, setEncuestas] = useState<Encuesta[]>([]);
  const [loadingList, setLoadingList] = useState(false);
  const [listError, setListError] = useState<string | null>(null);

  // Active survey / question state
  const [selectedEncuesta, setSelectedEncuesta] = useState<Encuesta | null>(
    null,
  );
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [questionsError, setQuestionsError] = useState<string | null>(null);

  // Answer state — keyed by question id
  const [respuestas, setRespuestas] = useState<Record<string, number>>({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [showCompletado, setShowCompletado] = useState(false);

  // ── Load assigned surveys ──────────────────────────────────────────────────

  const loadEncuestas = useCallback(async () => {
    setLoadingList(true);
    setListError(null);
    try {
      const data = await apiFetch<MySurveyResponse[]>(
        "/survey-assignment/my-surveys",
      );

      // Map API response → internal Encuesta shape
      const mapped: Encuesta[] = data.map((s) => ({
        id: s.id,
        nombre: s.name,
        already_responded: s.already_responded,
        preguntas: [], // populated lazily on open
      }));

      setEncuestas(mapped);
    } catch (err) {
      setListError(
        err instanceof Error ? err.message : "Error cargando encuestas",
      );
    } finally {
      setLoadingList(false);
    }
  }, []);

  // ── Open a survey — fetch questions lazily ─────────────────────────────────

  const handleSelectEncuesta = useCallback(async (encuesta: Encuesta) => {
    // Reset per-survey state
    setCurrentQuestion(0);
    setRespuestas({});
    setShowCompletado(false);
    setQuestionsError(null);

    // If we already have questions cached, open immediately
    if (encuesta.preguntas.length > 0) {
      setSelectedEncuesta(encuesta);
      return;
    }

    // Fetch questions for this survey
    setLoadingQuestions(true);
    setSelectedEncuesta({ ...encuesta, preguntas: [] }); // open modal in loading state

    try {
      const data = await apiFetch<SurveyWithQuestions>(
        `/survey/${encuesta.id}/questions`,
      );

      // Normalise: all questions are escala; map text → texto
      const preguntas: EncuestaPregunta[] = data.questions.map((q) => ({
        id: q.id,
        texto: q.text,
        tipo: "escala" as const,
      }));

      const populated: Encuesta = { ...encuesta, preguntas };

      // Update cache so reopening doesn't refetch
      setEncuestas((prev) =>
        prev.map((e) => (e.id === encuesta.id ? populated : e)),
      );

      setSelectedEncuesta(populated);
    } catch (err) {
      setQuestionsError(
        err instanceof Error ? err.message : "Error cargando preguntas",
      );
      setSelectedEncuesta(null);
    } finally {
      setLoadingQuestions(false);
    }
  }, []);

  // ── Answer + navigation ────────────────────────────────────────────────────

  const handleRespuesta = useCallback(
    (value: number) => {
      if (!selectedEncuesta) return;
      const preguntaId = selectedEncuesta.preguntas[currentQuestion]?.id;
      if (!preguntaId) return;
      setRespuestas((prev) => ({ ...prev, [preguntaId]: value }));
    },
    [selectedEncuesta, currentQuestion],
  );

  const handleNext = useCallback(() => {
    if (!selectedEncuesta) return;
    if (currentQuestion < selectedEncuesta.preguntas.length - 1) {
      setCurrentQuestion((q) => q + 1);
    } else {
      setShowCompletado(true);
    }
  }, [selectedEncuesta, currentQuestion]);

  const handlePrev = useCallback(() => {
    setCurrentQuestion((q) => Math.max(0, q - 1));
  }, []);

  const handleClose = useCallback(() => {
    setSelectedEncuesta(null);
    setCurrentQuestion(0);
    setRespuestas({});
    setShowCompletado(false);
    setQuestionsError(null);
  }, []);

  // ── Derived values the view needs ──────────────────────────────────────────

  const currentPregunta = selectedEncuesta?.preguntas[currentQuestion] ?? null;
  const currentRespuesta = currentPregunta
    ? (respuestas[currentPregunta.id] ?? undefined)
    : undefined;

  return {
    // Survey list
    encuestas,
    loadingList,
    listError,
    loadEncuestas,

    // Selected survey + question flow
    selectedEncuesta,
    loadingQuestions,
    questionsError,
    handleSelectEncuesta,

    // Answers + navigation
    currentQuestion,
    respuestas,
    currentPregunta,
    currentRespuesta,
    showCompletado,
    handleRespuesta,
    handleNext,
    handlePrev,
    handleClose,
  };
}
