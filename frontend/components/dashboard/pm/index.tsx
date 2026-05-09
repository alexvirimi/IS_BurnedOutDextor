"use client";

import { useState } from "react";
import { PMSidebar, type PMView, type GroupType } from "./sidebar";
import { PMEncuestasView } from "./views/encuestas-view";
import { PMProgresoView } from "./views/progreso-view";
import { PMHistoricosView } from "./views/historicos-view";
import { PMFlaggearView } from "./views/flaggear-view";

const USER_IMAGE =
  "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face";

export function PMDashboard() {
  const [activeView, setActiveView] = useState<PMView>("encuestas");
  const [selectedGroup, setSelectedGroup] = useState<GroupType>(null);

  const handleViewChange = (view: PMView, group?: GroupType) => {
    setActiveView(view);
    if (group !== undefined) setSelectedGroup(group);
  };

  const renderView = () => {
    switch (activeView) {
      case "encuestas":
        return <PMEncuestasView userName="<USUARIO>" />;
      case "progreso":
        return <PMProgresoView />;
      case "historicos":
        return <PMHistoricosView group={selectedGroup} />;
      case "flaggear":
        return <PMFlaggearView group={selectedGroup} />;
      default:
        return <PMEncuestasView userName="<USUARIO>" />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <PMSidebar
        activeView={activeView}
        selectedGroup={selectedGroup}
        onViewChange={handleViewChange}
        userName="Nombre Apellido Apellido"
        userImage={USER_IMAGE}
      />
      <main className="ml-72 flex-1 min-h-screen overflow-y-auto">
        {renderView()}
      </main>
    </div>
  );
}
