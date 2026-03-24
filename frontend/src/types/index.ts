/**
 * TypeScript types that mirror the Pydantic models from the backend.
 * Keep these in sync with backend/app/schemas/__init__.py
 */

export type Persona =
  | "software_engineering"
  | "product_management"
  | "operations_marketing"
  | "ui_ux_design";

export interface ExperienceEntry {
  title: string;
  company: string;
  start_date: string;
  end_date: string;
  bullets: string[];
  persona_tags: Persona[];
}

export interface EducationEntry {
  institution: string;
  degree: string;
  field_of_study: string;
  graduation_year: number;
  gpa?: number | null;
  highlights: string[];
}

export interface ProjectEntry {
  name: string;
  description: string;
  technologies: string[];
  persona_tags: Persona[];
  url?: string | null;
}

export interface Resume {
  name: string;
  email: string;
  phone: string;
  linkedin: string;
  github: string;
  website: string;
  summary: string;
  experience: ExperienceEntry[];
  education: EducationEntry[];
  projects: ProjectEntry[];
  skills: string[];
  persona: Persona | null;
}

export interface CoverLetter {
  company: string;
  role: string;
  prose: string;
  word_count: number;
}

export interface InterviewQuestion {
  question: string;
  category: string;
  hint: string;
}

export interface InterviewScript {
  role: string;
  company: string;
  questions: InterviewQuestion[];
  prep_resources: string[];
  estimated_duration_minutes: number;
}

export interface OrchestrationRequest {
  job_description: string;
  company: string;
  role: string;
  persona: Persona;
}

export interface OrchestrationResponse {
  resume: Resume;
  cover_letter: CoverLetter;
  interview_script: InterviewScript;
}
