"use client";

import { useState } from "react";
import { HRSidebar, type HRView } from "./sidebar";
import { HRMiProgreso } from "./views/mi-progreso";
import { HRHistoricos } from "./views/historicos";
import { HRCrearEncuesta } from "./views/crear-encuesta";
import { HRModificarEncuestas } from "./views/modificar-encuestas";
import { useWorkerName } from "@/hooks/useWorkerName";

const USER_IMAGE =
  "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face";

export function HRDashboard() {
  const [activeView, setActiveView] = useState<HRView>("mi-progreso");
  const { fullName, isLoading } = useWorkerName();

  const renderView = () => {
    switch (activeView) {
      case "mi-progreso":
        return <HRMiProgreso />;
      case "areas":
        return <HRHistoricos type="areas" />;
      case "grupos":
        return <HRHistoricos type="grupos" />;
      case "trabajadores":
        return <HRHistoricos type="trabajadores" />;
      case "crear-encuesta":
        return <HRCrearEncuesta />;
      case "modificar-encuestas":
        return <HRModificarEncuestas />;
      default:
        return <HRMiProgreso />;
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      <HRSidebar
        activeView={activeView}
        onViewChange={setActiveView}
        userName={isLoading ? "..." : fullName}
      />
      <main className="flex-1 ml-72 min-h-screen overflow-y-auto">
        <div className="max-w-5xl">{renderView()}</div>
      </main>
    </div>
  );
}
