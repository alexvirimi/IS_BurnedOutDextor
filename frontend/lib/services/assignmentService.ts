// ─── lib/services/assignmentService.ts ───────────────────────────────────────
//
// Servicio puro (sin estado React) que encapsula toda la lógica de:
//   1. Filtrar trabajadores según un AssignmentTarget
//   2. Llamar al endpoint POST /survey-assignment/assign
//
// Diseñado para ser extensible: añadir un nuevo scope (cargo, sede, equipo)
// solo requiere agregar un case en `filterWorkers` y el tipo en AssignmentTarget.

import { apiFetch, apiPostJson } from "@/lib/api/context";
import type {
  Worker,
  Group,
  AssignmentTarget,
  SurveyWorkerAssignment,
} from "@/lib/api/interfaces";

// ─── Tipos internos ───────────────────────────────────────────────────────────

export interface AssignmentContext {
  /** Trabajadores ya cargados en memoria (evita refetch si el padre los tiene) */
  workers: Worker[];
  /** Grupos ya cargados en memoria (necesarios para filtrar por área) */
  groups: Group[];
}

export interface AssignSurveyResult {
  /** Asignaciones creadas (puede ser [] si todos ya estaban asignados) */
  assignments: SurveyWorkerAssignment[];
  /** IDs de trabajadores a los que se intentó asignar */
  targetWorkerIds: string[];
}

// ─── Filtros ──────────────────────────────────────────────────────────────────

/**
 * Devuelve los IDs de los trabajadores que corresponden al scope seleccionado.
 * Función pura — sin side effects, fácil de testear.
 *
 * Extensión futura:
 *   - Para "cargo": añadir `cargo_id` a Worker y filtrar por él.
 *   - Para "sede": añadir `sede_id` a Worker (o a Company) y filtrar.
 *   - Para "equipo": puede ser otro nivel de Group anidado.
 */
export function filterWorkersByTarget(
  target: AssignmentTarget,
  workers: Worker[],
  groups: Group[],
): string[] {
  switch (target.type) {
    case "empresa":
      // Todos los trabajadores de la empresa
      return workers.map((w) => w.id);

    case "area": {
      // Trabajadores cuyos grupos pertenecen a esta área
      const groupIdsInArea = new Set(
        groups.filter((g) => g.id_area === target.areaId).map((g) => g.id),
      );
      return workers
        .filter((w) => groupIdsInArea.has(w.id_group))
        .map((w) => w.id);
    }

    case "grupo":
      // Trabajadores del grupo específico
      return workers
        .filter((w) => w.id_group === target.grupoId)
        .map((w) => w.id);

    case "trabajador":
      // Un solo trabajador
      return [target.trabajadorId];

    // ── Casos futuros (no implementados, lanzar error descriptivo) ────────────
    case "cargo":
      throw new Error(
        "Filtro por cargo aún no implementado. " +
          "Añadir campo cargo_id a Worker y completar este case.",
      );
    case "sede":
      throw new Error(
        "Filtro por sede aún no implementado. " +
          "Añadir campo sede_id a Worker/Company y completar este case.",
      );
    case "equipo":
      throw new Error(
        "Filtro por equipo aún no implementado. " +
          "Definir estructura de equipos y completar este case.",
      );

    default: {
      // Exhaustiveness check en tiempo de compilación
      const _exhaustive: never = target;
      throw new Error(
        `Scope de asignación desconocido: ${JSON.stringify(_exhaustive)}`,
      );
    }
  }
}

// ─── Fetch helpers (con lazy-load) ────────────────────────────────────────────

/**
 * Si el padre ya tiene workers/groups en memoria los reutiliza.
 * Si no, los fetcha. Evita requests duplicadas.
 */
async function resolveContext(
  partial: Partial<AssignmentContext>,
): Promise<AssignmentContext> {
  const [workers, groups] = await Promise.all([
    partial.workers?.length
      ? Promise.resolve(partial.workers)
      : apiFetch<Worker[]>("/worker/"),
    partial.groups?.length
      ? Promise.resolve(partial.groups)
      : apiFetch<Group[]>("/group/"),
  ]);
  return { workers, groups };
}

// ─── Servicio principal ───────────────────────────────────────────────────────

/**
 * Asigna una encuesta a los trabajadores que corresponden al scope indicado.
 *
 * @param surveyId  - ID de la encuesta recién creada (o existente)
 * @param target    - Scope de asignación (empresa, área, grupo, trabajador)
 * @param ctx       - Workers/groups ya en memoria (opcional, evita refetch)
 *
 * @returns AssignSurveyResult con las asignaciones creadas y los IDs objetivo
 * @throws Error si el fetch falla o no hay trabajadores para el scope
 */
export async function assignSurveyToTarget(
  surveyId: string,
  target: AssignmentTarget,
  ctx: Partial<AssignmentContext> = {},
): Promise<AssignSurveyResult> {
  // 1. Resolver workers y grupos (de memoria o fetch)
  const context = await resolveContext(ctx);

  // 2. Filtrar según el scope
  const workerIds = filterWorkersByTarget(
    target,
    context.workers,
    context.groups,
  );

  if (workerIds.length === 0) {
    // No es un error fatal — puede que el grupo esté vacío
    return { assignments: [], targetWorkerIds: [] };
  }

  // 3. Llamar al endpoint — espera JSON body
  const assignments = await apiPostJson<SurveyWorkerAssignment[]>(
    "/survey-assignment/assign",
    {
      id_survey: surveyId,
      worker_ids: workerIds,
    },
  );

  return { assignments, targetWorkerIds: workerIds };
}
