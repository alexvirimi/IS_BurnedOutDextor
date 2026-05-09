"use client";

import { useState } from "react";
import { WKRSidebar, type WKRTab } from "./sidebar";
import { WKREncuestasView } from "./views/encuestas-view";
import { WKRProgresoView } from "./views/progreso-view";

const USER_IMAGE =
  "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face";

export function WKRDashboard() {
  const [activeTab, setActiveTab] = useState<WKRTab>("encuestas");

  return (
    <div className="flex min-h-screen bg-background">
      <WKRSidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        userName="Nombre Apellido Apellido"
        userImage={USER_IMAGE}
      />
      <main className="flex-1 ml-72 min-h-screen overflow-y-auto flex">
        {activeTab === "encuestas" ? (
          <WKREncuestasView userName="<USUARIO>" />
        ) : (
          <WKRProgresoView />
        )}
      </main>
    </div>
  );
}
