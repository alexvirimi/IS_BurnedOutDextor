"use client";

/**
 * useEncuestas
 * ────────────
 * Shared hook for WKREncuestasView, PMEncuestasView, and HRRealizarEncuestasView.
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
import { apiFetch, apiPostJson } from "@/lib/api/context";
import type {
  MySurveyResponse,
  SurveyComplete,
  BulkAnswerPayload,
  BulkAnswerItem,
} from "@/lib/api/interfaces";

// ─── Constante canónica (misma que el backend) ────────────────────────────────
const STATUS_FINALIZADA = "finalizada";

/**
 * Devuelve true si la encuesta puede recibir respuestas.
 * Normaliza a minúsculas para tolerar inconsistencias del backend.
 * Trata status null/undefined/vacío como "abierta" (safe default).
 */
function isSurveyOpen(status: string | null | undefined): boolean {
  if (!status) return true;
  return status.trim().toLowerCase() !== STATUS_FINALIZADA;
}

// ─── Tipos internos ───────────────────────────────────────────────────────────

export interface EncuestaPregunta {
  id: string;
  texto: string;
  tipo: "escala";
}

export interface Encuesta {
  id: string;
  nombre: string;
  status: string; // ← nuevo: propagado desde MySurveyResponse
  already_responded: boolean;
  /** Populated lazily when the user opens the survey */
  preguntas: EncuestaPregunta[];
}

