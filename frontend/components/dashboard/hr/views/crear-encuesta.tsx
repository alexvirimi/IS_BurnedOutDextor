"use client";

import { useState } from "react";
import { Filter, Search, ChevronDown, ChevronUp, X, Check } from "lucide-react";

interface Encuesta {
  id: number;
  nombre: string;
  preguntas: string[];
}

const encuestasData: Encuesta[] = [
  {
    id: 1,
    nombre: "Encuesta 1",
    preguntas: Array.from({ length: 11 }, (_, i) => `Pregunta ${i + 1}`),
  },
  {
    id: 2,
    nombre: "Encuesta 2",
    preguntas: [
      "Pregunta A",
      "Pregunta B",
      "Pregunta C",
      "Pregunta D",
      "Pregunta E",
    ],
  },
];

const areasData = [
  { id: 1, nombre: "Área de Ventas" },
  { id: 2, nombre: "Área de Marketing" },
  { id: 3, nombre: "Área de Finanzas" },
  { id: 4, nombre: "Área de Recursos Humanos" },
  { id: 5, nombre: "Área de Tecnología" },
];

const gruposData = [
  { id: 1, nombre: "Grupo A" },
  { id: 2, nombre: "Grupo B" },
  { id: 3, nombre: "Grupo C" },
  { id: 4, nombre: "Grupo D" },
];

const trabajadoresData = [
  { id: 1, nombre: "Juan Pérez" },
  { id: 2, nombre: "María García" },
  { id: 3, nombre: "Carlos López" },
  { id: 4, nombre: "Ana Martínez" },
  { id: 5, nombre: "Roberto Sánchez" },
  { id: 6, nombre: "Laura Rodríguez" },
];

type TargetType = "empresa" | "area" | "grupo" | "trabajador";

