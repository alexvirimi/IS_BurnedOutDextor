"use client";

import {
  SidebarShell,
  SidebarNavButton,
} from "@/components/dashboard/shared/sidebar-shell";

export type WKRTab = "progreso" | "encuestas";

interface WKRSidebarProps {
  activeTab: WKRTab;
  onTabChange: (tab: WKRTab) => void;
  userName: string;
}

export function WKRSidebar({
  activeTab,
  onTabChange,
  userName,
}: WKRSidebarProps) {
  return (
    <SidebarShell userName={userName}>
      <SidebarNavButton
        label="Mi Progreso"
        isActive={activeTab === "progreso"}
        onClick={() => onTabChange("progreso")}
      />
      <SidebarNavButton
        label="Encuestas"
        isActive={activeTab === "encuestas"}
        onClick={() => onTabChange("encuestas")}
      />
    </SidebarShell>
  );
}
