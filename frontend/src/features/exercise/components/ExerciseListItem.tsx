'use client';

import React from 'react';
import Link from 'next/link';
import { Exercise } from '../types';

interface ExerciseListItemProps {
  exercise: Exercise;
}

export function ExerciseListItem({ exercise }: ExerciseListItemProps) {
  const getStatusIcon = (status: Exercise['status']) => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'in-progress':
        return '▶';
      case 'not-started':
        return '○';
    }
  };

  const getStatusColor = (status: Exercise['status']) => {
    switch (status) {
      case 'completed':
        return 'text-[#4ADE80]';
      case 'in-progress':
        return 'text-[#FCD34D]';
      case 'not-started':
        return 'text-[#94A3B8]';
    }
  };

  return (
    <Link
      href={`/exercises/${exercise.category}/${exercise.id}`}
      className="block w-full bg-[#FDFEF0] border-2 border-[#3A7E56] px-6 py-4 text-left transition-all hover:bg-[#F0F7F0] hover:border-[#2C5F2D] hover:shadow-md group"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 flex-1">
          <span className={`text-2xl font-bold ${getStatusColor(exercise.status)}`}>
            {getStatusIcon(exercise.status)}
          </span>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-[#2C5F2D] group-hover:text-[#1a4023]">
              {exercise.title}
            </h3>
            {exercise.completionRate !== undefined && exercise.status === 'in-progress' && (
              <div className="mt-1 flex items-center gap-2">
                <div className="w-32 h-2 bg-[#D1D5DB] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#4ADE80] transition-all"
                    style={{ width: `${exercise.completionRate}%` }}
                  />
                </div>
                <span className="text-xs text-[#6B7280]">{exercise.completionRate}%</span>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm text-[#6B7280]">
          <span className="font-medium">{exercise.estimatedTime}分</span>
          <span className="text-2xl text-[#3A7E56] group-hover:translate-x-1 transition-transform">›</span>
        </div>
      </div>
    </Link>
  );
}
