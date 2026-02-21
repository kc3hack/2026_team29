export type LessonType = "video" | "reading" | "practice";

export interface Lesson {
  id: string;
  number: number;
  title: string;
  type: LessonType;
  description: string;
  completed: boolean;
}

export interface ExerciseDetail {
  id: string;
  title: string;
  category: string;
  difficulty: "beginner" | "intermediate" | "advanced" | "expert";
  description: string;
  lessons: Lesson[];
  confirmationTest?: {
    id: string;
    title: string;
    description: string;
    type: "text" | "choice";
    problem: string;
    choices?: string[];
    placeholder?: string;
  };
}
