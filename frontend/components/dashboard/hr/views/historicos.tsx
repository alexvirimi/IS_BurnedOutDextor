"use client";

import { useState, useEffect } from "react";
import { Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { BurnoutLineChart } from "@/components/dashboard/shared/burnout-line-chart";
import { ReporteList } from "@/components/dashboard/shared/reporte-list";
import {
  useHistoricoReportsHR,
  type HistoricoScope,
  type Reporte,
} from "@/hooks/useReportes";
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
  // ── Reference data for the scope selector ──────────────────────────────
  const [areas, setAreas] = useState<Area[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [refLoading, setRefLoading] = useState(true);

  // ── Active scope and selected report ──────────────────────────────────
  const [scope, setScope] = useState<HistoricoScope | null>(null);
  const [selectedReporte, setSelectedReporte] = useState<Reporte | null>(null);

  // ── Fetch reference data once ─────────────────────────────────────────
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

  // ── Set default scope when type changes and reference data is ready ───
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

  const { reportes, loading, error } = useHistoricoReportsHR(scope);

  // Auto-select first report when list changes
  useEffect(() => {
    setSelectedReporte(reportes.length > 0 ? reportes[0] : null);
  }, [reportes]);

  // ── Dropdown open state ──────────────────────────────────────────────────
  const [dropdownOpen, setDropdownOpen] = useState(false);

  // ── Derived: label of the currently selected scope item ──────────────────
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

  // ── Scope selector — one dropdown trigger matching "Dirigida a" style ────
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

    items = items.filter((item) => item.id !== activeId);

    if (items.length === 0) return null;

    return (
      <div className="relative mb-6">
        <button
          onClick={() => setDropdownOpen((v) => !v)}
          className={`w-full flex items-center justify-between px-4 py-3 border rounded-lg transition-colors ${"border-foreground/30 bg-background text-foreground hover:bg-secondary"}`}
        >
          <span>
            {scope?.type ? type.charAt(0).toUpperCase() + type.slice(1) : ""}:{" "}
            {selectedLabel ?? placeholder}
          </span>
          {dropdownOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>

        {dropdownOpen && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-foreground/30 rounded-lg shadow-lg z-10 overflow-hidden max-h-60 overflow-y-auto">
            {items.map((item) => (
              <button
                key={item.id}
                onClick={() => onSelect(item.id)}
                className={`w-full text-left px-4 py-3 hover:bg-secondary transition-colors ${
                  item.id === activeId ? "bg-[#E0D7F9]" : ""
                }`}
              >
                {scope?.type
                  ? type.charAt(0).toUpperCase() + type.slice(1)
                  : ""}
                : {item.label}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-6"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        VISUALIZACIÓN
      </h1>

      {/* Power BI placeholder — shows selected report name */}
      <div className="mb-4">
        <BurnoutLineChart title={selectedReporte?.nombre} />
      </div>

      {/* Scope selector */}
      {renderScopeSelector()}

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-3 mt-8 text-muted-foreground">
          <Loader2 className="animate-spin w-4 h-4" />
          <span className="text-sm font-sans">Cargando reportes...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-8 px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {error}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && reportes.length === 0 && scope && (
        <p className="mt-8 text-sm text-muted-foreground font-sans">
          No hay encuestas completadas por todos los miembros en este{" "}
          {type === "areas"
            ? "área"
            : type === "grupos"
              ? "grupo"
              : "trabajador"}
          .
        </p>
      )}

      {/* Report list */}
      {!loading && reportes.length > 0 && (
        <ReporteList
          reportes={reportes}
          selectedReporte={selectedReporte ?? undefined}
          onSelectReporte={(r) => setSelectedReporte(r)}
          title={`REPORTES · ${SUBTITLES[type].toUpperCase()}`}
        />
      )}
    </div>
  );
}
