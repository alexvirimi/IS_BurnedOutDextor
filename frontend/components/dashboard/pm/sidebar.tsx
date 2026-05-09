"use client";

import {
  SidebarShell,
  SidebarNavButton,
  SidebarExpandable,
  SidebarSubItem,
} from "@/components/dashboard/shared/sidebar-shell";

export type PMView = "encuestas" | "progreso" | "historicos" | "flaggear";
export type GroupType = "A" | "B" | "C" | null;

const GROUPS: Exclude<GroupType, null>[] = ["A", "B", "C"];

interface PMSidebarProps {
  activeView: PMView;
  selectedGroup: GroupType;
  onViewChange: (view: PMView, group?: GroupType) => void;
  userName: string;
  userImage: string;
}

export function PMSidebar({
  activeView,
  selectedGroup,
  onViewChange,
  userName,
  userImage,
}: PMSidebarProps) {
  const isHistoricosExpanded = activeView === "historicos";
  const isFlaggearExpanded = activeView === "flaggear";

  return (
    <SidebarShell userName={userName} userImage={userImage}>
      {/* Mi Progreso */}
      <SidebarNavButton
        label="Mi Progreso"
        isActive={activeView === "progreso"}
        onClick={() => onViewChange("progreso")}
      />

      {/* Históricos */}
      <SidebarExpandable
        label="Históricos"
        isExpanded={isHistoricosExpanded}
        isActive={isHistoricosExpanded}
        onToggle={() => onViewChange("historicos", selectedGroup ?? "A")}
      >
        {GROUPS.map((g) => (
          <SidebarSubItem
            key={g}
            label={`Grupo ${g}`}
            isActive={activeView === "historicos" && selectedGroup === g}
            onClick={() => onViewChange("historicos", g)}
          />
        ))}
      </SidebarExpandable>

      {/* Flaggear */}
      <SidebarExpandable
        label="Flaggear"
        isExpanded={isFlaggearExpanded}
        isActive={isFlaggearExpanded}
        onToggle={() => onViewChange("flaggear", selectedGroup ?? "A")}
      >
        {GROUPS.map((g) => (
          <SidebarSubItem
            key={g}
            label={`Grupo ${g}`}
            isActive={activeView === "flaggear" && selectedGroup === g}
            onClick={() => onViewChange("flaggear", g)}
          />
        ))}
      </SidebarExpandable>

      {/* Encuestas */}
      <SidebarNavButton
        label="Encuestas"
        isActive={activeView === "encuestas"}
        onClick={() => onViewChange("encuestas")}
      />
    </SidebarShell>
  );
}
