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
  userImage: string;
}

export function WKRSidebar({
  activeTab,
  onTabChange,
  userName,
  userImage,
}: WKRSidebarProps) {
  return (
    <SidebarShell userName={userName} userImage={userImage}>
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
