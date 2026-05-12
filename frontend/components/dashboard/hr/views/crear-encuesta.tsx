"use client";

// ─── components/dashboard/hr/views/crear-encuesta.tsx ────────────────────────
//
// CAMBIOS vs versión anterior:
//   1. Importa `assignSurveyToTarget` del nuevo servicio.
//   2. El estado `selectedTarget` ahora usa el tipo `AssignmentTarget`
//      (discriminated union), lo que hace el código type-safe y extensible.
//   3. `handleCrearEncuesta` llama al servicio de asignación después de crear
//      la encuesta, pasando workers y grupos ya cargados para evitar refetch.
//   4. Nuevo estado `submitting` granular: "idle" | "creating" | "assigning" | "done"
//      para mostrar feedback preciso al usuario.
//   5. Sin cambios visuales — misma UI que antes.

import { useState, useEffect } from "react";
import {
  Filter,
  Search,
  ChevronDown,
  ChevronUp,
  X,
  Check,
  Loader2,
  Plus,
} from "lucide-react";
import { apiFetch, apiPost } from "@/lib/api/context";
import type {
  Area,
  Group,
  Worker,
  Survey,
  Question,
  SurveyWithQuestions,
  AssignmentTarget,
} from "@/lib/api/interfaces";
import { BUTTONS_COLORS } from "@/lib/styles/buttons-colors";
import { QuestionSearchWithCreate } from "@/components/dashboard/shared/questionsearchwithcreate";
import { assignSurveyToTarget } from "@/lib/services/assignmentService";

const C = BUTTONS_COLORS.hr;
const M = BUTTONS_COLORS.hrModal;

// ─── Tipo de estado de envío ──────────────────────────────────────────────────
// Permite mostrar feedback granular ("Creando encuesta…" vs "Asignando…")

type SubmitPhase = "idle" | "creating" | "assigning" | "done";

const PHASE_LABEL: Record<SubmitPhase, string> = {
  idle: "Crear Encuesta",
  creating: "Creando encuesta...",
  assigning: "Asignando a trabajadores...",
  done: "Crear Encuesta",
};

// ─── Component ────────────────────────────────────────────────────────────────

