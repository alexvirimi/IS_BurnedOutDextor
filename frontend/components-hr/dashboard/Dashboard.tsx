"use client"

import { useState } from "react"
import Sidebar from "./Sidebar"
import MiProgreso from "./views/MiProgreso"
import Historicos from "./views/Historicos"
import CrearEncuesta from "./views/CrearEncuesta"
import ModificarEncuestas from "./views/ModificarEncuestas"

type View = "mi-progreso" | "areas" | "grupos" | "trabajadores" | "crear-encuesta" | "modificar-encuestas"

export default function Dashboard() {
  const [activeView, setActiveView] = useState<View>("mi-progreso")

  const renderView = () => {
    switch (activeView) {
      case "mi-progreso":
        return <MiProgreso />
      case "areas":
        return <Historicos type="areas" />
      case "grupos":
        return <Historicos type="grupos" />
      case "trabajadores":
        return <Historicos type="trabajadores" />
      case "crear-encuesta":
        return <CrearEncuesta />
      case "modificar-encuestas":
        return <ModificarEncuestas />
      default:
        return <MiProgreso />
    }
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar activeView={activeView} setActiveView={(view) => setActiveView(view as View)} />
      <main className="flex-1 ml-[280px] h-screen overflow-y-auto">
        <div className="max-w-5xl">
          {renderView()}
        </div>
      </main>
    </div>
  )
}
