"use client";

/**
 * BurnoutLineChart
 * ─────────────────
 * Gráfica de líneas del historial de riesgo de burnout del usuario.
 * Consume GET /results/my-progress
 *
 * Las clases categóricas se convierten a valores numéricos (1-5) en el backend:
 *   1 = Muy Bajo  2 = Bajo  3 = Medio  4 = Moderado  5 = Alto
 *
 * Uso: reemplaza <PowerBIPlaceholder /> en las vistas de progreso personal.
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

// ─── Tipos ────────────────────────────────────────────────────────────────────

interface ProgressPoint {
  fecha: string; // ISO date string "2025-06-01"
  clase: string; // "Bajo", "Moderado", etc.
  valor: number; // 1-5
  confianza: number; // 0.0-1.0
  encuesta_id: string;
}

// ─── Constantes ───────────────────────────────────────────────────────────────

// Mapeo inverso para el eje Y del tooltip
export const SCORE_TO_LABEL: Record<number, string> = {
  1: "Muy Bajo",
  2: "Bajo",
  3: "Medio",
  4: "Moderado",
  5: "Alto",
};

// Color del punto/línea según el riesgo
const SCORE_TO_COLOR: Record<number, string> = {
  1: "#22c55e", // green-500
  2: "#86efac", // green-300
  3: "#facc15", // yellow-400
  4: "#f97316", // orange-500
  5: "#ef4444", // red-500
};

// Colores del tema Inbudex
const PRIMARY = "#2694D2";
const FOREGROUND = "#3D4676";
const MUTED = "#9ca3af";

// ─── Tooltip personalizado ────────────────────────────────────────────────────

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: ProgressPoint }[];
}) {
  if (!active || !payload?.length) return null;

  const point = payload[0].payload;
  const color = SCORE_TO_COLOR[point.valor] ?? PRIMARY;
  const label = SCORE_TO_LABEL[point.valor] ?? point.clase;

  // Formatear fecha a "DD MMM YYYY" en español
  const dateStr = new Date(point.fecha + "T00:00:00").toLocaleDateString(
    "es-CO",
    { day: "2-digit", month: "short", year: "numeric" },
  );

  return (
    <div
      style={{
        background: "white",
        border: `1px solid #E5E5E5`,
        borderRadius: 8,
        padding: "10px 14px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
        fontFamily: "var(--font-montserrat, sans-serif)",
        minWidth: 160,
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
        <span
          style={{
            fontSize: 13,
            fontWeight: 600,
            color: FOREGROUND,
          }}
        >
          {label}
        </span>
      </div>
      <p style={{ fontSize: 11, color: MUTED, marginTop: 4 }}>
        Confianza: {Math.round(point.confianza * 100)}%
      </p>
    </div>
  );
}

// ─── Punto personalizado (coloreado por nivel) ────────────────────────────────

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
  const color = SCORE_TO_COLOR[payload.valor] ?? PRIMARY;
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

// ─── Componente principal ─────────────────────────────────────────────────────

interface BurnoutLineChartProps {
  /** Título que se muestra sobre la gráfica */
  title?: string;
  /** Altura del área de la gráfica en px */
  height?: number;
}

export function BurnoutLineChart({
  title,
  height = 280,
}: BurnoutLineChartProps) {
  const [data, setData] = useState<ProgressPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const points = await apiFetch<ProgressPoint[]>("/results/my-progress");
        if (!cancelled) setData(points);
      } catch (err) {
        if (!cancelled)
          setError(
            err instanceof Error ? err.message : "Error cargando progreso",
          );
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  // ── Estado: cargando ──────────────────────────────────────────────────
  if (loading) {
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

  // ── Estado: error ─────────────────────────────────────────────────────
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

  // ── Estado: sin datos ─────────────────────────────────────────────────
  if (data.length === 0) {
    return (
      <div
        className="mt-6 bg-muted rounded-lg flex flex-col items-center justify-center gap-3"
        style={{ height }}
      >
        <TrendingUp className="w-8 h-8 text-muted-foreground opacity-40" />
        <p className="text-sm text-muted-foreground font-sans">
          Aún no hay resultados para mostrar.
        </p>
        <p className="text-xs text-muted-foreground font-sans opacity-70">
          Completa una encuesta para ver tu progreso aquí.
        </p>
      </div>
    );
  }

  // Formatear etiquetas del eje X: "Jun 25"
  const formatXTick = (dateStr: string) =>
    new Date(dateStr + "T00:00:00").toLocaleDateString("es-CO", {
      month: "short",
      day: "numeric",
    });

  return (
    <div className="mt-6 bg-background rounded-lg border border-border p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 px-2">
        <div>
          <p className="text-xs text-muted-foreground font-sans uppercase tracking-wide">
            Historial de riesgo
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

        {/* Leyenda de colores */}
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

      {/* Gráfica */}
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

          {/* Línea de referencia en "Moderado" como zona de alerta */}
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

          <Tooltip content={<CustomTooltip />} />

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

      {/* Footer: rango de fechas */}
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
