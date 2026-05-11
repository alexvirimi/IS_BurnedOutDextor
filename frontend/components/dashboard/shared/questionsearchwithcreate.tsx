"use client";

/**
 * QuestionSearchWithCreate
 * ─────────────────────────
 * A self-contained search + inline-create component for survey question pickers.
 *
 * Props
 * ─────
 * questions        — full list of available questions (already fetched by parent)
 * selectedIds      — Set of already-selected question IDs
 * disabledIds      — Set of IDs that cannot be toggled (already linked, etc.)
 * onToggle(id)     — called when a question is checked/unchecked
 * onCreated(q)     — called after a new question is successfully POSTed to /question/
 * className        — optional wrapper class
 *
 * State flow
 * ──────────
 * searchText          → filters the question list
 * createMode          → whether the inline-create form is expanded
 * selectedVariableId  → the psicometric_variable the user picks while creating
 * creating            → loading flag while POST is in-flight
 * createError         → error message from the POST
 */

import { useState, useEffect, useRef } from "react";
import { Search, Plus, Check, Loader2, ChevronDown, X } from "lucide-react";
import { apiFetch, apiPost } from "@/lib/api/context";
import { BUTTONS_COLORS } from "@/lib/styles/buttons-colors";
import { PsicometricVariable, Question } from "@/lib/api/interfaces";

const M = BUTTONS_COLORS.hrModal;

interface Props {
  questions: Question[];
  selectedIds: Set<string>;
  disabledIds?: Set<string>;
  onToggle: (id: string) => void;
  onCreated: (question: Question) => void;
  className?: string;
}

// ─── Helper ───────────────────────────────────────────────────────────────────

function getVariableName(v: Question["psicometric_variable"]): string {
  if (!v) return "";
  if (typeof v === "string") return v;
  return v.name;
}

// ─── Component ────────────────────────────────────────────────────────────────