export function HRCrearEncuesta() {
  const [selectedEncuesta, setSelectedEncuesta] = useState<Encuesta | null>(
    null,
  );
  const [showModal, setShowModal] = useState(false);
  const [confirmedEncuesta, setConfirmedEncuesta] = useState<Encuesta | null>(
    null,
  );

  // Dropdown states
  const [areaOpen, setAreaOpen] = useState(false);
  const [grupoOpen, setGrupoOpen] = useState(false);
  const [trabajadorOpen, setTrabajadorOpen] = useState(false);

  // Selection states
  const [selectedTarget, setSelectedTarget] = useState<TargetType>("empresa");
  const [selectedArea, setSelectedArea] = useState<number | null>(null);
  const [selectedGrupo, setSelectedGrupo] = useState<number | null>(null);
  const [selectedTrabajador, setSelectedTrabajador] = useState<number | null>(
    null,
  );

  const handleSelectEncuesta = (encuesta: Encuesta) => {
    setSelectedEncuesta(encuesta);
    setShowModal(true);
  };

  const handleConfirmEncuesta = () => {
    setConfirmedEncuesta(selectedEncuesta);
    setShowModal(false);
  };

  const handleSelectTarget = (type: TargetType, id?: number) => {
    setSelectedTarget(type);
    if (type === "area" && id) {
      setSelectedArea(id);
      setAreaOpen(false);
    } else if (type === "grupo" && id) {
      setSelectedGrupo(id);
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

  const handleCrearEncuesta = () => {
    // Here you would handle the survey creation
    alert(
      `Encuesta "${confirmedEncuesta?.nombre}" creada para ${getTargetLabel()}`,
    );
  };

  const getTargetLabel = () => {
    switch (selectedTarget) {
      case "empresa":
        return "Toda la empresa";
      case "area":
        return (
          areasData.find((a) => a.id === selectedArea)?.nombre ||
          "Área particular"
        );
      case "grupo":
        return (
          gruposData.find((g) => g.id === selectedGrupo)?.nombre ||
          "Grupo particular"
        );
      case "trabajador":
        return (
          trabajadoresData.find((t) => t.id === selectedTrabajador)?.nombre ||
          "Trabajador particular"
        );
    }
  };

  const canCreate =
    confirmedEncuesta &&
    (selectedTarget === "empresa" ||
      (selectedTarget === "area" && selectedArea) ||
      (selectedTarget === "grupo" && selectedGrupo) ||
      (selectedTarget === "trabajador" && selectedTrabajador));

  return (
    <div className="p-8">
      <h1
        className="text-4xl font-bold text-foreground mb-8"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        CREAR ENCUESTA
      </h1>

      {/* Encuestas Section */}
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-2xl font-bold text-foreground"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          ENCUESTAS
        </h2>
        <div className="flex items-center gap-2">
          <button className="p-2 border border-foreground/30 rounded-lg hover:bg-secondary transition-colors">
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
              className="pl-10 pr-4 py-2 border border-foreground/30 rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>
      </div>

      {/* Encuestas Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {encuestasData.map((encuesta) => (
          <button
            key={encuesta.id}
            onClick={() => handleSelectEncuesta(encuesta)}
            className={`p-8 rounded-xl border-2 transition-all text-center relative ${
              confirmedEncuesta?.id === encuesta.id
                ? "bg-accent border-accent text-foreground"
                : "bg-background border-foreground/30 text-foreground hover:border-primary"
            }`}
          >
            <span className="font-medium text-lg">{encuesta.nombre}</span>
            {confirmedEncuesta?.id === encuesta.id && (
              <div className="absolute top-2 right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                <Check size={14} className="text-primary-foreground" />
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Dirigida A Section */}
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
              ? "bg-accent border-accent text-foreground"
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
                ? "bg-accent border-accent text-foreground"
                : "border-foreground/30 bg-background text-foreground hover:bg-secondary"
            }`}
          >
            <span>
              {selectedTarget === "area" && selectedArea
                ? areasData.find((a) => a.id === selectedArea)?.nombre
                : "Área particular"}
            </span>
            {areaOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          {areaOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-foreground/30 rounded-lg shadow-lg z-10 overflow-hidden">
              {areasData.map((area) => (
                <button
                  key={area.id}
                  onClick={() => handleSelectTarget("area", area.id)}
                  className={`w-full text-left px-4 py-3 hover:bg-secondary transition-colors ${
                    selectedArea === area.id ? "bg-accent" : ""
                  }`}
                >
                  {area.nombre}
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
                ? "bg-accent border-accent text-foreground"
                : "border-foreground/30 bg-background text-foreground hover:bg-secondary"
            }`}
          >
            <span>
              {selectedTarget === "grupo" && selectedGrupo
                ? gruposData.find((g) => g.id === selectedGrupo)?.nombre
                : "Grupo particular"}
            </span>
            {grupoOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          {grupoOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-foreground/30 rounded-lg shadow-lg z-10 overflow-hidden">
              {gruposData.map((grupo) => (
                <button
                  key={grupo.id}
                  onClick={() => handleSelectTarget("grupo", grupo.id)}
                  className={`w-full text-left px-4 py-3 hover:bg-secondary transition-colors ${
                    selectedGrupo === grupo.id ? "bg-accent" : ""
                  }`}
                >
                  {grupo.nombre}
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
                ? "bg-accent border-accent text-foreground"
                : "border-foreground/30 bg-background text-foreground hover:bg-secondary"
            }`}
          >
            <span>
              {selectedTarget === "trabajador" && selectedTrabajador
                ? trabajadoresData.find((t) => t.id === selectedTrabajador)
                    ?.nombre
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
              {trabajadoresData.map((trabajador) => (
                <button
                  key={trabajador.id}
                  onClick={() =>
                    handleSelectTarget("trabajador", trabajador.id)
                  }
                  className={`w-full text-left px-4 py-3 hover:bg-secondary transition-colors ${
                    selectedTrabajador === trabajador.id ? "bg-accent" : ""
                  }`}
                >
                  {trabajador.nombre}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Crear Encuesta Button */}
        <button
          onClick={handleCrearEncuesta}
          disabled={!canCreate}
          className={`w-full mt-6 py-3 rounded-lg font-medium transition-colors ${
            canCreate
              ? "bg-primary text-primary-foreground hover:bg-primary/90"
              : "bg-secondary text-muted-foreground cursor-not-allowed"
          }`}
        >
          Crear Encuesta
        </button>
      </div>

      {/* Modal */}
      {showModal && selectedEncuesta && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto relative">
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <X size={18} />
            </button>

            <h2
              className="text-2xl font-bold text-foreground mb-6"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              {selectedEncuesta.nombre.toUpperCase()}
            </h2>

            <div className="space-y-3 mb-6">
              {selectedEncuesta.preguntas.map((pregunta, index) => (
                <div
                  key={index}
                  className="px-4 py-3 border-2 border-foreground/30 rounded-full text-foreground"
                >
                  {pregunta}
                </div>
              ))}
            </div>

            <button
              onClick={handleConfirmEncuesta}
              className="w-full bg-accent text-foreground py-3 rounded-lg font-medium hover:bg-accent/80 transition-colors"
            >
              Elegir Encuesta
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
