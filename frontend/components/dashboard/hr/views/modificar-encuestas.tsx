"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Filter,
  Search,
  X,
  Trash2,
  Loader2,
  Check,
  Plus,
  Minus,
} from "lucide-react";
import { apiFetch, apiPost, apiDelete, apiPatch } from "@/lib/api/context";
import { BUTTONS_COLORS } from "@/lib/styles/buttons-colors";
import {
  Survey,
  QuestionSurveyRelation,
  Question,
  SurveyWithQuestions,
} from "@/lib/api/interfaces";

const C = BUTTONS_COLORS.hr;
const M = BUTTONS_COLORS.hrModal;

// ─── Component ────────────────────────────────────────────────────────────────

export function HRModificarEncuestas() {
  // ── Remote data ──────────────────────────────────────────────────────────────
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [allQuestions, setAllQuestions] = useState<Question[]>([]);
  const [allRelations, setAllRelations] = useState<QuestionSurveyRelation[]>(
    [],
  );
  const [loadingList, setLoadingList] = useState(true);
  const [listError, setListError] = useState<string | null>(null);

  // ── Survey detail modal ───────────────────────────────────────────────────────
  const [selectedSurvey, setSelectedSurvey] = useState<Survey | null>(null);
  const [modalMode, setModalMode] = useState<"active" | "finalizada">("active");
  const [linkedQuestions, setLinkedQuestions] = useState<Question[]>([]);
  const [linkedRelations, setLinkedRelations] = useState<
    QuestionSurveyRelation[]
  >([]);
  const [showModal, setShowModal] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  // ── Editable header fields (active modal only) ────────────────────────────────
  const [editName, setEditName] = useState("");
  const [editAperture, setEditAperture] = useState("");
  const [editFinishing, setEditFinishing] = useState("");
  const [savingActiveHeader, setSavingActiveHeader] = useState(false);
  const [headerSaved, setHeaderSaved] = useState(false);

  // ── Question management inside modal ─────────────────────────────────────────
  const [showAddQuestions, setShowAddQuestions] = useState(false);
  const [questionSearch, setQuestionSearch] = useState("");
  const [savingQuestion, setSavingQuestion] = useState<string | null>(null); // question id being added/removed

  // ── Delete survey modal ───────────────────────────────────────────────────────
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [surveyToDelete, setSurveyToDelete] = useState<Survey | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  // ── Filters ───────────────────────────────────────────────────────────────────
  const [searchActive, setSearchActive] = useState("");
  const [searchInactive, setSearchInactive] = useState("");

  // ─── Load surveys + relations on mount ───────────────────────────────────────

  const loadAll = useCallback(async () => {
    setLoadingList(true);
    setListError(null);
    try {
      const [surveysData, questionsData, relationsData] = await Promise.all([
        apiFetch<Survey[]>("/survey/"),
        apiFetch<Question[]>("/question/"),
        apiFetch<QuestionSurveyRelation[]>("/question_survey/"),
      ]);
      setSurveys(surveysData);
      setAllQuestions(questionsData);
      setAllRelations(relationsData);
    } catch (err) {
      setListError(err instanceof Error ? err.message : "Error cargando datos");
    } finally {
      setLoadingList(false);
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  // ─── Derived lists ────────────────────────────────────────────────────────────

  const activeSurveys = surveys.filter(
    (s) =>
      s.status.toLowerCase() !== "finalizada" &&
      s.name.toLowerCase().includes(searchActive.toLowerCase()),
  );

  const inactiveSurveys = surveys.filter(
    (s) =>
      s.status.toLowerCase() === "finalizada" &&
      s.name.toLowerCase().includes(searchInactive.toLowerCase()),
  );

  // Questions not yet linked to the selected survey
  const linkedQuestionIds = new Set(linkedQuestions.map((q) => q.id));
  const availableQuestions = allQuestions.filter(
    (q) =>
      !linkedQuestionIds.has(q.id) &&
      q.text.toLowerCase().includes(questionSearch.toLowerCase()),
  );

  // ─── Open survey detail ───────────────────────────────────────────────────────

  const handleOpenSurvey = async (
    survey: Survey,
    mode: "active" | "finalizada" = "active",
  ) => {
    setSelectedSurvey(survey);
    setModalMode(mode);
    setShowModal(true);
    setShowAddQuestions(false);
    setQuestionSearch("");
    setDetailError(null);
    setLoadingDetail(true);
    setHeaderSaved(false);
    // Seed editable fields from current survey data
    setEditName(survey.name);
    setEditAperture(survey.aperture_date);
    setEditFinishing(survey.finishing_date);

    try {
      const data = await apiFetch<SurveyWithQuestions>(
        `/survey/${survey.id}/questions`,
      );
      setLinkedQuestions(data.questions);

      // Keep track of relation IDs so we can DELETE by relation id (not question id)
      const surveyRelations = allRelations.filter(
        (r) => r.id_survey === survey.id,
      );
      setLinkedRelations(surveyRelations);
    } catch (err) {
      setDetailError(
        err instanceof Error ? err.message : "Error cargando preguntas",
      );
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedSurvey(null);
    setLinkedQuestions([]);
    setLinkedRelations([]);
    setShowAddQuestions(false);
    setQuestionSearch("");
    setDetailError(null);
    setEditName("");
    setEditAperture("");
    setEditFinishing("");
    setHeaderSaved(false);
  };

  // ─── Save edited name / dates ─────────────────────────────────────────────────

  const handleFinalizedSurvey = async () => {
    if (!selectedSurvey) return;
    setSavingActiveHeader(true);
    setDetailError(null);
    try {
      await apiPatch(`/survey/${selectedSurvey.id}`, {
        name: editName.trim(),
        aperture_date: editAperture,
        finishing_date: editFinishing,
      });
      // Update local list so the row reflects the new name/dates immediately
      setSurveys((prev) =>
        prev.map((s) =>
          s.id === selectedSurvey.id
            ? {
                ...s,
                name: editName.trim(),
                aperture_date: editAperture,
                finishing_date: editFinishing,
              }
            : s,
        ),
      );
      setSelectedSurvey((prev) =>
        prev
          ? {
              ...prev,
              name: editName.trim(),
              aperture_date: editAperture,
              finishing_date: editFinishing,
            }
          : prev,
      );
      setHeaderSaved(true);
      setTimeout(() => setHeaderSaved(false), 2000);
    } catch (err) {
      setDetailError(
        err instanceof Error ? err.message : "Error guardando cambios",
      );
    } finally {
      setSavingActiveHeader(false);
    }
  };

  const handleSaveHeader = async () => {
    if (!selectedSurvey) return;
    setSavingActiveHeader(true);
    setDetailError(null);
    try {
      await apiPatch(`/survey/${selectedSurvey.id}`, {
        name: editName.trim(),
        aperture_date: editAperture,
        finishing_date: editFinishing,
      });
      // Update local list so the row reflects the new name/dates immediately
      setSurveys((prev) =>
        prev.map((s) =>
          s.id === selectedSurvey.id
            ? {
                ...s,
                name: editName.trim(),
                aperture_date: editAperture,
                finishing_date: editFinishing,
              }
            : s,
        ),
      );
      setSelectedSurvey((prev) =>
        prev
          ? {
              ...prev,
              name: editName.trim(),
              aperture_date: editAperture,
              finishing_date: editFinishing,
            }
          : prev,
      );
      setHeaderSaved(true);
      setTimeout(() => setHeaderSaved(false), 2000);
    } catch (err) {
      setDetailError(
        err instanceof Error ? err.message : "Error guardando cambios",
      );
    } finally {
      setSavingActiveHeader(false);
    }
  };

  const handleAddQuestion = async (question: Question) => {
    if (!selectedSurvey) return;
    setSavingQuestion(question.id);
    try {
      const newRelation = await apiPost<QuestionSurveyRelation>(
        "/question_survey/",
        {
          id_survey: selectedSurvey.id,
          id_question: question.id,
        },
      );
      // Update local state immediately (optimistic)
      setLinkedQuestions((prev) => [...prev, question]);
      setLinkedRelations((prev) => [...prev, newRelation]);
      setAllRelations((prev) => [...prev, newRelation]);
    } catch (err) {
      setDetailError(
        err instanceof Error ? err.message : "Error añadiendo pregunta",
      );
    } finally {
      setSavingQuestion(null);
    }
  };

  // ─── Remove question from survey ─────────────────────────────────────────────

  const handleRemoveQuestion = async (question: Question) => {
    if (!selectedSurvey) return;

    // Find the relation record for this question+survey pair
    const relation = linkedRelations.find(
      (r) => r.id_question === question.id && r.id_survey === selectedSurvey.id,
    );
    if (!relation) return;

    setSavingQuestion(question.id);
    try {
      await apiDelete(`/question_survey/${relation.id}`);
      // Update local state immediately
      setLinkedQuestions((prev) => prev.filter((q) => q.id !== question.id));
      setLinkedRelations((prev) => prev.filter((r) => r.id !== relation.id));
      setAllRelations((prev) => prev.filter((r) => r.id !== relation.id));
    } catch (err) {
      setDetailError(
        err instanceof Error ? err.message : "Error eliminando pregunta",
      );
    } finally {
      setSavingQuestion(null);
    }
  };

  // ─── Deactivate survey ────────────────────────────────────────────────────────
  // The backend has no PATCH/PUT for survey status, so we create a new survey
  // record with status "Inactiva" as a workaround — if the backend adds a status
  // endpoint this can be replaced with a single PATCH call.
  // For now we optimistically update the local list.

  const handleDeleteClick = (e: React.MouseEvent, survey: Survey) => {
    e.stopPropagation();
    setSurveyToDelete(survey);
    setShowDeleteModal(true);
    setDeleteError(null);
  };

  const handleConfirmDeactivate = async () => {
    if (!surveyToDelete) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      await apiPatch(`/survey/${surveyToDelete.id}`, {
        status: "finalizada",
      });
      setSurveys((prev) =>
        prev.map((s) =>
          s.id === surveyToDelete.id ? { ...s, status: "finalizada" } : s,
        ),
      );
      setShowDeleteModal(false);
      setSurveyToDelete(null);
    } catch (err) {
      setDeleteError(
        err instanceof Error ? err.message : "Error desactivando encuesta",
      );
    } finally {
      setDeleting(false);
    }
  };

  // ─── Render ───────────────────────────────────────────────────────────────────

  // if (loadingList) {
  //   return (
  //     <div className="p-8 flex items-center gap-3 text-muted-foreground">
  //       <Loader2 className="animate-spin w-5 h-5" />
  //       <span className="font-sans text-sm">Cargando encuestas...</span>
  //     </div>
  //   );
  // }

  if (listError) {
    return (
      <div className="p-8">
        <div className="px-4 py-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm font-sans">
          {listError}
        </div>
        <button
          onClick={loadAll}
          className={`mt-4 px-4 py-2 rounded-lg text-sm font-sans`}
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* ── Active surveys ────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-2xl font-bold text-foreground"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          ENCUESTAS
        </h2>
        <div className="flex items-center gap-2">
          <button className={`p-2 rounded-lg transition-colors`}>
            <Filter size={20} />
          </button>
          <div className="relative">
            <Search
              size={20}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <input
              type="text"
              placeholder="Buscar"
              value={searchActive}
              onChange={(e) => setSearchActive(e.target.value)}
              className="pl-10 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>
      </div>

      <div className="space-y-3 mb-10">
        {loadingList ? (
          <div className="flex-1 text-left px-4 py-3 rounded-lg border border-border">
            <div className="p-8 flex items-center gap-3 text-muted-foreground">
              <Loader2 className="animate-spin w-5 h-5" />
              <span className="font-sans text-sm">Cargando encuestas...</span>
            </div>
          </div>
        ) : (
          activeSurveys.length === 0 && (
            <p className="text-muted-foreground text-sm font-sans">
              No hay encuestas activas.
            </p>
          )
        )}
        {activeSurveys.map((survey) => (
          <div key={survey.id} className="flex items-center gap-2">
            <button
              onClick={() => handleOpenSurvey(survey)}
              className={`flex-1 text-left px-4 py-3 rounded-lg transition-colors border border-border hover:bg-secondary`}
            >
              <span>{survey.name}</span>
              <span className="ml-2 text-xs opacity-70">
                {survey.aperture_date} → {survey.finishing_date}
              </span>
            </button>
            <button
              onClick={(e) => handleDeleteClick(e, survey)}
              className="p-3 border border-red-300 rounded-lg bg-background text-red-500 hover:bg-red-50 transition-colors"
              title="Desactivar encuesta"
            >
              <Trash2 size={20} />
            </button>
          </div>
        ))}
      </div>

      {/* ── Inactive surveys ─────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-2xl font-bold text-foreground"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          ENCUESTAS INACTIVAS
        </h2>
        <div className="flex items-center gap-2">
          <button className={`p-2 rounded-lg transition-colors`}>
            <Filter size={20} />
          </button>
          <div className="relative">
            <Search
              size={20}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <input
              type="text"
              placeholder="Buscar"
              value={searchInactive}
              onChange={(e) => setSearchInactive(e.target.value)}
              className="pl-10 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {loadingList ? (
          <div className="flex-1 text-left px-4 py-3 rounded-lg border border-border">
            <div className="p-8 flex items-center gap-3 text-muted-foreground">
              <Loader2 className="animate-spin w-5 h-5" />
              <span className="font-sans text-sm">Cargando encuestas...</span>
            </div>
          </div>
        ) : (
          inactiveSurveys.length === 0 && (
            <p className="text-muted-foreground text-sm font-sans">
              No hay encuestas activas.
            </p>
          )
        )}
        {inactiveSurveys.map((survey) => (
          <button
            key={survey.id}
            onClick={() => handleOpenSurvey(survey, "finalizada")}
            className="w-full text-left px-4 py-3 text-white rounded-lg bg-accent text-foreground hover:opacity-90 transition-opacity"
          >
            <span>{survey.name}</span>
            <span className="ml-2 text-xs opacity-60">
              {survey.aperture_date} → {survey.finishing_date}
            </span>
          </button>
        ))}
      </div>

      {/* ── Survey detail modal ───────────────────────────────────────── */}
      {showModal && selectedSurvey && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-xl p-6 w-full max-w-2xl max-h-[90vh] flex flex-col relative">
            {/* Close */}
            <button
              onClick={handleCloseModal}
              className={`absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center transition-colors ${M.button}`}
            >
              <X size={18} />
            </button>

            {/* Header — editable for active, read-only for inactive */}
            {modalMode === "active" ? (
              <div className="mb-4 space-y-2">
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full text-2xl font-bold text-foreground bg-transparent border-b-2 border-foreground/20 focus:border-primary focus:outline-none pb-1 font-heading uppercase"
                  style={{ fontFamily: "var(--font-heading)" }}
                />
                {/* Change Date and Save Button */}
                <div className="flex items-center gap-3">
                  <div className="flex flex-col gap-0.5 flex-1">
                    <span className="text-xs text-muted-foreground font-sans">
                      Apertura
                    </span>
                    <input
                      type="date"
                      value={editAperture}
                      onChange={(e) => setEditAperture(e.target.value)}
                      className="px-2 py-1 border border-foreground/20 rounded-lg bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  </div>
                  <div className="flex flex-col gap-0.5 flex-1">
                    <span className="text-xs text-muted-foreground font-sans">
                      Cierre
                    </span>
                    <input
                      type="date"
                      value={editFinishing}
                      min={editAperture || undefined}
                      onChange={(e) => setEditFinishing(e.target.value)}
                      className="px-2 py-1 border border-foreground/20 rounded-lg bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  </div>
                  <button
                    onClick={handleSaveHeader}
                    disabled={savingActiveHeader || !editName.trim()}
                    className={`mt-4 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex-shrink-0 disabled:opacity-50 ${
                      headerSaved
                        ? "bg-green-100 text-green-700"
                        : `${M.button}`
                    }`}
                  >
                    {savingActiveHeader ? (
                      <Loader2 size={13} className="animate-spin" />
                    ) : headerSaved ? (
                      <>
                        <Check size={13} /> Guardado
                      </>
                    ) : (
                      "Guardar"
                    )}
                  </button>
                </div>
                <p className="text-xs text-muted-foreground font-sans">
                  Estado:{" "}
                  <span className="font-medium text-foreground">
                    {selectedSurvey.status}
                  </span>
                </p>
              </div>
            ) : (
              <div className="mb-4">
                <h2
                  className="text-2xl font-bold text-foreground mb-1"
                  style={{ fontFamily: "var(--font-heading)" }}
                >
                  {selectedSurvey.name.toUpperCase()}
                </h2>
                <p className="text-sm text-muted-foreground mb-1 font-sans">
                  {selectedSurvey.aperture_date} →{" "}
                  {selectedSurvey.finishing_date}
                </p>
                <p className="text-xs text-muted-foreground font-sans">
                  Estado:{" "}
                  <span className="font-medium text-destructive">
                    {selectedSurvey.status}
                  </span>
                </p>
              </div>
            )}

            {/* Error */}
            {detailError && (
              <div className="mb-3 px-3 py-2 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs font-sans">
                {detailError}
              </div>
            )}

            {/* Loading */}
            {loadingDetail ? (
              <div className="flex items-center gap-3 py-8 text-muted-foreground justify-center">
                <Loader2 className="animate-spin w-5 h-5" />
                <span className="text-sm font-sans">Cargando preguntas...</span>
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto space-y-2 mb-4">
                {/* Linked questions */}
                {linkedQuestions.length === 0 && (
                  <p className="text-muted-foreground text-sm font-sans text-center py-4">
                    Esta encuesta no tiene preguntas vinculadas.
                  </p>
                )}
                {linkedQuestions.map((question, i) => (
                  <div
                    key={question.id}
                    className="flex items-center justify-between px-4 py-3 border-2 border-foreground/20 rounded-xl"
                  >
                    <div className="flex flex-col gap-0.5">
                      <span className="text-sm text-foreground">
                        {i + 1}. {question.text}
                      </span>
                      <span className="text-xs text-muted-foreground font-sans">
                        {question.psicometric_variable}
                      </span>
                    </div>
                    <button
                      onClick={() => handleRemoveQuestion(question)}
                      disabled={savingQuestion === question.id}
                      className={`ml-3 flex-shrink-0 w-7 h-7 rounded-full border-2 border-red-300 flex items-center justify-center text-red-500 hover:bg-red-50 transition-colors disabled:opacity-40 ${
                        modalMode === "finalizada" ? "invisible" : ""
                      }`}
                      title="Desvincular pregunta"
                    >
                      {savingQuestion === question.id ? (
                        <Loader2 size={13} className="animate-spin" />
                      ) : (
                        <Minus size={13} />
                      )}
                    </button>
                  </div>
                ))}

                {/* Add questions section — active only */}
                {showAddQuestions && modalMode === "active" && (
                  <div className="mt-4 border-t border-border pt-4">
                    <div className="relative mb-3">
                      <Search
                        size={15}
                        className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                      />
                      <input
                        type="text"
                        placeholder="Buscar preguntas disponibles..."
                        value={questionSearch}
                        onChange={(e) => setQuestionSearch(e.target.value)}
                        className="w-full pl-9 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                      />
                    </div>

                    {availableQuestions.length === 0 ? (
                      <p className="text-muted-foreground text-xs font-sans text-center py-2">
                        {allQuestions.length === linkedQuestions.length
                          ? "Todas las preguntas ya están vinculadas."
                          : "No se encontraron preguntas."}
                      </p>
                    ) : (
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {availableQuestions.map((question) => (
                          <div
                            key={question.id}
                            className="flex items-center justify-between px-4 py-3 border border-foreground/20 rounded-xl"
                          >
                            <div className="flex flex-col gap-0.5">
                              <span className="text-sm text-foreground">
                                {question.text}
                              </span>
                              <span className="text-xs text-muted-foreground font-sans">
                                {question.psicometric_variable}
                              </span>
                            </div>
                            <button
                              onClick={() => handleAddQuestion(question)}
                              disabled={savingQuestion === question.id}
                              className={`ml-3 flex-shrink-0 w-7 h-7 rounded-full border-2 flex items-center justify-center transition-colors disabled:opacity-40 ${M.button} border-foreground/30`}
                              title="Vincular pregunta"
                            >
                              {savingQuestion === question.id ? (
                                <Loader2 size={13} className="animate-spin" />
                              ) : (
                                <Plus size={13} />
                              )}
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Footer actions — active only */}
            {!loadingDetail && (
              <div className="flex items-center justify-between pt-2 border-t border-border">
                <span className="text-sm text-muted-foreground font-sans">
                  {linkedQuestions.length} pregunta
                  {linkedQuestions.length !== 1 ? "s" : ""} vinculada
                  {linkedQuestions.length !== 1 ? "s" : ""}
                </span>
                {modalMode === "active" && (
                  <button
                    onClick={() => {
                      setShowAddQuestions((v) => !v);
                      setQuestionSearch("");
                    }}
                    className={`px-5 py-2 rounded-lg font-medium text-sm transition-colors flex items-center gap-1.5 ${M.button}`}
                  >
                    {showAddQuestions ? (
                      <>
                        <X size={14} /> Cerrar
                      </>
                    ) : (
                      <>
                        <Plus size={14} /> Añadir preguntas
                      </>
                    )}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Deactivate confirmation modal ─────────────────────────────── */}
      {showDeleteModal && surveyToDelete && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-xl p-6 w-full max-w-md relative">
            <button
              onClick={() => {
                setShowDeleteModal(false);
                setSurveyToDelete(null);
                setDeleteError(null);
              }}
              className={`absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center transition-colors ${M.button}`}
            >
              <X size={18} />
            </button>

            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Trash2 size={32} className="text-red-500" />
              </div>

              <h2
                className="text-xl font-bold text-foreground mb-2"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                DESACTIVAR ENCUESTA
              </h2>

              <p className="text-muted-foreground mb-2">
                ¿Estás seguro de que deseas desactivar{" "}
                <strong className="text-foreground">
                  {surveyToDelete.name}
                </strong>
                ?
              </p>
              <p className="text-muted-foreground text-sm mb-6">
                La encuesta pasará a la lista de inactivas.
              </p>

              {deleteError && (
                <div className="mb-4 px-3 py-2 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs font-sans">
                  {deleteError}
                </div>
              )}

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setSurveyToDelete(null);
                    setDeleteError(null);
                  }}
                  disabled={deleting}
                  className={`flex-1 py-3 rounded-lg font-medium transition-colors ${M.button}`}
                >
                  Cancelar
                </button>
                <button
                  onClick={handleConfirmDeactivate}
                  disabled={deleting}
                  className="flex-1 py-3 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-60"
                >
                  {deleting && <Loader2 size={15} className="animate-spin" />}
                  {deleting ? "Desactivando..." : "Desactivar"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
