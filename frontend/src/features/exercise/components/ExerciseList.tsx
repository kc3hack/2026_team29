'use client';

import React, { useState, useEffect } from 'react';
import { Exercise, DifficultyLevel, DIFFICULTY_LABELS } from '../types';
import { ExerciseListItem } from './ExerciseListItem';
import { getExercisesByCategory } from '../api/mock';

interface ExerciseListProps {
  category: string;
}

const DIFFICULTY_TABS: DifficultyLevel[] = ['beginner', 'intermediate', 'advanced', 'expert'];

export function ExerciseList({ category }: ExerciseListProps) {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeDifficulty, setActiveDifficulty] = useState<DifficultyLevel>('beginner');

  useEffect(() => {
    const fetchExercises = async () => {
      setLoading(true);
      try {
        const data = await getExercisesByCategory(category);
        setExercises(data);
      } catch (error) {
        console.error('Failed to fetch exercises:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchExercises();
  }, [category]);

  const filteredExercises = exercises.filter((ex) => ex.difficulty === activeDifficulty);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#3A7E56]"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Difficulty Tabs */}
      <div className="flex gap-2 mb-6 border-b-2 border-[#3A7E56] pb-2">
        {DIFFICULTY_TABS.map((difficulty) => {
          const isActive = activeDifficulty === difficulty;
          const count = exercises.filter((ex) => ex.difficulty === difficulty).length;
          
          return (
            <button
              key={difficulty}
              onClick={() => setActiveDifficulty(difficulty)}
              className={`px-6 py-2 font-bold text-lg transition-all ${
                isActive
                  ? 'text-[#2C5F2D] border-b-4 border-[#2C5F2D] -mb-[10px]'
                  : 'text-[#6B7280] hover:text-[#3A7E56]'
              }`}
            >
              {DIFFICULTY_LABELS[difficulty]}
              {count > 0 && (
                <span className="ml-2 text-sm opacity-70">({count})</span>
              )}
            </button>
          );
        })}
      </div>

      {/* Exercise List */}
      <div className="flex-1 space-y-3">
        {filteredExercises.length > 0 ? (
          filteredExercises.map((exercise) => (
            <ExerciseListItem
              key={exercise.id}
              exercise={exercise}
            />
          ))
        ) : (
          <div className="flex flex-col items-center justify-center h-48 text-[#6B7280]">
            <div className="text-6xl mb-4">📝</div>
            <p className="text-lg">この難易度の演習はまだありません</p>
          </div>
        )}
      </div>
    </div>
  );
}
