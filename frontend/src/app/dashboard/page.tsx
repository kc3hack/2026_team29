"use client";

/**
 * Dashboard Page
 * ダッシュボード機能のメインページ（認証必須）
 */

import { withAuth } from "@/lib/auth/withAuth";
import { DashboardContainer } from "@/features/dashboard/components/DashboardContainer";

function DashboardPage() {
  return <DashboardContainer />;
}

export default withAuth(DashboardPage);
