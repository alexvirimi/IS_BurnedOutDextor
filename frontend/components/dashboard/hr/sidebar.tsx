"use client";

import { useState } from "react";
import {
  SidebarShell,
  SidebarNavButton,
  SidebarExpandable,
  SidebarSubItem,
} from "@/components/dashboard/shared/sidebar-shell";

export type HRView =
  | "mi-progreso"
  | "areas"
  | "grupos"
  | "trabajadores"
  | "realizar-encuestas"
  | "crear-encuesta"
  | "modificar-encuestas";

interface HRSidebarProps {
  activeView: HRView;
  onViewChange: (view: HRView) => void;
  userName: string;
}

export function HRSidebar({
  activeView,
  onViewChange,
  userName,
}: HRSidebarProps) {
  const isHistoricosActive = ["areas", "grupos", "trabajadores"].includes(
    activeView,
  );
  const isEncuestasActive = [
    "realizar-encuestas",
    "crear-encuesta",
    "modificar-encuestas",
  ].includes(activeView);

  const [historicosOpen, setHistoricosOpen] = useState(isHistoricosActive);
  const [encuestasOpen, setEncuestasOpen] = useState(isEncuestasActive);

  return (
    <SidebarShell userName={userName}>
      <SidebarNavButton
        label="Mi Progreso"
        isActive={activeView === "mi-progreso"}
        onClick={() => onViewChange("mi-progreso")}
      />

      <SidebarExpandable
        label="Históricos"
        isExpanded={historicosOpen}
        isActive={isHistoricosActive}
        onToggle={() => setHistoricosOpen((v) => !v)}
      >
        <SidebarSubItem
          label="Áreas"
          isActive={activeView === "areas"}
          onClick={() => onViewChange("areas")}
        />
        <SidebarSubItem
          label="Grupos"
          isActive={activeView === "grupos"}
          onClick={() => onViewChange("grupos")}
        />
        <SidebarSubItem
          label="Trabajadores"
          isActive={activeView === "trabajadores"}
          onClick={() => onViewChange("trabajadores")}
        />
      </SidebarExpandable>

      <SidebarExpandable
        label="Encuestas"
        isExpanded={encuestasOpen}
        isActive={isEncuestasActive}
        onToggle={() => setEncuestasOpen((v) => !v)}
      >
        <SidebarSubItem
          label="Crear Encuesta"
          isActive={activeView === "crear-encuesta"}
          onClick={() => onViewChange("crear-encuesta")}
        />
        <SidebarSubItem
          label="Modificar Encuestas"
          isActive={activeView === "modificar-encuestas"}
          onClick={() => onViewChange("modificar-encuestas")}
        />
        <SidebarSubItem
          label="Realizar Encuestas"
          isActive={activeView === "realizar-encuestas"}
          onClick={() => onViewChange("realizar-encuestas")}
        />
      </SidebarExpandable>
    </SidebarShell>
  );
}
