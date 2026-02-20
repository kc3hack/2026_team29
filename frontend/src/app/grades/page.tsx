'use client';

/**
 * Grade Page
 * 成績を表示するページ
 */

import React from 'react';
import { GradesContainer } from '@/features/grades/components/GradesContainer';

export default function GradePage() {
  return (
    <div className="h-full w-full">
      <GradesContainer />
    </div>
  );
}
