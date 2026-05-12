// ─── lib/api/interfaces.tsx (reemplaza el archivo existente) ─────────────────
// Añade SurveyWorkerAssignment y AssignmentTarget manteniendo todos los tipos previos.

export interface Area {
  id: string;
  name: string;
}

export interface Group {
  id: string;
  name: string;
  id_area: string;
  id_leader: string | null;
}

export interface Worker {
  id: string;
  name: string;
  last_names: string;
  id_group: string;
}

export interface Survey {
  id: string;
  name: string;
  aperture_date: string;
  finishing_date: string;
  status: string;
}

export interface PsicometricVariable {
  id: string;
  name: string;
}

export interface Question {
  id: string;
  text: string;
  psicometric_variable: PsicometricVariable | string;
}

export interface QuestionSurveyRelation {
  id: string;
  id_survey: string;
  id_question: string;
}

export interface SurveyWithQuestions {
  id: string;
  name: string;
  questions: Question[];
}

/** Mirrors backend MySurveyResponse from /survey-assignment/my-surveys */
export interface MySurveyResponse {
  id: string;
  name: string;
  aperture_date: string;
  finishing_date: string;
  status: string;
  assignment_id: string;
  questions_count: number;
  already_responded: boolean;
}

/** Mirrors backend SurveyWorkerAssignmentResponse */
export interface SurveyWorkerAssignment {
  id: string;
  id_survey: string;
  id_worker: string;
  created_at: string;
}

// ─── Discriminated union para el scope de asignación ─────────────────────────
// Diseñado para ser extensible: añadir nuevos scopes (cargo, sede, equipo)
// solo requiere agregar un nuevo case aquí y un filtro en assignmentService.

export type AssignmentTarget =
  | { type: "empresa" }
  | { type: "area"; areaId: string }
  | { type: "grupo"; grupoId: string }
  | { type: "trabajador"; trabajadorId: string }
  // Casos futuros (no implementados aún, reservados para extensión):
  | { type: "cargo"; cargoId: string }
  | { type: "sede"; sedeId: string }
  | { type: "equipo"; equipoId: string };
