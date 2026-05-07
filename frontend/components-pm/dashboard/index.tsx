"use client"

import { useState } from "react"
import { Sidebar, type ViewType, type GroupType } from "./sidebar"
import { EncuestasView } from "./encuestas-view"
import { ProgresoView } from "./progreso-view"
import { HistoricosView } from "./historicos-view"
import { FlaggearView } from "./flaggear-view"

const USER_IMAGE = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face"

interface DashboardProps {
  role?: "worker" | "pm"
}

export function Dashboard({ role = "pm" }: DashboardProps) {
  const [activeView, setActiveView] = useState<ViewType>("encuestas")
  const [selectedGroup, setSelectedGroup] = useState<GroupType>(null)
  const userName = "Nombre Apellido Apellido"
  const userFirstName = "<USUARIO>"

  const handleViewChange = (view: ViewType, group?: GroupType) => {
    setActiveView(view)
    if (group !== undefined) {
      setSelectedGroup(group)
    }
  }

  const renderView = () => {
    switch (activeView) {
      case "encuestas":
        return <EncuestasView userName={userFirstName} />
      case "progreso":
        return <ProgresoView />
      case "historicos":
        return <HistoricosView group={selectedGroup} />
      case "flaggear":
        return <FlaggearView group={selectedGroup} />
      default:
        return <EncuestasView userName={userFirstName} />
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar
        activeView={activeView}
        selectedGroup={selectedGroup}
        onViewChange={handleViewChange}
        userName={userName}
        userImage={USER_IMAGE}
        role={role}
      />
      <main className="ml-72 flex-1 min-h-screen overflow-y-auto">
        {renderView()}
      </main>
    </div>
  )
}
