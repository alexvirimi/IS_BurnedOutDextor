"use client"

import { useState } from "react"
import { ChevronDown, ChevronUp } from "lucide-react"
import Image from "next/image"

interface SidebarProps {
  activeView: string
  setActiveView: (view: string) => void
}

export default function Sidebar({ activeView, setActiveView }: SidebarProps) {
  const isHistoricosActive = ["areas", "grupos", "trabajadores"].includes(activeView)
  const isEncuestasActive = ["crear-encuesta", "modificar-encuestas"].includes(activeView)
  
  const [historicosOpen, setHistoricosOpen] = useState(isHistoricosActive)
  const [encuestasOpen, setEncuestasOpen] = useState(isEncuestasActive)

  return (
    <aside className="fixed left-0 top-0 h-screen w-[280px] bg-background border-r border-secondary flex flex-col z-50">
      {/* User Profile */}
      <div className="flex flex-col items-center pt-8 pb-6 px-6">
        <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-primary mb-4 bg-secondary flex items-center justify-center">
          <Image
            src="/placeholder.svg?height=128&width=128"
            alt="Profile"
            width={128}
            height={128}
            className="w-full h-full object-cover"
          />
        </div>
        <h2 className="text-foreground font-semibold text-center">Nombre Apellido Apellido</h2>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-6 overflow-y-auto">
        {/* Mi Progreso */}
        <button
          onClick={() => setActiveView("mi-progreso")}
          className={`w-full text-left px-4 py-3 rounded-lg mb-2 transition-colors ${
            activeView === "mi-progreso"
              ? "bg-primary text-primary-foreground"
              : "border border-foreground/30 text-foreground hover:bg-secondary"
          }`}
        >
          <span className="font-medium">Mi Progreso</span>
        </button>

        {/* Históricos */}
        <div className="mb-2">
          <button
            onClick={() => setHistoricosOpen(!historicosOpen)}
            className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors ${
              isHistoricosActive
                ? "bg-primary text-primary-foreground"
                : "border border-foreground/30 text-foreground hover:bg-secondary"
            }`}
          >
            <span className="font-medium">Históricos</span>
            {historicosOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          {historicosOpen && (
            <div className="ml-2 mt-1 bg-secondary rounded-lg overflow-hidden">
              <button
                onClick={() => setActiveView("areas")}
                className={`w-full text-left px-4 py-2 transition-colors ${
                  activeView === "areas" ? "bg-accent/30 font-semibold" : "hover:bg-accent/20"
                } text-foreground`}
              >
                Áreas
              </button>
              <button
                onClick={() => setActiveView("grupos")}
                className={`w-full text-left px-4 py-2 transition-colors ${
                  activeView === "grupos" ? "bg-accent/30 font-semibold" : "hover:bg-accent/20"
                } text-foreground`}
              >
                Grupos
              </button>
              <button
                onClick={() => setActiveView("trabajadores")}
                className={`w-full text-left px-4 py-2 transition-colors ${
                  activeView === "trabajadores" ? "bg-accent/30 font-semibold" : "hover:bg-accent/20"
                } text-foreground`}
              >
                Trabajadores
              </button>
            </div>
          )}
        </div>

        {/* Encuestas */}
        <div className="mb-2">
          <button
            onClick={() => setEncuestasOpen(!encuestasOpen)}
            className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors ${
              isEncuestasActive
                ? "bg-primary text-primary-foreground"
                : "border border-foreground/30 text-foreground hover:bg-secondary"
            }`}
          >
            <span className="font-medium">Encuestas</span>
            {encuestasOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          {encuestasOpen && (
            <div className="ml-2 mt-1 bg-secondary rounded-lg overflow-hidden">
              <button
                onClick={() => setActiveView("crear-encuesta")}
                className={`w-full text-left px-4 py-2 transition-colors ${
                  activeView === "crear-encuesta" ? "bg-accent/30 font-semibold" : "hover:bg-accent/20"
                } text-foreground`}
              >
                Crear Encuesta
              </button>
              <button
                onClick={() => setActiveView("modificar-encuestas")}
                className={`w-full text-left px-4 py-2 transition-colors ${
                  activeView === "modificar-encuestas" ? "bg-accent/30 font-semibold" : "hover:bg-accent/20"
                } text-foreground`}
              >
                Modificar Encuestas
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* Burnout Risk & Logo */}
      <div className="px-6 pb-6">
        <div className="bg-secondary rounded-lg p-4 mb-4">
          <h3 className="font-semibold text-foreground text-sm">Riesgo de Burn Out</h3>
          <div className="flex justify-between items-center">
            <span className="text-primary text-sm">Poco Probable</span>
            <span className="text-foreground text-sm">15%</span>
          </div>
        </div>
        <div className="flex justify-center">
          <BudLogo />
        </div>
      </div>
    </aside>
  )
}

function BudLogo() {
  return (
    <svg width="120" height="53" viewBox="0 0 504 224" fill="none" xmlns="http://www.w3.org/2000/svg">
      <g opacity="0.9">
        <path d="M186.798 68.0543C196.792 61.1322 209.423 60.9735 219.178 67.2646C225.472 71.3247 227.309 78.9437 227.309 85.642V104.489C227.532 111.173 230.745 116.311 235.553 119.864C240.406 123.45 246.9 125.419 253.503 125.567C260.106 125.714 266.657 124.037 271.64 120.534C276.562 117.074 280.028 111.788 280.551 104.456V80.306C280.551 77.2652 280.771 73.1786 283.673 70.4567C287.305 67.0504 293.287 65.0937 299.481 64.7187C305.716 64.3413 312.523 65.5402 317.943 68.8464C323.093 71.9885 324.82 78.0088 325.361 83.1993C327.908 107.663 328.961 128.428 328.013 145.794C327.065 163.149 324.113 177.227 318.563 188.246C312.987 199.317 304.819 207.241 293.606 212.284C282.45 217.301 268.38 219.422 251.033 219.114C233.468 219.278 219.451 217.079 208.489 212.041C197.459 206.971 189.628 199.075 184.4 188.093C179.2 177.17 176.601 163.25 175.866 146.116C175.131 128.97 176.258 108.476 178.603 84.3353C179.186 78.3315 181.338 71.8367 186.798 68.0543ZM297.102 166.85C297.102 161.955 291.57 159.019 287.294 161.483C261.046 161.56 243.08 161.56 217.319 161.597C213.09 159.113 207.559 162.005 207.558 166.869C207.558 169.016 208.709 171.011 210.598 172.07C242.687 190.053 261.969 190.322 294.057 172.098C295.952 171.022 297.102 169.012 297.102 166.85Z" fill="#2694D2"/>
        <path d="M35.0711 3.21038C30.0365 0.29243 24.4574 -1.70374 17.0343 2.07032L16.9633 2.1062L16.8961 2.14704C11.0515 5.67079 5.34428 9.19507 2.31851 13.4643C0.752018 15.6749 -0.140915 18.1352 0.0182201 20.911C0.17589 23.6583 1.35435 26.544 3.59131 29.6483L3.65857 29.7424L3.73951 29.829C15.4571 42.5475 20.1578 62.0614 22.3181 79.8696C24.4794 97.6864 21.2101 112.598 19.7675 131.187C14.0286 168.567 7.45786 193.909 32.5206 212.915C57.5833 231.922 119.982 228.096 145.488 188.816C173.269 146.033 160.577 95.3459 130.755 83.7835C119.162 79.2887 105.651 75.9235 90.8533 77.4255C87.3749 77.84 86.9475 78.8604 87.4888 81.355C93.3904 109.055 89.1722 132.652 86.7209 137.523C85.6743 140.707 81.6197 145.759 77.7938 145.759C69.7197 145.759 71.5653 142.1 72.055 137.523C85.4456 88.106 50.3748 12.08 35.0711 3.21038Z" fill="#2694D2"/>
        <path d="M468.929 3.21038C473.963 0.29243 479.543 -1.70374 486.966 2.07032L487.037 2.1062L487.104 2.14704C492.948 5.67079 498.656 9.19507 501.681 13.4643C503.248 15.6749 504.141 18.1352 503.982 20.911C503.824 23.6583 502.646 26.544 500.409 29.6483L500.341 29.7424L500.261 29.829C488.543 42.5475 483.842 62.0614 481.682 79.8696C479.521 97.6864 482.79 112.598 484.233 131.187C489.971 168.567 496.542 193.909 471.48 212.915C446.417 231.922 384.018 228.096 358.512 188.816C330.731 146.033 343.423 95.3459 373.245 83.7835C384.838 79.2887 398.349 75.9235 413.147 77.4255C416.625 77.84 417.052 78.8604 416.511 81.355C410.61 109.055 414.828 132.652 417.279 137.523C418.326 140.707 422.38 145.759 426.206 145.759C434.28 145.759 432.435 142.1 431.945 137.523C418.554 88.106 453.625 12.08 468.929 3.21038Z" fill="#2694D2"/>
      </g>
    </svg>
  )
}
