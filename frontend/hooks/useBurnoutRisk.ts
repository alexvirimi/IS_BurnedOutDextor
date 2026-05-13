"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api/context";
import { SCORE_TO_LABEL } from "@/components/dashboard/shared/burnout-line-chart";

interface ProgressPoint {
  fecha: string;
  clase: string;
  valor: number;
  confianza: number;
  encuesta_id: string;
}

interface UseBurnoutRiskResult {
  label: string;
  isLoading: boolean;
}

export function useBurnoutRisk(): UseBurnoutRiskResult {
  const [label, setLabel] = useState<string>("--");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let cancelled = false;

    async function fetchProgress() {
      try {
        const data = await apiFetch<ProgressPoint[]>("/results/my-progress");

        const latest = data.at(-1);

        if (!latest || cancelled) return;

        setLabel(SCORE_TO_LABEL[latest.valor] ?? "--");
      } catch {
        if (!cancelled) {
          setLabel("--");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    fetchProgress();

    return () => {
      cancelled = true;
    };
  }, []);

  return {
    label,
    isLoading,
  };
}
