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
 *  5. After a successful bulk submission, call POST /burnout/predict and
 *     refresh GET /results/ — both fire-and-forget with safe error handling.
 */

import { useState, useCallback, useRef } from "react";
import { apiFetch, apiPostJson } from "@/lib/api/context";
import type {
  MySurveyResponse,
  SurveyComplete,
  BulkAnswerPayload,
  BulkAnswerItem,
} from "@/lib/api/interfaces";

// ─── Constante canónica (misma que el backend) ────────────────────────────────
const STATUS_CERRADA = "cerrada";

function isSurveyOpen(status: string | null | undefined): boolean {
  if (!status) return true;
  return status.trim().toLowerCase() !== STATUS_CERRADA;
}

// ─── Prediction status ────────────────────────────────────────────────────────

/**
 * idle        – no prediction in flight
 * pending     – waiting for the backend to finish the AI call
 * success     – prediction stored and results refreshed
 * unavailable – backend says not enough survey history yet
 * error       – unexpected error (AI service down, network, etc.)
 */
export type PredictionStatus =
  | "idle"
  | "pending"
  | "success"
  | "unavailable"
  | "error";

const INCOMPLETE_HISTORY_KEYWORDS = [
  "incompleto",
  "insuficiente",
  "faltan",
  "historial",
  "avg_despersonalizacion",
  "avg_agotamiento",
  "eficacia_invertida",
  "datos incompletos",
];

/** Returns true when the error message indicates missing survey history. */
function isInsufficientHistoryError(message: string): boolean {
  const lower = message.toLowerCase();
  return INCOMPLETE_HISTORY_KEYWORDS.some((kw) => lower.includes(kw));
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
  status: string;
  already_responded: boolean;
  preguntas: EncuestaPregunta[];
}

export type SubmitState = "idle" | "submitting" | "success" | "error";

// ─── Prediction trigger ───────────────────────────────────────────────────────

/**
 * Calls POST /burnout/predict and then refreshes GET /results/.
 * Returns the final PredictionStatus — never throws.
 *
 * Separated from the hook so it is easy to unit-test.
 *
 * @param workerId  – worker UUID from the JWT session
 * @param surveyId  – survey that was just completed
 * @param delayMs   – optional warm-up delay before hitting the predict endpoint
 *                   (gives asyncio.create_task on the backend a head-start)
 */
export async function triggerPrediction(
  workerId: string,
  surveyId: string,
  delayMs = 1500,
): Promise<PredictionStatus> {
  // Small delay so the backend async task has already persisted answers
  if (delayMs > 0) {
    await new Promise((r) => setTimeout(r, delayMs));
  }

  try {
    await apiPostJson("/burnout/predict", {
      worker_id: workerId,
      survey_id: surveyId,
    });
    return "success";
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);

    if (isInsufficientHistoryError(message)) {
      return "unavailable";
    }

    // AI service down, network error, etc.
    console.warn("[useEncuestas] Prediction failed (non-critical):", message);
    return "error";
  }
}

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

  // ── Prediction state ───────────────────────────────────────────────────────
  const [predictionStatus, setPredictionStatus] =
    useState<PredictionStatus>("idle");

  /**
   * Guard against duplicate prediction calls for the same survey.
   * Stores the surveyId of the in-flight or last completed prediction.
   */
  const predictionInFlightRef = useRef<string | null>(null);

  // ── Load assigned surveys ─────────────────────────────────────────────────

  const loadEncuestas = useCallback(async () => {
    setLoadingList(true);
    setListError(null);
    try {
      const data = await apiFetch<MySurveyResponse[]>(
        "/survey-assignment/my-surveys",
      );

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
    if (!isSurveyOpen(encuesta.status)) {
      setQuestionsError(
        "Esta encuesta ya fue cerrada y no acepta nuevas respuestas.",
      );
      return;
    }

    setCurrentQuestion(0);
    setRespuestas({});
    setShowCompletado(false);
    setQuestionsError(null);
    setSubmitState("idle");
    setSubmitError(null);
    setPredictionStatus("idle");

    if (encuesta.preguntas.length > 0) {
      setSelectedEncuesta(encuesta);
      return;
    }

    setLoadingQuestions(true);
    setSelectedEncuesta({ ...encuesta, preguntas: [] });

    try {
      const data = await apiFetch<SurveyComplete>(
        `/survey/${encuesta.id}/complete`,
      );

      const preguntas: EncuestaPregunta[] = data.questions.map((q) => ({
        id: q.id,
        texto: q.question_text,
        tipo: "escala" as const,
      }));

      const populated: Encuesta = { ...encuesta, preguntas };

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

  // ── Submit answers + orchestrate prediction ───────────────────────────────

  const submitAnswers = useCallback(
    async (encuesta: Encuesta, answers: Record<string, number>) => {
      if (submitState === "submitting") return;

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
      setPredictionStatus("idle");

      const items: BulkAnswerItem[] = encuesta.preguntas.map((p) => ({
        id_question_survey: p.id,
        value: answers[p.id],
      }));

      const payload: BulkAnswerPayload = {
        id_survey: encuesta.id,
        answers: items,
      };

      // ── Step 1: Submit answers ────────────────────────────────────────────
      try {
        await apiPostJson("/answers/bulk", payload);
      } catch (err) {
        setSubmitState("error");
        setSubmitError(
          err instanceof Error ? err.message : "Error enviando respuestas",
        );
        return;
      }

      // Mark locally as responded immediately so the button disables
      setEncuestas((prev) =>
        prev.map((e) =>
          e.id === encuesta.id ? { ...e, already_responded: true } : e,
        ),
      );

      // Show completion screen right away — prediction happens in background
      setSubmitState("success");
      setShowCompletado(true);

      // ── Step 2: Trigger prediction (non-blocking) ─────────────────────────
      // Guard: skip if a prediction is already in-flight for this survey
      if (predictionInFlightRef.current === encuesta.id) return;
      predictionInFlightRef.current = encuesta.id;

      setPredictionStatus("pending");

      // Retrieve workerId from the session cookie that AuthProvider stores.
      // We read it here lazily to avoid coupling this hook to useAuth.
      let workerId: string | null = null;
      try {
        const cookieMatch = document.cookie
          .split("; ")
          .find((row) => row.startsWith("bud_session="));
        if (cookieMatch) {
          const raw = decodeURIComponent(
            cookieMatch.split("=").slice(1).join("="),
          );
          workerId =
            (JSON.parse(raw) as { worker_id?: string }).worker_id ?? null;
        }
      } catch {
        // Cookie unavailable in SSR or malformed — skip prediction silently
      }

      if (!workerId) {
        // Can't predict without a worker id — not a fatal UI error
        setPredictionStatus("unavailable");
        predictionInFlightRef.current = null;
        return;
      }

      // Fire-and-forget: does not block the UI
      triggerPrediction(workerId, encuesta.id).then((status) => {
        setPredictionStatus(status);
        predictionInFlightRef.current = null;
      });
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
    setPredictionStatus("idle");
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

    // Prediction (new)
    predictionStatus,
  };
}
