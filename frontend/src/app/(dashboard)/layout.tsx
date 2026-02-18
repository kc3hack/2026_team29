/**
 * Dashboard Layout
 * ダッシュボード機能用のレイアウト（ロジックはなく、フロートのみ）
 */

export const metadata = {
  title: 'Dashboard',
  description: 'Your personal dashboard',
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
