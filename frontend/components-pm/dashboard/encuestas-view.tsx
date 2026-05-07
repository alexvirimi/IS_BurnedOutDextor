"use client"

interface EncuestasViewProps {
  userName: string
}

const encuestas = [
  { id: 1, title: "Realizar encuesta de seguimiento 2026-4-2" },
  { id: 2, title: "Realizar encuesta mensual 2026-4" },
]

export function EncuestasView({ userName }: EncuestasViewProps) {
  return (
    <div className="flex-1 p-8 lg:p-12 overflow-auto">
      <div className="max-w-3xl">
        {/* Greeting */}
        <h1 className="font-heading font-bold text-foreground text-3xl lg:text-4xl uppercase tracking-tight">
          {userName}, QUE LINDO VOLVER A VERTE
        </h1>

        {/* Message */}
        <p className="font-sans text-foreground text-lg mt-6 leading-relaxed">
          Esta semana te esforzaste tanto que necesitas un respiro de tu ámbiente laboral.
        </p>
        <p className="font-sans text-primary text-lg mt-4">
          Respira con nosotros.
        </p>

        {/* Surveys List */}
        <div className="mt-16 flex flex-col gap-4">
          {encuestas.map((encuesta) => (
            <button
              key={encuesta.id}
              className="w-full text-left px-6 py-4 bg-secondary rounded-lg font-sans text-secondary-foreground hover:bg-secondary/80 transition-colors"
            >
              {encuesta.title}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
