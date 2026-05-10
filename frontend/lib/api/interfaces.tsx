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

export interface Question {
  id: string;
  text: string;
  psicometric_variable: string;
}

export interface SurveyWithQuestions {
  id: string;
  name: string;
  questions: Question[];
}
