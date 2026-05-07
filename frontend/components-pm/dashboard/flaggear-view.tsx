"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import type { GroupType } from "./sidebar"

interface Employee {
  id: number
  name: string
  image: string
}

const employeesByGroup: Record<GroupType, Employee[]> = {
  A: [
    { id: 1, name: "Carlos Rodríguez", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
    { id: 2, name: "María González", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
    { id: 3, name: "Juan Pérez", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
    { id: 4, name: "Ana Martínez", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
    { id: 5, name: "Pedro López", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
    { id: 6, name: "Laura Sánchez", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
    { id: 7, name: "Diego Torres", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
    { id: 8, name: "Sofía Ramírez", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
    { id: 9, name: "Andrés Castro", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
    { id: 10, name: "Valentina Díaz", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
    { id: 11, name: "Fernando Ruiz", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
    { id: 12, name: "Camila Herrera", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=256&h=256&fit=crop&crop=face" },
  ],
  B: [
    { id: 1, name: "Isabella Moreno", image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=256&h=256&fit=crop&crop=face" },
    { id: 2, name: "Sebastián Vargas", image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=256&h=256&fit=crop&crop=face" },
    { id: 3, name: "Daniela Ortiz", image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=256&h=256&fit=crop&crop=face" },
    { id: 4, name: "Mateo Jiménez", image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=256&h=256&fit=crop&crop=face" },
    { id: 5, name: "Luciana Reyes", image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=256&h=256&fit=crop&crop=face" },
    { id: 6, name: "Nicolás Mendoza", image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=256&h=256&fit=crop&crop=face" },
    { id: 7, name: "Gabriela Flores", image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=256&h=256&fit=crop&crop=face" },
    { id: 8, name: "Alejandro Ríos", image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=256&h=256&fit=crop&crop=face" },
  ],
  C: [
    { id: 1, name: "Regina Salazar", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=256&h=256&fit=crop&crop=face" },
    { id: 2, name: "Emilio Guzmán", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=256&h=256&fit=crop&crop=face" },
    { id: 3, name: "Paula Navarro", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=256&h=256&fit=crop&crop=face" },
    { id: 4, name: "Ricardo Aguilar", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=256&h=256&fit=crop&crop=face" },
    { id: 5, name: "Mariana Vega", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=256&h=256&fit=crop&crop=face" },
    { id: 6, name: "Santiago Molina", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=256&h=256&fit=crop&crop=face" },
    { id: 7, name: "Catalina Rojas", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=256&h=256&fit=crop&crop=face" },
    { id: 8, name: "Tomás Guerrero", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=256&h=256&fit=crop&crop=face" },
    { id: 9, name: "Andrea Paredes", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=256&h=256&fit=crop&crop=face" },
    { id: 10, name: "Felipe Campos", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=256&h=256&fit=crop&crop=face" },
  ],
}

interface FlaggearViewProps {
  group: GroupType
}

export function FlaggearView({ group }: FlaggearViewProps) {
  const [selectedEmployees, setSelectedEmployees] = useState<Set<number>>(new Set())

  // Reset selection when group changes
  useEffect(() => {
    setSelectedEmployees(new Set())
  }, [group])

  const employees = employeesByGroup[group]

  const toggleEmployee = (id: number) => {
    setSelectedEmployees((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const isSelected = (id: number) => selectedEmployees.has(id)

  return (
    <div className="flex-1 p-8 lg:p-12 overflow-auto">
      <div className="max-w-4xl">
        {/* Title */}
        <h1 className="font-heading font-bold text-foreground text-3xl lg:text-4xl uppercase tracking-tight">
          GRUPO {group}
        </h1>

        {/* Employee Grid */}
        <div className="mt-8 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {employees.map((employee) => (
            <button
              key={employee.id}
              onClick={() => toggleEmployee(employee.id)}
              className={`p-4 rounded-xl border transition-all ${
                isSelected(employee.id)
                  ? "bg-secondary border-secondary"
                  : "bg-background border-border hover:border-primary/30"
              }`}
            >
              <div className="flex flex-col items-center">
                <div className={`w-24 h-24 rounded-full overflow-hidden border-4 ${
                  isSelected(employee.id) 
                    ? "border-primary/30" 
                    : "border-border"
                }`}>
                  <Image
                    src={employee.image}
                    alt={employee.name}
                    width={96}
                    height={96}
                    className="w-full h-full object-cover"
                  />
                </div>
                <span className={`mt-3 font-sans text-xs text-center leading-tight ${
                  isSelected(employee.id) 
                    ? "text-secondary-foreground font-medium" 
                    : "text-foreground"
                }`}>
                  {employee.name}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
