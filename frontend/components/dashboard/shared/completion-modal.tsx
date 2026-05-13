"use client";

/**
 * CompletionModal
 * ───────────────
 * Shown after a survey is submitted. Displays prediction status:
 *   pending     → "Calculando tu nivel de riesgo…"
 *   success     → "Análisis completado"
 *   unavailable → friendly message about needing more history
 *   error       → non-critical warning (prediction failed, answers saved)
 *   idle        → nothing extra (fallback)
 *
 * Drop-in replacement for the inline completion block in:
 *   WKREncuestasView, PMEncuestasView, HRRealizarEncuestasView
 *
 * Usage:
 *   import { CompletionModal } from "@/components/dashboard/shared/completion-modal";
 *
 *   {showCompletado && (
 *     <CompletionModal
 *       predictionStatus={predictionStatus}
 *       onClose={handleClose}
 *       colors={C}
 *     />
 *   )}
 */

import { Check, Loader2, AlertCircle, Info } from "lucide-react";
import type { PredictionStatus } from "@/hooks/useEncuestas";

interface ColorTokens {
  button: string;
}

interface CompletionModalProps {
  predictionStatus: PredictionStatus;
  onClose: () => void;
  /** Pass BUTTONS_COLORS.worker / .pm / .hr as needed */
  colors: ColorTokens;
}

// ─── Prediction status copy ────────────────────────────────────────────────────

const PREDICTION_UI: Record<
  PredictionStatus,
  { icon: React.ReactNode; text: string; sub: string } | null
> = {
  idle: null,
  pending: {
    icon: <Loader2 size={16} className="animate-spin text-primary" />,
    text: "Calculando tu nivel de riesgo…",
    sub: "El análisis de burnout se está procesando en segundo plano.",
  },
  success: {
    icon: <Check size={16} className="text-green-600" />,
    text: "Análisis completado",
    sub: "Tu resultado ya está disponible en la sección de progreso.",
  },
  unavailable: {
    icon: <Info size={16} className="text-muted-foreground" />,
    text: "Se necesitan más encuestas",
    sub: "Para generar tu predicción de burnout necesitamos historial de al menos una encuesta completada por período. ¡Sigue respondiendo!",
  },
  error: {
    icon: <AlertCircle size={16} className="text-amber-500" />,
    text: "El análisis tardará un poco más",
    sub: "Tus respuestas quedaron guardadas. El resultado se calculará automáticamente en los próximos minutos.",
  },
};

// ─── Component ─────────────────────────────────────────────────────────────────

export function CompletionModal({
  predictionStatus,
  onClose,
  colors,
}: CompletionModalProps) {
  const predictionUI = PREDICTION_UI[predictionStatus];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-background rounded-xl p-8 w-full max-w-md text-center">
        {/* Success icon */}
        <div
          className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 ${colors.button}`}
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
          Gracias por tomarte el tiempo de responder. Tus respuestas nos ayudan
          a mejorar tu experiencia laboral.
        </p>

        {/* Prediction status banner */}
        {predictionUI && (
          <div className="mb-6 flex items-start gap-3 px-4 py-3 rounded-lg bg-secondary text-left">
            <span className="mt-0.5 flex-shrink-0">{predictionUI.icon}</span>
            <div>
              <p className="text-sm font-medium text-foreground">
                {predictionUI.text}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5 font-sans leading-relaxed">
                {predictionUI.sub}
              </p>
            </div>
          </div>
        )}

        <button
          onClick={onClose}
          className={`px-8 py-3 rounded-lg transition-colors ${colors.button}`}
        >
          Cerrar
        </button>
      </div>
    </div>
  );
}
