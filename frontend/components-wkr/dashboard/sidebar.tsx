"use client"

import Image from "next/image"
import { BudLogo } from "@/components/icons"

interface SidebarProps {
  activeTab: "progreso" | "encuestas"
  onTabChange: (tab: "progreso" | "encuestas") => void
  userName: string
  userImage: string
}

export function Sidebar({ activeTab, onTabChange, userName, userImage }: SidebarProps) {
  return (
    <aside className="w-72 min-h-screen bg-background flex flex-col border-r border-border">
      {/* User Profile */}
      <div className="flex flex-col items-center pt-8 px-6">
        <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-primary/20 mb-4">
          <Image
            src={userImage}
            alt={userName}
            width={128}
            height={128}
            className="w-full h-full object-cover"
          />
        </div>
        <h2 className="font-heading font-bold text-foreground text-center text-sm">
          {userName}
        </h2>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-2 mt-8 px-6">
        <button
          onClick={() => onTabChange("progreso")}
          className={`w-full text-left px-4 py-3 rounded-lg font-sans text-sm transition-colors ${
            activeTab === "progreso"
              ? "bg-primary text-primary-foreground font-medium"
              : "bg-transparent border border-border text-foreground hover:bg-muted"
          }`}
        >
          Mi Progreso
        </button>
        <button
          onClick={() => onTabChange("encuestas")}
          className={`w-full text-left px-4 py-3 rounded-lg font-sans text-sm transition-colors ${
            activeTab === "encuestas"
              ? "bg-primary text-primary-foreground font-medium"
              : "bg-transparent border border-border text-foreground hover:bg-muted"
          }`}
        >
          Encuestas
        </button>
      </nav>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Burn Out Risk Card */}
      <div className="px-6 mb-6">
        <div className="bg-muted rounded-lg p-4">
          <h3 className="font-heading font-bold text-foreground text-sm">
            Riesgo de Burn Out
          </h3>
          <div className="flex justify-between items-center mt-1">
            <span className="text-primary text-sm font-sans">Poco Probable</span>
            <span className="text-foreground text-sm font-sans">15%</span>
          </div>
        </div>
      </div>

      {/* Logo */}
      <div className="flex justify-center pb-8">
        <BudLogo className="w-24 h-auto" />
      </div>
    </aside>
  )
}