export function HRCrearEncuesta() {
  // ── Remote data ───────────────────────────────────────────────────────────
  const [areas, setAreas] = useState<Area[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // ── Survey fields ─────────────────────────────────────────────────────────
  const [surveyName, setSurveyName] = useState("");
  const [apertureDate, setApertureDate] = useState("");
  const [finishingDate, setFinishingDate] = useState("");

  // ── Survey selection + question picking ───────────────────────────────────
  const [selectedSurvey, setSelectedSurvey] = useState<Survey | null>(null);
  const [showSurveyModal, setShowSurveyModal] = useState(false);
  const [confirmedSurvey, setConfirmedSurvey] = useState<Survey | null>(null);
  const [selectedQuestionIds, setSelectedQuestionIds] = useState<Set<string>>(
    new Set(),
  );
  const [linkedQuestionIds, setLinkedQuestionIds] = useState<Set<string>>(
    new Set(),
  );
  const [loadingLinked, setLoadingLinked] = useState(false);
  const [surveySearch, setSurveySearch] = useState("");
  const [isFromScratch, setIsFromScratch] = useState(false);

  // ── Target (scope de asignación) ──────────────────────────────────────────
  // Usamos AssignmentTarget directamente como estado: type-safe y extensible.
  const [assignmentTarget, setAssignmentTarget] = useState<AssignmentTarget>({
    type: "empresa",
  });

  // UI auxiliar para los dropdowns del scope
  const [areaOpen, setAreaOpen] = useState(false);
  const [grupoOpen, setGrupoOpen] = useState(false);
  const [trabajadorOpen, setTrabajadorOpen] = useState(false);

  // ── Submit ────────────────────────────────────────────────────────────────
  const [submitPhase, setSubmitPhase] = useState<SubmitPhase>("idle");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // ── Fetch al montar ───────────────────────────────────────────────────────

  useEffect(() => {
    async function loadAll() {
      setLoadingData(true);
      setFetchError(null);
      try {
        const [areasData, groupsData, workersData, surveysData, questionsData] =
          await Promise.all([
            apiFetch<Area[]>("/areas/"),
            apiFetch<Group[]>("/group/"),
            apiFetch<Worker[]>("/worker/"),
            apiFetch<Survey[]>("/survey/"),
            apiFetch<Question[]>("/question/"),
          ]);
        setAreas(areasData);
        setGroups(groupsData);
        setWorkers(workersData);
        setSurveys(surveysData);
        setQuestions(questionsData);
        setApertureDate(new Date().toISOString().split("T")[0]);
      } catch (err) {
        setFetchError(
          err instanceof Error ? err.message : "Error cargando datos",
        );
      } finally {
        setLoadingData(false);
      }
    }
    loadAll();
  }, []);

  // ── Derived data ──────────────────────────────────────────────────────────

  // ── Survey list shown in the cards grid ──────────────────────────────────
  // • No search active → show only the 3 most recently created surveys
  //   (tail of the array, which reflects DB insertion order: oldest → newest).
  // • User is typing  → lift the limit and show all matching surveys.
  const RECENT_SURVEYS_LIMIT = 3;
  const isSurveySearchActive = surveySearch.trim().length > 0;

  const filteredSurveys = isSurveySearchActive
    ? surveys.filter((s) =>
        s.name.toLowerCase().includes(surveySearch.toLowerCase()),
      )
    : surveys.slice(-RECENT_SURVEYS_LIMIT);

  // Grupos y trabajadores filtrados para los dropdowns del scope
  const filteredGroups =
    assignmentTarget.type === "area"
      ? groups.filter((g) => g.id_area === assignmentTarget.areaId)
      : groups;

  const filteredWorkers =
    assignmentTarget.type === "grupo"
      ? workers.filter((w) => w.id_group === assignmentTarget.grupoId)
      : assignmentTarget.type === "area"
        ? workers.filter((w) =>
            groups.some(
              (g) =>
                g.id === w.id_group && g.id_area === assignmentTarget.areaId,
            ),
          )
        : workers;

  const modalAvailableQuestions = isFromScratch
    ? questions
    : questions.filter((q) => !linkedQuestionIds.has(q.id));

  // ── Helpers de scope ──────────────────────────────────────────────────────

  /** Devuelve el label legible del scope actual para mostrarlo en la UI */
  function getTargetLabel(target: AssignmentTarget): string {
    switch (target.type) {
      case "empresa":
        return "Toda la empresa";
      case "area":
        return areas.find((a) => a.id === target.areaId)?.name ?? "Área";
      case "grupo":
        return groups.find((g) => g.id === target.grupoId)?.name ?? "Grupo";
      case "trabajador": {
        const w = workers.find((t) => t.id === target.trabajadorId);
        return w ? `${w.name} ${w.last_names}` : "Trabajador";
      }
      default:
        return "Desconocido";
    }
  }

  // ── Handlers de encuesta ──────────────────────────────────────────────────

  const handleSelectSurvey = async (survey: Survey) => {
    setIsFromScratch(false);
    setSelectedSurvey(survey);
    setSelectedQuestionIds(new Set());
    setShowSurveyModal(true);
    setLoadingLinked(true);

    try {
      const data = await apiFetch<SurveyWithQuestions>(
        `/survey/${survey.id}/questions`,
      );
      const alreadyLinked = new Set(data.questions.map((q) => q.id));
      setLinkedQuestionIds(alreadyLinked);
      setSelectedQuestionIds(new Set(alreadyLinked));
    } catch {
      setLinkedQuestionIds(new Set());
    } finally {
      setLoadingLinked(false);
    }
  };

  const handleCreateFromScratch = () => {
    setIsFromScratch(true);
    setSelectedSurvey(null);
    setConfirmedSurvey(null);
    setSelectedQuestionIds(new Set());
    setLinkedQuestionIds(new Set());
    setSurveyName("");
    setApertureDate("");
    setFinishingDate("");
    setShowSurveyModal(true);
    setLoadingLinked(false);
  };

  const toggleQuestion = (id: string) => {
    setSelectedQuestionIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handleQuestionCreated = (newQuestion: Question) => {
    setQuestions((prev) => [...prev, newQuestion]);
    setSelectedQuestionIds((prev) => new Set([...prev, newQuestion.id]));
  };

  const handleConfirmSurvey = () => {
    setConfirmedSurvey(isFromScratch ? null : selectedSurvey);
    setShowSurveyModal(false);
  };

  // ── Handlers de scope ─────────────────────────────────────────────────────

  const handleSelectEmpresa = () => {
    setAssignmentTarget({ type: "empresa" });
    setAreaOpen(false);
    setGrupoOpen(false);
    setTrabajadorOpen(false);
  };

  const handleSelectArea = (areaId: string) => {
    setAssignmentTarget({ type: "area", areaId });
    setAreaOpen(false);
    setGrupoOpen(false);
    setTrabajadorOpen(false);
  };

  const handleSelectGrupo = (grupoId: string) => {
    setAssignmentTarget({ type: "grupo", grupoId });
    setGrupoOpen(false);
    setTrabajadorOpen(false);
  };

  const handleSelectTrabajador = (trabajadorId: string) => {
    setAssignmentTarget({ type: "trabajador", trabajadorId });
    setTrabajadorOpen(false);
  };

  // ── Submit principal ──────────────────────────────────────────────────────

  const handleCrearEncuesta = async () => {
    if (isFromScratch) {
      if (!surveyName.trim() || selectedQuestionIds.size === 0) return;
    } else {
      if (!confirmedSurvey || selectedQuestionIds.size === 0) return;
    }

    setSubmitPhase("creating");
    setSubmitError(null);
    setSubmitSuccess(false);

    try {
      let surveyId: string;

      if (isFromScratch) {
        // 1a. Crear encuesta nueva
        const today = new Date().toISOString().split("T")[0];
        const newSurvey = await apiPost<Survey>("/survey/", {
          name: surveyName.trim(),
          aperture_date: apertureDate || today,
          finishing_date: finishingDate || today,
          status: "activa",
        });
        surveyId = newSurvey.id;

        // 1b. Vincular preguntas seleccionadas
        for (const questionId of selectedQuestionIds) {
          await apiPost("/question_survey/", {
            id_survey: surveyId,
            id_question: questionId,
          });
        }
      } else {
        // Encuesta existente: solo vincular preguntas nuevas
        surveyId = confirmedSurvey!.id;
        const toLink = [...selectedQuestionIds].filter(
          (id) => !linkedQuestionIds.has(id),
        );
        for (const questionId of toLink) {
          await apiPost("/question_survey/", {
            id_survey: surveyId,
            id_question: questionId,
          });
        }
      }

      // 2. Asignar encuesta a los trabajadores según el scope seleccionado
      //    Pasamos workers y groups ya en memoria → sin refetch innecesario.
      setSubmitPhase("assigning");

      await assignSurveyToTarget(surveyId, assignmentTarget, {
        workers,
        groups,
      });

      // 3. Éxito: resetear formulario
      setSubmitSuccess(true);
      setSubmitPhase("done");

      setIsFromScratch(false);
      setConfirmedSurvey(null);
      setSelectedSurvey(null);
      setSelectedQuestionIds(new Set());
      setLinkedQuestionIds(new Set());
      setSurveyName("");
      setApertureDate("");
      setFinishingDate("");
      setAssignmentTarget({ type: "empresa" });
    } catch (err) {
      setSubmitError(
        err instanceof Error ? err.message : "Error al crear encuesta",
      );
    } finally {
      setSubmitPhase("idle");
    }
  };

  // ── Derived booleans ──────────────────────────────────────────────────────

  const surveyChosen = isFromScratch
    ? surveyName.trim().length > 0 && selectedQuestionIds.size > 0
    : confirmedSurvey !== null && selectedQuestionIds.size > 0;

  // El scope siempre está definido (tiene default "empresa"), así que
  // `canCreate` solo depende de que la encuesta esté configurada.
  const canCreate = surveyChosen;
  const isSubmitting =
    submitPhase === "creating" || submitPhase === "assigning";

  // ── Helpers de UI para los dropdowns ─────────────────────────────────────

  const currentTarget = assignmentTarget;

  // ─────────────────────────────────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────────────────────────────────

  if (fetchError) {
    return (
      <div className="p-8">
        <div className="px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {fetchError}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        CREAR ENCUESTA
      </h1>

      {/* ── Banners ─────────────────────────────────────────────────── */}

      {submitSuccess && (
        <div className="mb-6 flex items-center gap-2 px-4 py-3 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm font-sans">
          <Check className="w-4 h-4 flex-shrink-0" />
          Encuesta creada y asignada correctamente a{" "}
          <strong>{getTargetLabel(currentTarget)}</strong>.
        </div>
      )}

      {submitError && (
        <div className="mb-6 px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {submitError}
        </div>
      )}

      {/* ── Nombre ──────────────────────────────────────────────────── */}

      <div className="bg-background flex flex-col justify-center space-y-3 mb-6">
        <label className="text-2xl font-bold text-foreground font-heading">
          {"Nombre de la encuesta".toUpperCase()}
        </label>
        <input
          type="text"
          placeholder="Ej. Encuesta de bienestar mayo 2026"
          value={surveyName}
          onChange={(e) => setSurveyName(e.target.value)}
          className="px-4 py-2.5 border border-foreground/30 rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm font-sans"
        />
      </div>

      {/* ── Período ─────────────────────────────────────────────────── */}

      <div className="rounded-xl bg-background flex flex-col justify-center space-y-3 mb-6">
        <label className="text-2xl font-bold text-foreground font-heading">
          {"Período de la encuesta".toUpperCase()}
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground font-sans">
              Apertura
            </span>
            <input
              type="date"
              min={new Date().toISOString().split("T")[0]}
              value={apertureDate || new Date().toISOString().split("T")[0]}
              onChange={(e) => setApertureDate(e.target.value)}
              className="px-4 py-2.5 border border-foreground/30 rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm font-sans"
            />
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground font-sans">
              Cierre
            </span>
            <input
              type="date"
              value={finishingDate}
              min={apertureDate || undefined}
              onChange={(e) => setFinishingDate(e.target.value)}
              className="px-4 py-2.5 border border-foreground/30 rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm font-sans"
            />
          </div>
        </div>
      </div>

      {/* ── Elegir preguntas ─────────────────────────────────────────── */}

      <div className="flex items-center justify-between mb-3">
        <h2
          className="text-2xl font-bold text-foreground"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          ELEGIR PREGUNTAS
        </h2>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search
              size={20}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <input
              type="text"
              placeholder="Buscar"
              value={surveySearch}
              onChange={(e) => setSurveySearch(e.target.value)}
              className="pl-10 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {/* Crear desde cero */}
        <button
          onClick={handleCreateFromScratch}
          className={`p-8 rounded-xl border-2 transition-all text-center relative flex flex-col items-center justify-center gap-2 ${
            isFromScratch
              ? `${C.button} border-[#7485bb]`
              : "bg-background border-dashed border-foreground/30 text-foreground hover:border-[#8795C7] hover:bg-secondary/40"
          }`}
        >
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${
              isFromScratch
                ? "border-white/60 bg-white/20"
                : "border-foreground/30"
            }`}
          >
            <Plus size={22} strokeWidth={2} />
          </div>
          <span className="font-medium text-base leading-tight">
            Nuevas preguntas
          </span>
          {isFromScratch && (
            <div className="absolute top-2 right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
              <Check size={14} className="text-primary-foreground" />
            </div>
          )}
        </button>

        {/* Skeleton de carga */}
        {loadingData ? (
          <div className="p-8 rounded-xl border-2 border-foreground/10 flex items-center justify-center text-muted-foreground gap-3">
            <Loader2 className="animate-spin w-5 h-5" />
            <span className="font-sans text-sm">Cargando datos...</span>
          </div>
        ) : (
          filteredSurveys.length === 0 && (
            <p className="text-muted-foreground text-sm font-sans col-span-1 flex items-center">
              {isSurveySearchActive
                ? "No se encontraron encuestas con ese nombre."
                : "No hay encuestas disponibles."}
            </p>
          )
        )}

        {/* Encuestas existentes */}
        {filteredSurveys.map((survey) => (
          <button
            key={survey.id}
            onClick={() => handleSelectSurvey(survey)}
            className={`p-8 rounded-xl border-2 transition-all text-center relative ${
              !isFromScratch && confirmedSurvey?.id === survey.id
                ? `${C.button} border-[#7485bb]`
                : "bg-background border-foreground/30 text-foreground hover:border-[#8795C7]"
            }`}
          >
            <span className="font-medium text-lg">
              Preguntas de {survey.name}
            </span>
            {!isFromScratch && confirmedSurvey?.id === survey.id && (
              <div className="absolute top-2 right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                <Check size={14} className="text-primary-foreground" />
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Hint: tells the user how many surveys are visible and how to see more */}
      {!loadingData && surveys.length > RECENT_SURVEYS_LIMIT && (
        <p className="text-xs text-muted-foreground font-sans mb-4 pl-0.5">
          {isSurveySearchActive
            ? `${filteredSurveys.length} encuesta${filteredSurveys.length !== 1 ? "s" : ""} encontrada${filteredSurveys.length !== 1 ? "s" : ""}`
            : `Mostrando las ${RECENT_SURVEYS_LIMIT} más recientes de ${surveys.length}. Busca para ver todas.`}
        </p>
      )}

      {/* ── Dirigida a ──────────────────────────────────────────────── */}

      <h2
        className="text-2xl font-bold text-foreground mb-4"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        DIRIGIDA A
      </h2>

      <div className="space-y-3 max-w-2xl">
        {/* Toda la empresa */}
        <button
          onClick={handleSelectEmpresa}
          className={`w-full px-4 py-3 border rounded-lg text-left transition-colors ${
            currentTarget.type === "empresa"
              ? `${C.button} border-[#7485bb]`
              : "border-foreground/30 bg-background text-foreground hover:bg-secondary"
          }`}
        >
          Toda la empresa
        </button>

        {/* Área particular */}
        <div className="relative">
          <button
            onClick={() => {
              setAreaOpen(!areaOpen);
              setGrupoOpen(false);
              setTrabajadorOpen(false);
            }}
            className={`w-full flex items-center justify-between px-4 py-3 border rounded-lg transition-colors ${
              currentTarget.type === "area"
                ? `${C.button} border-[#7485bb]`
                : "border-foreground/30 bg-background text-foreground hover:bg-secondary"
            }`}
          >
            <span>
              {currentTarget.type === "area"
                ? getTargetLabel(currentTarget)
                : "Área particular"}
            </span>
            {areaOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          {areaOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-foreground/30 rounded-lg shadow-lg z-10 overflow-hidden">
              {areas.map((area) => (
                <button
                  key={area.id}
                  onClick={() => handleSelectArea(area.id)}
                  className={`w-full text-left px-4 py-3 hover:bg-secondary transition-colors ${
                    currentTarget.type === "area" &&
                    currentTarget.areaId === area.id
                      ? "bg-[#E0D7F9]"
                      : ""
                  }`}
                >
                  {area.name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Grupo particular */}
        <div className="relative">
          <button
            onClick={() => {
              setGrupoOpen(!grupoOpen);
              setAreaOpen(false);
              setTrabajadorOpen(false);
            }}
            className={`w-full flex items-center justify-between px-4 py-3 border rounded-lg transition-colors ${
              currentTarget.type === "grupo"
                ? `${C.button} border-[#7485bb]`
                : "border-foreground/30 bg-background text-foreground hover:bg-secondary"
            }`}
          >
            <span>
              {currentTarget.type === "grupo"
                ? getTargetLabel(currentTarget)
                : "Grupo particular"}
            </span>
            {grupoOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          {grupoOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-foreground/30 rounded-lg shadow-lg z-10 overflow-hidden">
              {filteredGroups.map((grupo) => (
                <button
                  key={grupo.id}
                  onClick={() => handleSelectGrupo(grupo.id)}
                  className={`w-full text-left px-4 py-3 hover:bg-secondary transition-colors ${
                    currentTarget.type === "grupo" &&
                    currentTarget.grupoId === grupo.id
                      ? "bg-[#E0D7F9]"
                      : ""
                  }`}
                >
                  {grupo.name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Trabajador particular */}
        <div className="relative">
          <button
            onClick={() => {
              setTrabajadorOpen(!trabajadorOpen);
              setAreaOpen(false);
              setGrupoOpen(false);
            }}
            className={`w-full flex items-center justify-between px-4 py-3 border rounded-lg transition-colors ${
              currentTarget.type === "trabajador"
                ? `${C.button} border-[#7485bb]`
                : "border-foreground/30 bg-background text-foreground hover:bg-secondary"
            }`}
          >
            <span>
              {currentTarget.type === "trabajador"
                ? getTargetLabel(currentTarget)
                : "Trabajador particular"}
            </span>
            {trabajadorOpen ? (
              <ChevronUp size={20} />
            ) : (
              <ChevronDown size={20} />
            )}
          </button>
          {trabajadorOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-foreground/30 rounded-lg shadow-lg z-10 overflow-hidden max-h-48 overflow-y-auto">
              {filteredWorkers.map((worker) => (
                <button
                  key={worker.id}
                  onClick={() => handleSelectTrabajador(worker.id)}
                  className={`w-full text-left px-4 py-3 hover:bg-secondary transition-colors ${
                    currentTarget.type === "trabajador" &&
                    currentTarget.trabajadorId === worker.id
                      ? "bg-[#E0D7F9]"
                      : ""
                  }`}
                >
                  {worker.name} {worker.last_names}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* ── Resumen del scope seleccionado ─────────────────────────── */}
        {currentTarget.type !== "empresa" && (
          <p className="text-xs text-muted-foreground font-sans pl-1">
            La encuesta será asignada a:{" "}
            <span className="font-medium text-foreground">
              {getTargetLabel(currentTarget)}
            </span>
          </p>
        )}

        {/* ── Botón principal ──────────────────────────────────────────── */}
        <button
          onClick={handleCrearEncuesta}
          disabled={!canCreate || isSubmitting}
          className={`w-full mt-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
            canCreate && !isSubmitting
              ? `${C.button}`
              : "bg-secondary text-muted-foreground cursor-not-allowed"
          }`}
        >
          {isSubmitting && <Loader2 size={16} className="animate-spin" />}
          {PHASE_LABEL[submitPhase]}
        </button>
      </div>

      {/* ── Modal selector de preguntas ──────────────────────────────── */}

      {showSurveyModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-xl p-6 w-full max-w-2xl max-h-[90vh] flex flex-col relative">
            <button
              onClick={() => setShowSurveyModal(false)}
              className={`absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center transition-colors ${M.button}`}
            >
              <X size={18} />
            </button>

            <h2
              className="text-2xl font-bold text-foreground mb-1"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              {isFromScratch
                ? "NUEVA ENCUESTA DESDE CERO"
                : selectedSurvey?.name.toUpperCase()}
            </h2>

            <p className="text-sm text-muted-foreground mb-4 font-sans">
              {isFromScratch
                ? "Elige o crea las preguntas para esta encuesta"
                : "Selecciona las preguntas que formarán parte de esta encuesta"}
            </p>

            <div className="flex-1 overflow-y-auto mb-4">
              {/* Preguntas ya vinculadas (modo encuesta existente) */}
              {!isFromScratch && linkedQuestionIds.size > 0 && (
                <div className="mb-3">
                  <p className="text-xs text-muted-foreground font-sans mb-2">
                    Ya vinculadas ({linkedQuestionIds.size}):
                  </p>

                  {loadingLinked ? (
                    <div className="flex items-center gap-2 px-3 py-2 border border-primary/30 rounded-lg">
                      <Loader2 size={16} className="animate-spin" />
                      <span className="text-sm font-sans">
                        Cargando preguntas vinculadas...
                      </span>
                    </div>
                  ) : (
                    <div className="space-y-1">
                      {questions
                        .filter((q) => linkedQuestionIds.has(q.id))
                        .map((q) => (
                          <div
                            key={q.id}
                            className="flex items-center gap-2 px-3 py-2 border border-primary/30 bg-primary/5 rounded-lg"
                          >
                            <Check
                              size={12}
                              className="text-primary flex-shrink-0"
                            />
                            <span className="text-xs text-foreground truncate">
                              {q.text}
                            </span>
                          </div>
                        ))}
                    </div>
                  )}

                  <hr className="my-3 border-border" />
                </div>
              )}

              {loadingLinked ? (
                <div className="flex items-center justify-center gap-2 py-8 text-muted-foreground">
                  <Loader2 size={32} className="animate-spin" />
                </div>
              ) : (
                <QuestionSearchWithCreate
                  questions={modalAvailableQuestions}
                  selectedIds={
                    isFromScratch
                      ? selectedQuestionIds
                      : new Set(
                          [...selectedQuestionIds].filter(
                            (id) => !linkedQuestionIds.has(id),
                          ),
                        )
                  }
                  disabledIds={isFromScratch ? new Set() : linkedQuestionIds}
                  onToggle={toggleQuestion}
                  onCreated={handleQuestionCreated}
                />
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between pt-2 border-t border-border">
              <span className="text-sm text-muted-foreground font-sans">
                {selectedQuestionIds.size} pregunta
                {selectedQuestionIds.size !== 1 ? "s" : ""} seleccionada
                {selectedQuestionIds.size !== 1 ? "s" : ""}
              </span>

              <button
                onClick={handleConfirmSurvey}
                disabled={selectedQuestionIds.size === 0}
                className={`px-6 py-2 rounded-lg font-medium text-white text-sm transition-colors ${
                  selectedQuestionIds.size > 0
                    ? "bg-accent text-foreground hover:bg-accent/80"
                    : "bg-secondary text-muted-foreground cursor-not-allowed"
                }`}
              >
                {isFromScratch ? "Confirmar preguntas" : "Elegir Encuesta"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
