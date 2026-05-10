"use client";

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
  CalendarRange,
} from "lucide-react";
import { apiFetch, apiPost } from "@/lib/api/context";
import {
  Area,
  Group,
  Worker,
  Survey,
  Question,
  SurveyWithQuestions,
} from "@/lib/api/interfaces";
import { BUTTONS_COLORS } from "@/lib/styles/buttons-colors";

// Main view buttons → hr palette (#8795C7)
const C = BUTTONS_COLORS.hr;
// Modal buttons → hrModal palette (#E0D7F9)
const M = BUTTONS_COLORS.hrModal;

type TargetType = "empresa" | "area" | "grupo" | "trabajador";

// ─── Component ────────────────────────────────────────────────────────────────

export function HRCrearEncuesta() {
  // Remote data
  const [areas, setAreas] = useState<Area[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // New survey fields (from-scratch flow)
  const [surveyName, setSurveyName] = useState("");
  const [apertureDate, setApertureDate] = useState("");
  const [finishingDate, setFinishingDate] = useState("");

  // Survey selection + question picking
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
  const [questionSearch, setQuestionSearch] = useState("");

  // "Create from scratch" mode
  const [isFromScratch, setIsFromScratch] = useState(false);

  // Targeting
  const [areaOpen, setAreaOpen] = useState(false);
  const [grupoOpen, setGrupoOpen] = useState(false);
  const [trabajadorOpen, setTrabajadorOpen] = useState(false);
  const [selectedTarget, setSelectedTarget] = useState<TargetType>("empresa");
  const [selectedArea, setSelectedArea] = useState<string | null>(null);
  const [selectedGrupo, setSelectedGrupo] = useState<string | null>(null);
  const [selectedTrabajador, setSelectedTrabajador] = useState<string | null>(
    null,
  );

  // Submission state
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // ─── Fetch all reference data on mount ──────────────────────────────────────

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

  // ─── Derived data ────────────────────────────────────────────────────────────

  const filteredQuestions = questions.filter((q) =>
    q.text.toLowerCase().includes(questionSearch.toLowerCase()),
  );

  const filteredSurveys = surveys.filter((s) =>
    s.name.toLowerCase().includes(surveySearch.toLowerCase()),
  );

  const filteredGroups = selectedArea
    ? groups.filter((g) => g.id_area === selectedArea)
    : groups;

  const filteredWorkers = selectedGrupo
    ? workers.filter((w) => w.id_group === selectedGrupo)
    : selectedArea
      ? workers.filter((w) =>
          groups.some((g) => g.id === w.id_group && g.id_area === selectedArea),
        )
      : workers;

  // ─── Handlers ────────────────────────────────────────────────────────────────

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

  /** Open the question-picker modal in "from scratch" mode */
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

  const handleConfirmSurvey = () => {
    if (isFromScratch) {
      // No backend survey object yet; we just close the modal.
      // The name + questions will be sent on final submit.
      setConfirmedSurvey(null);
    } else {
      setConfirmedSurvey(selectedSurvey);
    }
    setShowSurveyModal(false);
  };

  const handleSelectTarget = (type: TargetType, id?: string) => {
    setSelectedTarget(type);
    if (type === "area" && id) {
      setSelectedArea(id);
      setSelectedGrupo(null);
      setSelectedTrabajador(null);
      setAreaOpen(false);
    } else if (type === "grupo" && id) {
      setSelectedGrupo(id);
      setSelectedTrabajador(null);
      setGrupoOpen(false);
    } else if (type === "trabajador" && id) {
      setSelectedTrabajador(id);
      setTrabajadorOpen(false);
    } else if (type === "empresa") {
      setSelectedArea(null);
      setSelectedGrupo(null);
      setSelectedTrabajador(null);
    }
  };

  // ─── Submit ───────────────────────────────────────────────────────────────────

  const handleCrearEncuesta = async () => {
    if (isFromScratch) {
      if (!surveyName.trim() || selectedQuestionIds.size === 0) return;
    } else {
      if (!confirmedSurvey || selectedQuestionIds.size === 0) return;
    }

    setSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);

    try {
      if (isFromScratch) {
        // 1. Create the survey first
        const today = new Date().toISOString().split("T")[0];
        const newSurvey = await apiPost<Survey>("/survey/", {
          name: surveyName.trim(),
          aperture_date: apertureDate || today,
          finishing_date: finishingDate || today,
          status: "Activa",
        });

        // 2. Link selected questions
        for (const questionId of selectedQuestionIds) {
          await apiPost("/question_survey/", {
            id_survey: newSurvey.id,
            id_question: questionId,
          });
        }
      } else {
        // Existing survey: only link questions that are NOT already linked
        const toLink = [...selectedQuestionIds].filter(
          (id) => !linkedQuestionIds.has(id),
        );
        for (const questionId of toLink) {
          await apiPost("/question_survey/", {
            id_survey: confirmedSurvey!.id,
            id_question: questionId,
          });
        }
      }

      setSubmitSuccess(true);
      // Reset form
      setIsFromScratch(false);
      setConfirmedSurvey(null);
      setSelectedSurvey(null);
      setSelectedQuestionIds(new Set());
      setLinkedQuestionIds(new Set());
      setSurveyName("");
      setApertureDate("");
      setFinishingDate("");
      setSelectedTarget("empresa");
      setSelectedArea(null);
      setSelectedGrupo(null);
      setSelectedTrabajador(null);
    } catch (err) {
      setSubmitError(
        err instanceof Error ? err.message : "Error al crear encuesta",
      );
    } finally {
      setSubmitting(false);
    }
  };

  // ─── Derived booleans ─────────────────────────────────────────────────────────

  const surveyChosen = isFromScratch
    ? surveyName.trim().length > 0 && selectedQuestionIds.size > 0
    : confirmedSurvey !== null && selectedQuestionIds.size > 0;

  const targetChosen =
    selectedTarget === "empresa" ||
    (selectedTarget === "area" && selectedArea) ||
    (selectedTarget === "grupo" && selectedGrupo) ||
    (selectedTarget === "trabajador" && selectedTrabajador);

  const canCreate = surveyChosen && targetChosen;

  // ─── Chosen survey label for display ─────────────────────────────────────────

  const chosenLabel = isFromScratch
    ? surveyName.trim() || "Nueva encuesta"
    : (confirmedSurvey?.name ?? null);

  // ─── Error state ──────────────────────────────────────────────────────────────

  if (fetchError) {
    return (
      <div className="p-8">
        <div className="px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {fetchError}
        </div>
      </div>
    );
  }

  // ─── Render ───────────────────────────────────────────────────────────────────

  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        CREAR ENCUESTA
      </h1>

      {/* Success banner */}
      {submitSuccess && (
        <div className="mb-6 flex items-center gap-2 px-4 py-3 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm font-sans">
          <Check className="w-4 h-4 flex-shrink-0" />
          Encuesta configurada correctamente. Las preguntas han sido vinculadas.
        </div>
      )}

      {/* Error banner */}
      {submitError && (
        <div className="mb-6 px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {submitError}
        </div>
      )}

      <div className="flex flex-col gap-3 space-y-3 mb-6">
        {/* ── Survey name card ── */}
        <div className="bg-background flex flex-col justify-center space-y-3">
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

        {/* ── Date range card ── */}
        <div className="rounded-xl bg-background flex flex-col justify-center space-y-3">
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
                value={apertureDate}
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
      </div>

      {/* ── Surveys section ───────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-2xl font-bold text-foreground"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          ELEGIR PREGUNTAS
        </h2>
        <div className="flex items-center gap-2">
          <button className="p-2 rounded-lg transition-colors">
            <Filter size={20} className="text-foreground" />
          </button>
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
        {/* ── Create-from-scratch card ── */}
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

        {/* Loading skeleton */}
        {loadingData ? (
          <div className="p-8 rounded-xl border-2 border-foreground/10 flex items-center justify-center text-muted-foreground gap-3">
            <Loader2 className="animate-spin w-5 h-5" />
            <span className="font-sans text-sm">Cargando datos...</span>
          </div>
        ) : (
          filteredSurveys.length === 0 && (
            <p className="text-muted-foreground text-sm font-sans col-span-1 flex items-center">
              No hay encuestas disponibles.
            </p>
          )
        )}

        {/* Existing survey cards */}
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

      {/* ── Target section ────────────────────────────────────────────────── */}
      <h2
        className="text-2xl font-bold text-foreground mb-4"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        DIRIGIDA A
      </h2>

      <div className="space-y-3 max-w-2xl">
        {/* Toda la empresa */}
        <button
          onClick={() => handleSelectTarget("empresa")}
          className={`w-full px-4 py-3 border rounded-lg text-left transition-colors ${
            selectedTarget === "empresa"
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
              selectedTarget === "area"
                ? `${C.button} border-[#7485bb]`
                : "border-foreground/30 bg-background text-foreground hover:bg-secondary"
            }`}
          >
            <span>
              {selectedTarget === "area" && selectedArea
                ? areas.find((a) => a.id === selectedArea)?.name
                : "Área particular"}
            </span>
            {areaOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          {areaOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-foreground/30 rounded-lg shadow-lg z-10 overflow-hidden">
              {areas.map((area) => (
                <button
                  key={area.id}
                  onClick={() => handleSelectTarget("area", area.id)}
                  className={`w-full text-left px-4 py-3 hover:bg-secondary transition-colors ${selectedArea === area.id ? "bg-[#E0D7F9]" : ""}`}
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
              selectedTarget === "grupo"
                ? `${C.button} border-[#7485bb]`
                : "border-foreground/30 bg-background text-foreground hover:bg-secondary"
            }`}
          >
            <span>
              {selectedTarget === "grupo" && selectedGrupo
                ? groups.find((g) => g.id === selectedGrupo)?.name
                : "Grupo particular"}
            </span>
            {grupoOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          {grupoOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-foreground/30 rounded-lg shadow-lg z-10 overflow-hidden">
              {filteredGroups.map((grupo) => (
                <button
                  key={grupo.id}
                  onClick={() => handleSelectTarget("grupo", grupo.id)}
                  className={`w-full text-left px-4 py-3 hover:bg-secondary transition-colors ${selectedGrupo === grupo.id ? "bg-[#E0D7F9]" : ""}`}
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
              selectedTarget === "trabajador"
                ? `${C.button} border-[#7485bb]`
                : "border-foreground/30 bg-background text-foreground hover:bg-secondary"
            }`}
          >
            <span>
              {selectedTarget === "trabajador" && selectedTrabajador
                ? (() => {
                    const w = workers.find((t) => t.id === selectedTrabajador);
                    return w
                      ? `${w.name} ${w.last_names}`
                      : "Trabajador particular";
                  })()
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
                  onClick={() => handleSelectTarget("trabajador", worker.id)}
                  className={`w-full text-left px-4 py-3 hover:bg-secondary transition-colors ${selectedTrabajador === worker.id ? "bg-[#E0D7F9]" : ""}`}
                >
                  {worker.name} {worker.last_names}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Submit */}
        <button
          onClick={handleCrearEncuesta}
          disabled={!canCreate || submitting}
          className={`w-full mt-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
            canCreate && !submitting
              ? `${C.button}`
              : "bg-secondary text-muted-foreground cursor-not-allowed"
          }`}
        >
          {submitting && <Loader2 size={16} className="animate-spin" />}
          {submitting ? "Creando..." : "Crear Encuesta"}
        </button>
      </div>

      {/* ── Question picker modal ─────────────────────────────────────────── */}
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
                ? "Elige las preguntas que formarán parte de esta nueva encuesta"
                : "Selecciona las preguntas que formarán parte de esta encuesta"}
            </p>

            {/* Question search */}
            <div className="relative mb-4">
              <Search
                size={16}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              />
              <input
                type="text"
                placeholder="Buscar preguntas..."
                value={questionSearch}
                onChange={(e) => setQuestionSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>

            {/* Question list */}
            <div className="flex-1 overflow-y-auto space-y-2 mb-4">
              {loadingLinked ? (
                <div className="flex items-center justify-center gap-2 py-8 text-muted-foreground">
                  <Loader2 size={16} className="animate-spin" />
                  <span className="text-sm font-sans">
                    Cargando preguntas vinculadas...
                  </span>
                </div>
              ) : filteredQuestions.length === 0 ? (
                <p className="text-muted-foreground text-sm font-sans text-center py-4">
                  No se encontraron preguntas.
                </p>
              ) : (
                filteredQuestions.map((question) => {
                  const isSelected = selectedQuestionIds.has(question.id);
                  const isAlreadyLinked =
                    !isFromScratch && linkedQuestionIds.has(question.id);
                  return (
                    <button
                      key={question.id}
                      onClick={() =>
                        !isAlreadyLinked && toggleQuestion(question.id)
                      }
                      disabled={isAlreadyLinked}
                      className={`w-full flex items-center justify-between px-4 py-3 border-2 rounded-xl text-left transition-all ${
                        isAlreadyLinked
                          ? "border-primary/40 bg-primary/5 opacity-60 cursor-default"
                          : isSelected
                            ? "border-primary bg-primary/5"
                            : "border-foreground/20 hover:border-foreground/40"
                      }`}
                    >
                      <div className="flex flex-col gap-0.5">
                        <span className="text-sm text-foreground">
                          {question.text}
                        </span>
                        {isAlreadyLinked && (
                          <span className="text-xs text-primary font-sans">
                            Ya vinculada
                          </span>
                        )}
                      </div>
                      <span
                        className={`ml-3 flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${
                          isSelected
                            ? "bg-primary border-primary"
                            : "border-foreground/30"
                        }`}
                      >
                        {isSelected && (
                          <Check
                            size={11}
                            className="text-primary-foreground"
                          />
                        )}
                      </span>
                    </button>
                  );
                })
              )}
            </div>

            {/* Selection count + confirm */}
            <div className="flex items-center justify-between pt-2 border-t border-border">
              <span className="text-sm text-muted-foreground font-sans">
                {selectedQuestionIds.size} pregunta
                {selectedQuestionIds.size !== 1 ? "s" : ""} seleccionada
                {selectedQuestionIds.size !== 1 ? "s" : ""}
              </span>
              <button
                onClick={handleConfirmSurvey}
                disabled={selectedQuestionIds.size === 0}
                className={`px-6 py-2 rounded-lg font-medium text-sm transition-colors ${
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
