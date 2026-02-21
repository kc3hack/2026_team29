"use client";

/**
 * Grade Page
 * 成績を表示するページ（認証必須）
 */

import React from "react";
import { withAuth } from "@/lib/auth/withAuth";
import { GradesContainer } from "@/features/grades/components/GradesContainer";

function GradePage() {
  return (
    <div className="h-full w-full">
      <GradesContainer />
    </div>
  );
}

export default withAuth(GradePage);
