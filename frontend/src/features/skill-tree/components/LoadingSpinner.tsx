/**
 * LoadingSpinner Component
 * スキルツリー読み込み中の表示
 */

export const LoadingSpinner: React.FC = () => (
  <div className="absolute inset-0 flex items-center justify-center bg-[#0a0f08]/80 z-30">
    <div className="text-[#e8b849] text-xl font-bold text-center">
      🌱 スキルツリーを生成中...
    </div>
  </div>
);
