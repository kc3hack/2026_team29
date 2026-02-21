"use client";

/**
 * Exercise Menu Page（認証必須）
 */

import React from "react";
import { withAuth } from "@/lib/auth/withAuth";
import { ExerciseMenu } from "@/features/exercise/components/ExerciseMenu";

function ExercisePage() {
  return (
    <div className="h-full w-full">
      <ExerciseMenu />
    </div>
  );
}

export default withAuth(ExercisePage);