export function QuestionSearchWithCreate({
  questions,
  selectedIds,
  disabledIds = new Set(),
  onToggle,
  onCreated,
  className = "",
}: Props) {
  // ── Search ──────────────────────────────────────────────────────────────────
  const [searchText, setSearchText] = useState("");
  const [questionText, setQuestionText] = useState("");

  const filtered = questions.filter((q) =>
    q.text.toLowerCase().includes(searchText.toLowerCase()),
  );

  const hasResults = filtered.length > 0;

  // ── Create mode ─────────────────────────────────────────────────────────────
  const [createMode, setCreateMode] = useState(false);
  const [variables, setVariables] = useState<PsicometricVariable[]>([]);
  const [loadingVars, setLoadingVars] = useState(false);
  const [selectedVariableId, setSelectedVariableId] = useState<string>("");
  const [varDropdownOpen, setVarDropdownOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [filterDisabled, setFilterDisabled] = useState(false);

  const varDropdownRef = useRef<HTMLDivElement>(null);

  // Close var dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (
        varDropdownRef.current &&
        !varDropdownRef.current.contains(e.target as Node)
      ) {
        setVarDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  // Fetch variables once when create mode opens
  const openCreateMode = async () => {
    setCreateMode(true);
    setCreateError(null);
    setFilterDisabled(true);
    setQuestionText(searchText);
    if (variables.length === 0) {
      setLoadingVars(true);
      try {
        const data = await apiFetch<PsicometricVariable[]>(
          "/psicometric_variable/",
        );
        setVariables(data);
      } catch {
        setCreateError("No se pudieron cargar las variables psicométricas.");
      } finally {
        setLoadingVars(false);
      }
    }
  };

  const closeCreateMode = () => {
    setCreateMode(false);
    setFilterDisabled(false);
    setSelectedVariableId("");
    setCreateError(null);
    setVarDropdownOpen(false);
  };

  // ── Submit new question ──────────────────────────────────────────────────────
  const handleCreate = async () => {
    if (!questionText.trim() || !selectedVariableId) return;
    setCreating(true);
    setCreateError(null);
    try {
      const newQuestion = await apiPost<Question>("/question/", {
        text: questionText.trim(),
        psicometric_variable_id: selectedVariableId,
      });
      onCreated(newQuestion);
      // Reset to search mode, clear the text so the user sees the new question
      closeCreateMode();
      setSearchText("");
      setQuestionText("");
    } catch (err) {
      setCreateError(
        err instanceof Error ? err.message : "Error creando la pregunta.",
      );
    } finally {
      setCreating(false);
    }
  };

  const selectedVariable = variables.find((v) => v.id === selectedVariableId);
  const canCreate = questionText.trim().length > 0 && selectedVariableId !== "";

  // ── Render ───────────────────────────────────────────────────────────────────
  return (
    <div className={`flex flex-col gap-2 p-1 ${className}`}>
      {/* ── Search input ── */}
      <div className="relative">
        <Search
          size={15}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
        />
        <input
          type="text"
          placeholder="Buscar preguntas disponibles..."
          disabled={filterDisabled}
          value={searchText}
          onChange={(e) => {
            setSearchText(e.target.value);
            // If user changes text while in create mode, keep mode open but reset variable
            if (createMode) {
              setSelectedVariableId("");
              setCreateError(null);
            }
          }}
          className={`w-full pl-9 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring
            ${filterDisabled ? "bg-secondary/70" : ""}
            `}
        />
      </div>

      {/* ── Question list ── */}
      {!createMode && (
        <div className="space-y-2 max-h-52 overflow-y-auto pr-0.5">
          {hasResults ? (
            filtered.map((question) => {
              const isSelected = selectedIds.has(question.id);
              const isDisabled = disabledIds.has(question.id);
              return (
                <button
                  key={question.id}
                  onClick={() => !isDisabled && onToggle(question.id)}
                  disabled={isDisabled}
                  className={`w-full flex items-center justify-between px-4 py-3 border-2 rounded-xl text-left transition-all ${
                    isDisabled
                      ? "border-primary/40 bg-primary/5 opacity-60 cursor-default"
                      : isSelected
                        ? "border-primary bg-primary/5"
                        : "border-foreground/20 hover:border-foreground/40"
                  }`}
                >
                  <div className="flex flex-col gap-0.5 min-w-0">
                    <span className="text-sm text-foreground truncate">
                      {question.text}
                    </span>
                    <span className="text-xs text-muted-foreground font-sans">
                      {getVariableName(question.psicometric_variable)}
                    </span>
                    {isDisabled && (
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
                      <Check size={11} className="text-primary-foreground" />
                    )}
                  </span>
                </button>
              );
            })
          ) : searchText.trim().length > 0 ? (
            /* No results — prompt to create */
            <div className="flex flex-col items-center gap-2 py-4 text-center">
              <p className="text-sm text-muted-foreground font-sans">
                No se encontró ninguna pregunta con ese texto.
              </p>
              <button
                onClick={openCreateMode}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${M.button}`}
              >
                <Plus size={14} />
                ¿Quieres crear esta pregunta?
              </button>
            </div>
          ) : null}
        </div>
      )}

      {/* ── Persistent "crear nueva pregunta" CTA (always visible when not in create mode) ── */}
      {!createMode && (
        <button
          onClick={openCreateMode}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-dashed border-foreground/30 text-sm text-muted-foreground hover:text-foreground hover:border-foreground/50 transition-colors mt-1"
        >
          <Plus size={14} />
          Crear nueva pregunta
        </button>
      )}

      {/* ── Inline create form ── */}
      {createMode && (
        <div className="border border-foreground/20 rounded-xl p-4 flex flex-col gap-3 bg-secondary/20">
          {/* Header */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-foreground">
              Nueva pregunta
            </span>
            <button
              onClick={closeCreateMode}
              className="w-6 h-6 rounded-full flex items-center justify-center hover:bg-foreground/10 transition-colors"
              title="Cancelar"
            >
              <X size={13} className="text-muted-foreground" />
            </button>
          </div>

          {/* Text preview (already filled from search input) */}
          <input
            type="text"
            autoFocus
            placeholder="Ingresa la nueva pregunta"
            value={questionText}
            onChange={(e) => {
              setQuestionText(e.target.value);
              // If user changes text while in create mode, keep mode open but reset variable
              if (createMode) {
                setSelectedVariableId("");
                setCreateError(null);
              }
            }}
            className="w-full px-3 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />

          {/* Psicometric variable selector */}
          <div className="flex flex-col gap-1">
            <label className="text-xs text-muted-foreground font-sans">
              Variable psicométrica
            </label>
            {loadingVars ? (
              <div className="flex items-center gap-2 px-3 py-2 text-muted-foreground text-sm">
                <Loader2 size={13} className="animate-spin" />
                Cargando variables...
              </div>
            ) : (
              <div className="relative" ref={varDropdownRef}>
                <button
                  onClick={() => setVarDropdownOpen((v) => !v)}
                  className="w-full flex items-center justify-between px-3 py-2 border border-foreground/30 rounded-lg bg-background text-sm transition-colors hover:border-foreground/50 focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <span
                    className={
                      selectedVariable
                        ? "text-foreground"
                        : "text-muted-foreground"
                    }
                  >
                    {selectedVariable
                      ? selectedVariable.name
                      : "Selecciona una categoría..."}
                  </span>
                  <ChevronDown
                    size={14}
                    className={`text-muted-foreground transition-transform ${varDropdownOpen ? "rotate-180" : ""}`}
                  />
                </button>

                {varDropdownOpen && variables.length > 0 && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-foreground/20 rounded-lg shadow-lg z-20 overflow-hidden max-h-40 overflow-y-auto">
                    {variables.map((variable) => (
                      <button
                        key={variable.id}
                        onClick={() => {
                          setSelectedVariableId(variable.id);
                          setVarDropdownOpen(false);
                        }}
                        className={`w-full text-left px-3 py-2.5 text-sm transition-colors hover:bg-secondary ${
                          selectedVariableId === variable.id
                            ? "bg-[#E0D7F9] font-medium"
                            : ""
                        }`}
                      >
                        {variable.name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Error */}
          {createError && (
            <p className="text-xs text-destructive font-sans">{createError}</p>
          )}

          {/* Submit */}
          <button
            onClick={handleCreate}
            disabled={!canCreate || creating}
            className={`flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              canCreate && !creating
                ? "bg-[#8795C7] text-white hover:bg-[#7485bb]"
                : "bg-secondary text-muted-foreground cursor-not-allowed"
            }`}
          >
            {creating && <Loader2 size={13} className="animate-spin" />}
            {creating ? "Creando..." : "Crear y añadir pregunta"}
          </button>
        </div>
      )}
    </div>
  );
}
