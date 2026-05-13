"use client";

/**
 * HRHistoricos — UPDATED
 * ───────────────────────
 * Key changes:
 *   1. `useBurnoutChart` replaces the placeholder chart.
 *   2. Scope is derived from the current `type` + selected entity id.
 *   3. Clicking a Reporte in <ReporteList> still works — it sets
 *      `selectedReporte` which is used for the chart title.
 *      The chart data itself comes from the scope (area / group / worker),
 *      not from the individual report — matching the spec:
 *      "display the aggregated mean of all workers in that context".
 *   4. No visual / layout changes.
 */

import { useState, useEffect, useCallback, useMemo } from "react";
import { Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { BurnoutLineChart } from "@/components/dashboard/shared/burnout-line-chart";
import { ReporteList } from "@/components/dashboard/shared/reporte-list";
import {
  useHistoricoReportsHR,
  type HistoricoScope,
  type Reporte,
} from "@/hooks/useReportes";
import {
  useBurnoutChart,
  type ChartScope,
  scopeToMode,
} from "@/hooks/useBurnoutChart";
import { apiFetch } from "@/lib/api/context";
import type { Area, Group, Worker } from "@/lib/api/interfaces";

type HistoricoType = "areas" | "grupos" | "trabajadores";

const SUBTITLES: Record<HistoricoType, string> = {
  areas: "Áreas",
  grupos: "Grupos",
  trabajadores: "Trabajadores",
};

interface HRHistoricosProps {
  type: HistoricoType;
}

export function HRHistoricos({ type }: HRHistoricosProps) {
  // ── Reference data ────────────────────────────────────────────────────────
  const [areas, setAreas] = useState<Area[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [refLoading, setRefLoading] = useState(true);

  // ── Scope state ───────────────────────────────────────────────────────────
  const [scope, setScope] = useState<HistoricoScope | null>(null);
  const [selectedReporte, setSelectedReporte] = useState<Reporte | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  // ── Load reference data ───────────────────────────────────────────────────
  useEffect(() => {
    async function load() {
      setRefLoading(true);
      try {
        const [areasData, groupsData, workersData] = await Promise.all([
          apiFetch<Area[]>("/areas/"),
          apiFetch<Group[]>("/group/"),
          apiFetch<Worker[]>("/worker/"),
        ]);
        setAreas(areasData);
        setGroups(groupsData);
        setWorkers(workersData);
      } finally {
        setRefLoading(false);
      }
    }
    load();
  }, []);

  // ── Set default scope when type changes ───────────────────────────────────
  useEffect(() => {
    if (refLoading) return;
    setSelectedReporte(null);
    setDropdownOpen(false);

    if (type === "areas" && areas.length > 0) {
      setScope({ type: "area", areaId: areas[0].id });
    } else if (type === "grupos" && groups.length > 0) {
      setScope({ type: "grupo", grupoId: groups[0].id });
    } else if (type === "trabajadores" && workers.length > 0) {
      setScope({ type: "trabajador", trabajadorId: workers[0].id });
    } else {
      setScope(null);
    }
  }, [type, refLoading, areas, groups, workers]);

  // ── Report list for this scope ─────────────────────────────────────────────
  const {
    reportes,
    loading: listLoading,
    error: listError,
  } = useHistoricoReportsHR(scope);

  useEffect(() => {
    setSelectedReporte(reportes.length > 0 ? reportes[0] : null);
  }, [reportes]);

  // ── Derive ChartScope from HistoricoScope ──────────────────────────────────
  // This is the translation layer between "report filter scope" (which surveys
  // to list) and "chart data scope" (which endpoint to hit for the graph).
  const chartScope = useMemo<ChartScope | null>(() => {
    if (!scope) return null;
    switch (scope.type) {
      case "area":
        return { type: "area", areaId: scope.areaId };
      case "grupo":
        return { type: "group", groupId: scope.grupoId };
      case "trabajador":
        return { type: "worker", workerId: scope.trabajadorId };
      default:
        return null;
    }
  }, [scope]);

  // ── Chart data ─────────────────────────────────────────────────────────────
  // We use selectedReporte.id as the trigger key so the chart refreshes when
  // the user picks a different report (even within the same scope).
  // When no reporte is selected yet (null), chart shows "select a report".
  const {
    data: chartData,
    loading: chartLoading,
    error: chartError,
  } = useBurnoutChart(
    chartScope ?? { type: "self" }, // fallback; guarded by reporteId=null when chartScope is null
    chartScope !== null ? (selectedReporte?.id ?? null) : null,
  );

  // ── Derived labels ────────────────────────────────────────────────────────
  const selectedLabel = (() => {
    if (!scope) return null;
    if (scope.type === "area")
      return areas.find((a) => a.id === scope.areaId)?.name ?? null;
    if (scope.type === "grupo")
      return groups.find((g) => g.id === scope.grupoId)?.name ?? null;
    if (scope.type === "trabajador") {
      const w = workers.find((w) => w.id === scope.trabajadorId);
      return w ? `${w.name} ${w.last_names}` : null;
    }
    return null;
  })();

  // ── Scope selector (unchanged UI) ─────────────────────────────────────────
  const renderScopeSelector = () => {
    if (refLoading) return null;

    type Item = { id: string; label: string };
    let items: Item[] = [];
    let placeholder = "";
    let onSelect: (id: string) => void = () => {};
    let activeId: string | null = null;

    if (type === "areas") {
      items = areas.map((a) => ({ id: a.id, label: a.name }));
      placeholder = "Seleccionar área";
      onSelect = (id) => {
        setScope({ type: "area", areaId: id });
        setDropdownOpen(false);
      };
      activeId = scope?.type === "area" ? scope.areaId : null;
    } else if (type === "grupos") {
      items = groups.map((g) => ({ id: g.id, label: g.name }));
      placeholder = "Seleccionar grupo";
      onSelect = (id) => {
        setScope({ type: "grupo", grupoId: id });
        setDropdownOpen(false);
      };
      activeId = scope?.type === "grupo" ? scope.grupoId : null;
    } else if (type === "trabajadores") {
      items = workers.map((w) => ({
        id: w.id,
        label: `${w.name} ${w.last_names}`,
      }));
      placeholder = "Seleccionar trabajador";
      onSelect = (id) => {
        setScope({ type: "trabajador", trabajadorId: id });
        setDropdownOpen(false);
      };
      activeId = scope?.type === "trabajador" ? scope.trabajadorId : null;
    }

    const filteredItems = items.filter((item) => item.id !== activeId);
    if (filteredItems.length === 0) return null;

    return (
      <div className="relative mb-6">
        <button
          onClick={() => setDropdownOpen((v) => !v)}
          className="w-full flex items-center justify-between px-4 py-3 border border-foreground/30 rounded-lg bg-background text-foreground hover:bg-secondary transition-colors"
        >
          <span>
            {scope?.type ? type.charAt(0).toUpperCase() + type.slice(1) : ""}
            {selectedLabel ? `: ${selectedLabel}` : `: ${placeholder}`}
          </span>
          {dropdownOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>

        {dropdownOpen && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-foreground/30 rounded-lg shadow-lg z-10 overflow-hidden max-h-60 overflow-y-auto">
            {filteredItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onSelect(item.id)}
                className="w-full text-left px-4 py-3 hover:bg-secondary transition-colors"
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}: {item.label}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  };

  const chartMode = chartScope ? scopeToMode(chartScope) : "self";

  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-6"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        VISUALIZACIÓN
      </h1>

      {/* Chart — aggregated data for the selected scope */}
      <BurnoutLineChart
        dataSource={chartData}
        mode={chartMode}
        title={selectedReporte?.nombre ?? selectedLabel ?? undefined}
        loading={chartLoading}
      />

      {chartError && (
        <div className="mt-4 px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {chartError}
        </div>
      )}

      <div className="mt-6">{renderScopeSelector()}</div>

      {listLoading && (
        <div className="flex items-center gap-3 mt-4 text-muted-foreground">
          <Loader2 className="animate-spin w-4 h-4" />
          <span className="text-sm font-sans">Cargando reportes...</span>
        </div>
      )}

      {listError && (
        <div className="mt-4 px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {listError}
        </div>
      )}

      {!listLoading && !listError && reportes.length === 0 && scope && (
        <p className="mt-4 text-sm text-muted-foreground font-sans">
          No hay encuestas completadas por todos los miembros en este{" "}
          {type === "areas"
            ? "área"
            : type === "grupos"
              ? "grupo"
              : "trabajador"}
          .
        </p>
      )}

      {!listLoading && reportes.length > 0 && (
        <ReporteList
          reportes={reportes}
          selectedReporte={selectedReporte ?? undefined}
          onSelectReporte={setSelectedReporte} // ← triggers chart title update
          title={`REPORTES · ${SUBTITLES[type].toUpperCase()}`}
        />
      )}
    </div>
  );
}
