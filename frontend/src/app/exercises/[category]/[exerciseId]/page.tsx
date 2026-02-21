"use client";

import { use, useEffect, useState } from "react";
import { ExerciseDetail } from "@/features/exercise/types/exerciseDetail";
import { getExerciseDetail } from "@/features/exercise/api/mockExerciseDetail";
import LessonList from "@/features/exercise/components/LessonList";
import ConfirmationTest from "@/features/exercise/components/ConfirmationTest";
import Link from "next/link";

interface PageProps {
  params: Promise<{
    category: string;
    exerciseId: string;
  }>;
}

export default function ExerciseDetailPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const [exercise, setExercise] = useState<ExerciseDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadExercise = async () => {
      setLoading(true);
      const data = await getExerciseDetail(resolvedParams.exerciseId);
      setExercise(data);
      setLoading(false);
    };

    loadExercise();
  }, [resolvedParams.exerciseId]);

  const handleLessonClick = (lessonId: string) => {
    console.log("Lesson clicked:", lessonId);
  };

  const handleTestSubmit = (answer: string) => {
    console.log("Test submitted:", answer);
    alert("解答を送信しました！実際のアプリではここで採点処理を行います。");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FDFEF0] flex items-center justify-center">
        <div className="text-[#14532D] text-2xl font-bold">Loading...</div>
      </div>
    );
  }

  if (!exercise) {
    return (
      <div className="min-h-screen bg-[#FDFEF0] flex items-center justify-center">
        <div className="text-[#14532D] text-2xl font-bold">
          演習が見つかりません
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FDFEF0] p-8">
      <div className="max-w-5xl mx-auto">
        {/* ヘッダー */}
        <div className="mb-8">
          <Link
            href={`/exercises/${resolvedParams.category}`}
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#FDFEF0] border-4 border-[#14532D] text-[#14532D] font-bold hover:bg-[#4ADE80] transition-colors mb-6"
            style={{
              boxShadow: "4px 4px 0 #000",
            }}
          >
            <span className="text-xl">←</span>
            <span>戻る</span>
          </Link>

          <div
            className="bg-[#4ADE80] border-4 border-black p-6"
            style={{
              boxShadow: "8px 8px 0 #000",
            }}
          >
            <div className="flex items-center gap-4 mb-2">
              <span className="px-4 py-1 bg-[#FCD34D] border-2 border-black text-black font-bold text-sm">
                通常演習
              </span>
            </div>
            <h1 className="text-4xl font-bold text-black">{exercise.title}</h1>
          </div>
        </div>

        {/* レッスンリスト */}
        {exercise.lessons.length > 0 && (
          <div className="mb-8">
            <LessonList
              lessons={exercise.lessons}
              onLessonClick={handleLessonClick}
            />
          </div>
        )}

        {/* 確認テスト */}
        {exercise.confirmationTest && (
          <ConfirmationTest
            testId={exercise.confirmationTest.id}
            title={exercise.confirmationTest.title}
            description={exercise.confirmationTest.description}
            type={exercise.confirmationTest.type}
            problem={exercise.confirmationTest.problem}
            choices={exercise.confirmationTest.choices}
            placeholder={exercise.confirmationTest.placeholder}
            onSubmit={handleTestSubmit}
          />
        )}
      </div>
    </div>
  );
}
