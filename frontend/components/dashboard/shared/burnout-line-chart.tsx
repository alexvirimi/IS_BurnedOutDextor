"use client";

/**
 * BurnoutLineChart
 * ─────────────────
 * FIX: The component was always self-fetching in "self" mode even when
 * the parent passed `dataSource`. This caused two competing fetch loops:
 * one from the internal useEffect and one from useBurnoutChart in the parent.
 * The fix: only self-fetch when dataSource is literally `undefined` (not passed).
 * When dataSource is passed (even as null or []), always use it directly.
 *
 * Supports two rendering modes:
 * 1. SELF mode — only activated when `dataSource` prop is NOT passed at all.
 *    Fetches GET /results/my-progress internally.
 * 2. EXTERNAL mode — when `dataSource` is passed (null, [], or ProgressPoint[]).
 *    Renders whatever is provided; caller handles fetching via useBurnoutChart.
 */

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { Loader2, TrendingUp } from "lucide-react";
import { apiFetch } from "@/lib/api/context";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface ProgressPoint {
  fecha: string;
  clase: string;
  valor: number;
  confianza: number;
  encuesta_id: string;
  workers?: number;
}

export type ChartMode = "self" | "individual" | "group" | "area";

export interface BurnoutLineChartProps {
  /**
   * When provided (including null or []), the chart uses this data directly.
   * When NOT provided (undefined), the chart self-fetches /results/my-progress.
   */
  dataSource?: ProgressPoint[] | null;
  mode?: ChartMode;
  title?: string;
  height?: number;
  loading?: boolean;
}

// ─── Constants ────────────────────────────────────────────────────────────────

export const SCORE_TO_LABEL: Record<number, string> = {
  1: "Muy Bajo",
  2: "Bajo",
  3: "Medio",
  4: "Moderado",
  5: "Alto",
};

const SCORE_TO_COLOR: Record<number, string> = {
  1: "#22c55e",
  2: "#86efac",
  3: "#facc15",
  4: "#f97316",
  5: "#ef4444",
};

const PRIMARY = "#2694D2";
const FOREGROUND = "#3D4676";
const MUTED = "#9ca3af";

function scoreColor(valor: number): string {
  const rounded = Math.round(valor);
  return SCORE_TO_COLOR[Math.max(1, Math.min(5, rounded))] ?? PRIMARY;
}

// ─── Tooltip ──────────────────────────────────────────────────────────────────

function CustomTooltip({
  active,
  payload,
  mode,
}: {
  active?: boolean;
  payload?: { payload: ProgressPoint }[];
  mode: ChartMode;
}) {
  if (!active || !payload?.length) return null;

  const point = payload[0].payload;
  const color = scoreColor(point.valor);
  const label = SCORE_TO_LABEL[Math.round(point.valor)] ?? point.clase;

  const dateStr = new Date(point.fecha + "T00:00:00").toLocaleDateString(
    "es-CO",
    { day: "2-digit", month: "short", year: "numeric" },
  );

  const isAggregated = mode === "group" || mode === "area";

  return (
    <div
      style={{
        background: "white",
        border: "1px solid #E5E5E5",
        borderRadius: 8,
        padding: "10px 14px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
        fontFamily: "var(--font-montserrat, sans-serif)",
        minWidth: 170,
      }}
    >
      <p style={{ fontSize: 11, color: MUTED, marginBottom: 4 }}>{dateStr}</p>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span
          style={{
            display: "inline-block",
            width: 10,
            height: 10,
            borderRadius: "50%",
            background: color,
            flexShrink: 0,
          }}
        />
        <span style={{ fontSize: 13, fontWeight: 600, color: FOREGROUND }}>
          {isAggregated ? `Promedio: ${label}` : label}
        </span>
      </div>
      {isAggregated && typeof point.valor === "number" && (
        <p style={{ fontSize: 11, color: MUTED, marginTop: 2 }}>
          Score: {point.valor.toFixed(2)} / 5
        </p>
      )}
      <p style={{ fontSize: 11, color: MUTED, marginTop: 2 }}>
        {isAggregated
          ? `Confianza prom.: ${Math.round(point.confianza * 100)}%`
          : `Confianza: ${Math.round(point.confianza * 100)}%`}
      </p>
      {isAggregated && point.workers != null && (
        <p style={{ fontSize: 11, color: MUTED, marginTop: 2 }}>
          Trabajadores: {point.workers}
        </p>
      )}
    </div>
  );
}

// ─── Custom dot ───────────────────────────────────────────────────────────────

function CustomDot({
  cx,
  cy,
  payload,
}: {
  cx?: number;
  cy?: number;
  payload?: ProgressPoint;
}) {
  if (cx === undefined || cy === undefined || !payload) return null;
  const color = scoreColor(payload.valor);
  return (
    <g>
      <circle
        cx={cx}
        cy={cy}
        r={6}
        fill={color}
        stroke="white"
        strokeWidth={2}
      />
    </g>
  );
}

// ─── Component ────────────────────────────────────────────────────────────────

