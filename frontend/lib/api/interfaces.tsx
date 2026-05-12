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
  id: string; // relation ID (used for DELETE)
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

/**
 * Mirrors backend QuestionComplete — returned by GET /survey/{id}/complete.
 * The `id` field here is the question_survey (join-table) id, which is what
 * POST /answers/bulk expects as `id_question_survey`.
 */
export interface QuestionComplete {
  id: string; // question_survey id  ← used as id_question_survey
  question_text: string;
  psicometric_variable: PsicometricVariable | string;
}

export interface AnswerOption {
  value: number;
  label: string;
}

/** Mirrors backend SurveyComplete from GET /survey/{id}/complete */
export interface SurveyComplete {
  id: string;
  name: string;
  aperture_date: string;
  finishing_date: string;
  status: string;
  questions: QuestionComplete[];
  answer_options: AnswerOption[];
}

/** Single item in the bulk-answer payload */
export interface BulkAnswerItem {
  id_question_survey: string;
  value: number; // 1–5  (AnswerEnum)
}

/** Body for POST /answers/bulk */
export interface BulkAnswerPayload {
  id_survey: string;
  answers: BulkAnswerItem[];
}
