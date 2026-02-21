"use client";

import { Lesson } from "../types/exerciseDetail";

interface LessonListProps {
  lessons: Lesson[];
  onLessonClick: (lessonId: string) => void;
}

export default function LessonList({ lessons, onLessonClick }: LessonListProps) {
  return (
    <div className="space-y-2">
      {lessons.map((lesson) => (
        <div
          key={lesson.id}
          onClick={() => onLessonClick(lesson.id)}
          className="flex items-start gap-4 p-4 bg-[#FDFEF0] border-4 border-[#14532D] cursor-pointer hover:bg-[#FCD34D] transition-colors"
          style={{
            boxShadow: "4px 4px 0 #14532D",
          }}
        >
          <div className="flex-shrink-0 w-12 h-12 bg-[#4ADE80] border-2 border-[#14532D] flex items-center justify-center">
            <span className="text-2xl font-bold text-[#14532D]">
              {String(lesson.number).padStart(2, "0")}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-bold text-[#14532D] mb-1">
              {lesson.title}
            </h3>
            <p className="text-sm text-[#14532D]">{lesson.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
