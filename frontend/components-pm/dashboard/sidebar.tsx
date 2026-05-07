"use client"

import Image from "next/image"
import { BudLogo, ChevronDownIcon, ChevronUpIcon } from "@/components/icons"

export type ViewType = "progreso" | "encuestas" | "historicos" | "flaggear"
export type GroupType = "A" | "B" | "C" | null

interface SidebarProps {
  activeView: ViewType
  selectedGroup: GroupType
  onViewChange: (view: ViewType, group?: GroupType) => void
  userName: string
  userImage: string
  role: "worker" | "pm"
}

export function Sidebar({ 
  activeView, 
  selectedGroup,
  onViewChange, 
  userName, 
  userImage, 
  role 
}: SidebarProps) {
  const isHistoricosExpanded = activeView === "historicos"
  const isFlaggearExpanded = activeView === "flaggear"

  const groups: GroupType[] = ["A", "B", "C"]

  return (
    <aside className="w-72 h-screen bg-background flex flex-col border-r border-border fixed left-0 top-0 overflow-y-auto">
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
        {/* Mi Progreso */}
        <button
          onClick={() => onViewChange("progreso")}
          className={`w-full text-left px-4 py-3 rounded-lg font-sans text-sm transition-colors ${
            activeView === "progreso"
              ? "bg-primary text-primary-foreground font-medium"
              : "bg-transparent border border-border text-foreground hover:bg-muted"
          }`}
        >
          Mi Progreso
        </button>

        {/* Históricos - Only for PM */}
        {role === "pm" && (
          <div>
            <button
              onClick={() => onViewChange("historicos", selectedGroup || "A")}
              className={`w-full text-left px-4 py-3 rounded-lg font-sans text-sm transition-colors flex items-center justify-between ${
                isHistoricosExpanded
                  ? "bg-primary text-primary-foreground font-medium"
                  : "bg-transparent border border-border text-foreground hover:bg-muted"
              }`}
            >
              <span>Históricos</span>
              {isHistoricosExpanded ? (
                <ChevronUpIcon className="w-4 h-4" />
              ) : (
                <ChevronDownIcon className="w-4 h-4" />
              )}
            </button>
            {isHistoricosExpanded && (
              <div className="mt-1 bg-secondary rounded-lg overflow-hidden">
                {groups.map((group) => (
                  <button
                    key={group}
                    onClick={() => onViewChange("historicos", group)}
                    className={`w-full text-left px-6 py-2 font-sans text-sm transition-colors ${
                      selectedGroup === group
                        ? "bg-secondary/80 font-bold text-foreground"
                        : "text-foreground hover:bg-secondary/60"
                    }`}
                  >
                    Grupo {group}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Flaggear - Only for PM */}
        {role === "pm" && (
          <div>
            <button
              onClick={() => onViewChange("flaggear", selectedGroup || "A")}
              className={`w-full text-left px-4 py-3 rounded-lg font-sans text-sm transition-colors flex items-center justify-between ${
                isFlaggearExpanded
                  ? "bg-primary text-primary-foreground font-medium"
                  : "bg-transparent border border-border text-foreground hover:bg-muted"
              }`}
            >
              <span>Flaggear</span>
              {isFlaggearExpanded ? (
                <ChevronUpIcon className="w-4 h-4" />
              ) : (
                <ChevronDownIcon className="w-4 h-4" />
              )}
            </button>
            {isFlaggearExpanded && (
              <div className="mt-1 bg-secondary rounded-lg overflow-hidden">
                {groups.map((group) => (
                  <button
                    key={group}
                    onClick={() => onViewChange("flaggear", group)}
                    className={`w-full text-left px-6 py-2 font-sans text-sm transition-colors ${
                      selectedGroup === group
                        ? "bg-secondary/80 font-bold text-foreground"
                        : "text-foreground hover:bg-secondary/60"
                    }`}
                  >
                    Grupo {group}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Encuestas */}
        <button
          onClick={() => onViewChange("encuestas")}
          className={`w-full text-left px-4 py-3 rounded-lg font-sans text-sm transition-colors ${
            activeView === "encuestas"
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