// Submission states exposed to the view
export type SubmitState = "idle" | "submitting" | "success" | "error";

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useEncuestas() {
  const [encuestas, setEncuestas] = useState<Encuesta[]>([]);
  const [loadingList, setLoadingList] = useState(false);
  const [listError, setListError] = useState<string | null>(null);

  const [selectedEncuesta, setSelectedEncuesta] = useState<Encuesta | null>(
    null,
  );
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [questionsError, setQuestionsError] = useState<string | null>(null);

  const [respuestas, setRespuestas] = useState<Record<string, number>>({});
  const [currentQuestion, setCurrentQuestion] = useState(0);

  // ── Submission state ───────────────────────────────────────────────────────
  const [submitState, setSubmitState] = useState<SubmitState>("idle");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [showCompletado, setShowCompletado] = useState(false);

  // ── Load assigned surveys ─────────────────────────────────────────────────

  const loadEncuestas = useCallback(async () => {
    setLoadingList(true);
    setListError(null);
    try {
      const data = await apiFetch<MySurveyResponse[]>(
        "/survey-assignment/my-surveys",
      );

      // ── Filtro canónico: excluir encuestas finalizadas ─────────────────
      // Se aplica una sola vez aquí. Los tres views que usan este hook
      // reciben únicamente encuestas abiertas, sin necesidad de filtrar
      // en cada componente individualmente.
      const mapped: Encuesta[] = data
        .filter((s) => isSurveyOpen(s.status))
        .map((s) => ({
          id: s.id,
          nombre: s.name,
          status: s.status,
          already_responded: s.already_responded,
          preguntas: [],
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

  // ── Open a survey ────────────────────────────────────────────────────────

  const handleSelectEncuesta = useCallback(async (encuesta: Encuesta) => {
    // ── Segunda guarda: rechaza en el handler aunque pase el filtro del list ──
    // Cubre casos como deep-links o race conditions donde el status cambia
    // después de cargar la lista.
    if (!isSurveyOpen(encuesta.status)) {
      setQuestionsError(
        "Esta encuesta ya fue finalizada y no acepta nuevas respuestas.",
      );
      return;
    }

    // Reset per-survey state
    setCurrentQuestion(0);
    setRespuestas({});
    setShowCompletado(false);
    setQuestionsError(null);
    setSubmitState("idle");
    setSubmitError(null);

    // If questions are already cached, open immediately
    if (encuesta.preguntas.length > 0) {
      setSelectedEncuesta(encuesta);
      return;
    }

    // Open modal in loading state while fetching
    setLoadingQuestions(true);
    setSelectedEncuesta({ ...encuesta, preguntas: [] });

    try {
      const data = await apiFetch<SurveyComplete>(
        `/survey/${encuesta.id}/complete`,
      );

      // `data.questions[].id` is the question_survey id — exactly what the
      // bulk endpoint needs. We store it as `EncuestaPregunta.id`.
      const preguntas: EncuestaPregunta[] = data.questions.map((q) => ({
        id: q.id, // question_survey id
        texto: q.question_text,
        tipo: "escala" as const,
      }));

      const populated: Encuesta = { ...encuesta, preguntas };

      // Cache so reopening the same survey doesn't refetch
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

  // ── Answer handlers ────────────────────────────────────────────────────────

  const handleRespuesta = useCallback(
    (value: number) => {
      if (!selectedEncuesta) return;
      const preguntaId = selectedEncuesta.preguntas[currentQuestion]?.id;
      if (!preguntaId) return;
      setRespuestas((prev) => ({ ...prev, [preguntaId]: value }));
    },
    [selectedEncuesta, currentQuestion],
  );

  const handlePrev = useCallback(() => {
    setCurrentQuestion((q) => Math.max(0, q - 1));
  }, []);

  // ── Submit answers to the backend ──────────────────────────────────────────

  const submitAnswers = useCallback(
    async (encuesta: Encuesta, answers: Record<string, number>) => {
      // Guard: prevent duplicate submissions
      if (submitState === "submitting") return;

      // Guard: all questions must be answered
      const unanswered = encuesta.preguntas.filter(
        (p) => answers[p.id] === undefined,
      );
      if (unanswered.length > 0) {
        setSubmitError(
          `Faltan ${unanswered.length} respuesta${unanswered.length > 1 ? "s" : ""} por completar.`,
        );
        return;
      }

      setSubmitState("submitting");
      setSubmitError(null);

      const items: BulkAnswerItem[] = encuesta.preguntas.map((p) => ({
        id_question_survey: p.id,
        value: answers[p.id],
      }));

      const payload: BulkAnswerPayload = {
        id_survey: encuesta.id,
        answers: items,
      };

      try {
        await apiPostJson("/answers/bulk", payload);

        setSubmitState("success");

        // Mark the survey as responded in the local list so the button
        // is disabled without requiring a full list refetch
        setEncuestas((prev) =>
          prev.map((e) =>
            e.id === encuesta.id ? { ...e, already_responded: true } : e,
          ),
        );

        setShowCompletado(true);
      } catch (err) {
        setSubmitState("error");
        setSubmitError(
          err instanceof Error ? err.message : "Error enviando respuestas",
        );
      }
    },
    [submitState],
  );

  // ── Next / Finalise ────────────────────────────────────────────────────────

  const handleNext = useCallback(() => {
    if (!selectedEncuesta) return;

    const isLast = currentQuestion === selectedEncuesta.preguntas.length - 1;

    if (!isLast) {
      setCurrentQuestion((q) => q + 1);
      return;
    }

    // Last question → submit
    submitAnswers(selectedEncuesta, respuestas);
  }, [selectedEncuesta, currentQuestion, respuestas, submitAnswers]);

  // ── Close / reset ──────────────────────────────────────────────────────────

  const handleClose = useCallback(() => {
    setSelectedEncuesta(null);
    setCurrentQuestion(0);
    setRespuestas({});
    setShowCompletado(false);
    setQuestionsError(null);
    setSubmitState("idle");
    setSubmitError(null);
  }, []);

  // ── Derived values ─────────────────────────────────────────────────────────

  const currentPregunta = selectedEncuesta?.preguntas[currentQuestion] ?? null;
  const currentRespuesta = currentPregunta
    ? (respuestas[currentPregunta.id] ?? undefined)
    : undefined;

  const isSubmitting = submitState === "submitting";

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

    // Submission
    submitState,
    submitError,
    isSubmitting,
  };
}
