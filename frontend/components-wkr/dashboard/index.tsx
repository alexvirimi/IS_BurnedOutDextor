"use client"

import { useState } from "react"
import { Sidebar } from "./sidebar"
import { EncuestasView } from "./encuestas-view"
import { ProgresoView } from "./progreso-view"

const USER_IMAGE = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face"

export function Dashboard() {
  const [activeTab, setActiveTab] = useState<"progreso" | "encuestas">("encuestas")
  const userName = "Nombre Apellido Apellido"
  const userFirstName = "<USUARIO>"

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        userName={userName}
        userImage={USER_IMAGE}
      />
      <main className="flex-1 flex">
        {activeTab === "encuestas" ? (
          <EncuestasView userName={userFirstName} />
        ) : (
          <ProgresoView />
        )}
      </main>
    </div>
  )
}