export function BurnoutLineChart({
  dataSource,
  mode,
  title,
  height = 280,
  loading: externalLoading = false,
}: BurnoutLineChartProps) {
  // KEY FIX: only self-fetch when dataSource was NOT provided at all (undefined).
  // If the parent passes null or [] we use that directly — no internal fetch.
  const isSelfMode = dataSource === undefined;
  const effectiveMode: ChartMode = mode ?? (isSelfMode ? "self" : "individual");

  const [selfData, setSelfData] = useState<ProgressPoint[]>([]);
  const [selfLoading, setSelfLoading] = useState(isSelfMode);
  const [selfError, setSelfError] = useState<string | null>(null);

  useEffect(() => {
    // Only run when we are truly in self-mode (no dataSource prop passed).
    if (!isSelfMode) return;

    let cancelled = false;
    async function load() {
      setSelfLoading(true);
      setSelfError(null);
      try {
        const points = await apiFetch<ProgressPoint[]>("/results/my-progress");
        if (!cancelled) setSelfData(points);
      } catch (err) {
        if (!cancelled)
          setSelfError(
            err instanceof Error ? err.message : "Error cargando progreso",
          );
      } finally {
        if (!cancelled) setSelfLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [isSelfMode]);

  // Resolve which data / loading / error to show
  const data: ProgressPoint[] = isSelfMode ? selfData : (dataSource ?? []);
  const isLoading = externalLoading || (isSelfMode && selfLoading);
  const error = isSelfMode ? selfError : null;

  // ── States ────────────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div
        className="mt-6 bg-muted rounded-lg flex items-center justify-center"
        style={{ height }}
      >
        <div className="flex flex-col items-center gap-3 text-muted-foreground">
          <Loader2 className="animate-spin w-6 h-6" />
          <span className="text-sm font-sans">Cargando historial...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="mt-6 bg-muted rounded-lg flex items-center justify-center"
        style={{ height }}
      >
        <p className="text-sm text-destructive font-sans px-6 text-center">
          {error}
        </p>
      </div>
    );
  }

  // dataSource === null means "nothing selected yet" — show hint
  if (dataSource === null) {
    return (
      <div
        className="mt-6 bg-muted rounded-lg flex flex-col items-center justify-center gap-3"
        style={{ height }}
      >
        <TrendingUp className="w-8 h-8 text-muted-foreground opacity-40" />
        <p className="text-sm text-muted-foreground font-sans">
          Selecciona un reporte para ver el gráfico.
        </p>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div
        className="mt-6 bg-muted rounded-lg flex flex-col items-center justify-center gap-3"
        style={{ height }}
      >
        <TrendingUp className="w-8 h-8 text-muted-foreground opacity-40" />
        <p className="text-sm text-muted-foreground font-sans">
          {isSelfMode
            ? "Completa una encuesta para ver tu progreso aquí."
            : "No hay datos disponibles para este reporte."}
        </p>
      </div>
    );
  }

  const formatXTick = (dateStr: string) =>
    new Date(dateStr + "T00:00:00").toLocaleDateString("es-CO", {
      month: "short",
      day: "numeric",
    });

  const isAggregated = effectiveMode === "group" || effectiveMode === "area";

  return (
    <div className="mt-6 bg-background rounded-lg border border-border p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 px-2">
        <div>
          <p className="text-xs text-muted-foreground font-sans uppercase tracking-wide">
            {isAggregated
              ? "Promedio de riesgo del grupo"
              : "Historial de riesgo"}
          </p>
          {title && (
            <p
              className="text-sm font-semibold text-foreground mt-0.5 truncate max-w-xs"
              style={{ fontFamily: "var(--font-unbounded, sans-serif)" }}
            >
              {title}
            </p>
          )}
        </div>

        {/* Colour legend */}
        <div className="hidden sm:flex items-center gap-3 flex-wrap justify-end">
          {Object.entries(SCORE_TO_LABEL)
            .sort((a, b) => Number(a[0]) - Number(b[0]))
            .map(([score, label]) => (
              <div key={score} className="flex items-center gap-1.5">
                <span
                  style={{
                    display: "inline-block",
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: SCORE_TO_COLOR[Number(score)],
                  }}
                />
                <span className="text-xs text-muted-foreground font-sans">
                  {label}
                </span>
              </div>
            ))}
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={data}
          margin={{ top: 8, right: 16, left: -8, bottom: 0 }}
        >
          <CartesianGrid
            strokeDasharray="4 4"
            stroke="#E5E5E5"
            vertical={false}
          />
          <XAxis
            dataKey="fecha"
            tickFormatter={formatXTick}
            tick={{ fontSize: 11, fill: MUTED, fontFamily: "sans-serif" }}
            axisLine={false}
            tickLine={false}
            dy={8}
          />
          <YAxis
            domain={[0.5, 5.5]}
            ticks={[1, 2, 3, 4, 5]}
            tickFormatter={(v: number) =>
              SCORE_TO_LABEL[v]?.split(" ")[0] ?? ""
            }
            tick={{ fontSize: 11, fill: MUTED, fontFamily: "sans-serif" }}
            axisLine={false}
            tickLine={false}
            width={52}
          />
          <ReferenceLine
            y={4}
            stroke="#f97316"
            strokeDasharray="6 3"
            strokeWidth={1}
            label={{
              value: "Alerta",
              position: "right",
              fontSize: 10,
              fill: "#f97316",
              fontFamily: "sans-serif",
            }}
          />
          <Tooltip content={<CustomTooltip mode={effectiveMode} />} />
          <Line
            type="monotone"
            dataKey="valor"
            stroke={PRIMARY}
            strokeWidth={2.5}
            dot={<CustomDot />}
            activeDot={{ r: 8, fill: PRIMARY, stroke: "white", strokeWidth: 2 }}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Date range footer */}
      {data.length >= 2 && (
        <p className="text-xs text-muted-foreground font-sans text-center mt-3 opacity-70">
          {new Date(data[0].fecha + "T00:00:00").toLocaleDateString("es-CO", {
            day: "numeric",
            month: "long",
            year: "numeric",
          })}{" "}
          →{" "}
          {new Date(
            data[data.length - 1].fecha + "T00:00:00",
          ).toLocaleDateString("es-CO", {
            day: "numeric",
            month: "long",
            year: "numeric",
          })}
        </p>
      )}
    </div>
  );
}
