'use client';

import { useState, useRef, useEffect } from 'react';
import { getCurrentUser } from '@/lib/api/auth';
import { generateSkillTree } from '@/lib/api/skillTree';

// ランク名マッピング（rank番号からランク名を取得）
const RANK_NAMES = [
  '種子', // rank 0
  '芽', // rank 1
  '若木', // rank 2
  '樹', // rank 3
  '母樹', // rank 4
  '賢樹', // rank 5
  '神樹', // rank 6
  '世界樹', // rank 7
];

// UserInfo型定義（getCurrentUserの戻り値に合わせる）
interface UserInfo {
  id: number;
  username: string;
  rank: number;
  exp: number;
  created_at: string;
  updated_at: string;
}

// RankAnalysisResponse互換の型（既存コードとの互換性のため）
export interface RankAnalysisResponse {
  percentile: number;
  rank: number;
  rank_name: string;
  reasoning: string;
}

type MeasurementState = 
  | 'idle' 
  | 'charging' 
  | 'fetching'
  | 'analyzing' 
  | 'calculating'
  | 'finalizing'
  | 'revealing' 
  | 'complete' 
  | 'error';

interface RankMeasurementProps {
  onComplete?: (rank: RankAnalysisResponse) => void;
}

export function RankMeasurement({ onComplete }: RankMeasurementProps) {
  const [state, setState] = useState<MeasurementState>('idle');
  const [chargeProgress, setChargeProgress] = useState(0);
  const [rankResult, setRankResult] = useState<RankAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [skillTreeGenerating, setSkillTreeGenerating] = useState(false);

  const chargeTimerRef = useRef<NodeJS.Timeout | null>(null);
  const decreaseTimerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(0);
  const isPressingRef = useRef(false);

  // チャージ時間（ミリ秒）
  const CHARGE_DURATION = 35000; // 35秒でじっくり焦らす
  const FETCHING_DURATION = 2000; // GitHub情報取得
  const ANALYZING_DURATION = 3000; // AI分析中
  const CALCULATING_DURATION = 2000; // ランク計算中
  const FINALIZING_DURATION = 2000; // 最終確認中
  const REVEAL_DURATION = 8000; // 豪華アニメーション時間

  // カスタムイージング関数：最初の15%の時間で30%まで到達、残り85%の時間で30-100%を激遅に
  const customEasing = (t: number): number => {
    if (t < 0.15) {
      // 最初の15%の時間（6秒）で30%まで到達
      return (t / 0.15) * 0.3;
    } else {
      // 残り85%の時間（34秒）で30-100%へ（どんどん遅くなる）
      const normalizedT = (t - 0.15) / 0.85; // 0.15-1.0を0-1に正規化
      const eased = 1 - Math.pow(1 - normalizedT, 5); // 5乗で超強力な減速
      return 0.3 + eased * 0.7; // 30%-100%の範囲
    }
  };

  // 長押し開始
  const handlePressStart = () => {
    if (state !== 'idle' && state !== 'charging') return;
    
    // 減るアニメーション中なら止める
    if (decreaseTimerRef.current) {
      clearInterval(decreaseTimerRef.current);
      decreaseTimerRef.current = null;
    }
    
    isPressingRef.current = true;
    setState('charging');
    
    // 現在のchargeProgressから逆算して開始時刻を調整
    const currentProgress = chargeProgress;
    // 現在のprogressに対応する時間を逆算
    let initialElapsed = 0;
    if (currentProgress > 0) {
      // progressから時間を逆算（カスタムイージングの逆関数）
      const normalizedProgress = currentProgress / 100;
      if (normalizedProgress <= 0.3) {
        initialElapsed = normalizedProgress * CHARGE_DURATION * 0.15 / 0.3;
      } else {
        const p = (normalizedProgress - 0.3) / 0.7;
        const t = 1 - Math.pow(1 - p, 0.2); // 5乗の逆は1/5乗
        initialElapsed = (0.15 + t * 0.85) * CHARGE_DURATION;
      }
    }

    // チャージプログレスアニメーション（カスタムイージング適用）
    // performance.now()はsetIntervalコールバック内で呼び出す
    startTimeRef.current = 0; // リセット（0は未初期化を示す）
    chargeTimerRef.current = setInterval(() => {
      // 初回のみ開始時刻を設定
      if (startTimeRef.current === 0) {
        startTimeRef.current = performance.now() - initialElapsed;
      }
      
      const elapsed = performance.now() - startTimeRef.current;
      const linearProgress = Math.min(elapsed / CHARGE_DURATION, 1);
      
      // カスタムイージング適用：最初は速く、後半激遅
      const easedProgress = customEasing(linearProgress) * 100;
      setChargeProgress(easedProgress);

      if (easedProgress >= 100) {
        if (chargeTimerRef.current) {
          clearInterval(chargeTimerRef.current);
        }
        // 100%を表示してから0.5秒後に次のステップへ
        setChargeProgress(100);
        setTimeout(() => {
          handleChargeComplete();
        }, 500);
      }
    }, 16); // ~60fps
  };

  // 長押し解除（途中でキャンセル）
  const handlePressEnd = () => {
    isPressingRef.current = false;
    
    // 100%に達していたら何もしない
    if (chargeProgress >= 100) return;
    
    if (state === 'charging' && chargeProgress < 100) {
      // チャージ完了前にリリースした場合は一気に減らす
      if (chargeTimerRef.current) {
        clearInterval(chargeTimerRef.current);
      }
      
      // 一気に減らすアニメーション（2秒で0まで）
      const currentProgress = chargeProgress;
      decreaseTimerRef.current = setInterval(() => {
        setChargeProgress((prev) => {
          const newProgress = prev - (currentProgress / 120); // 120フレーム（2秒）で0に
          if (newProgress <= 0) {
            if (decreaseTimerRef.current) {
              clearInterval(decreaseTimerRef.current);
              decreaseTimerRef.current = null;
            }
            setState('idle');
            return 0;
          }
          return newProgress;
        });
      }, 16);
    }
  };

  // チャージ完了時
  const handleChargeComplete = async () => {
    // ステップ1: GitHub情報取得中
    setState('fetching');
    await new Promise(resolve => setTimeout(resolve, FETCHING_DURATION));
    
    // ステップ2: AI分析中
    setState('analyzing');
    await new Promise(resolve => setTimeout(resolve, ANALYZING_DURATION));
    
   // ステップ3: ランク計算中
    setState('calculating');
    await new Promise(resolve => setTimeout(resolve, CALCULATING_DURATION));
    
    // ステップ4: 最終確認中
    setState('finalizing');
    await new Promise(resolve => setTimeout(resolve, FINALIZING_DURATION));
    
    try {
      // OAuth完了時にバックエンドで既に判定されたランク情報を取得
      const userInfo = await getCurrentUser();

      // RankAnalysisResponse形式に変換
      const result: RankAnalysisResponse = {
        rank: userInfo.rank,
        rank_name: RANK_NAMES[userInfo.rank] || '不明',
        percentile: (userInfo.rank / 7) * 100, // 暫定: rank0-7を0-100%に変換
        reasoning: `GitHub統計情報に基づいて自動判定されました。あなたのランクは「${RANK_NAMES[userInfo.rank] || '不明'}」です。`,
      };

      setRankResult(result);
      setState('revealing');

      // 豪華アニメーション中に裏でスキルツリー生成
      setSkillTreeGenerating(true);
      generateSkillTreeInBackground();

      // アニメーション後に完了状態へ
      setTimeout(() => {
        setState('complete');
        onComplete?.(result);
      }, REVEAL_DURATION);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'ランク測定に失敗しました');
      setState('error');
    }
  };

  // スキルツリーをバックグラウンドで生成
  const generateSkillTreeInBackground = async () => {
    try {
      // 複数カテゴリのスキルツリーを非同期で生成
      const categories = ['web', 'ai', 'security', 'infrastructure', 'game', 'design'];
      await Promise.all(
        categories.map(category => generateSkillTree(category))
      );
      setSkillTreeGenerating(false);
    } catch (err) {
      console.error('スキルツリー生成エラー:', err);
      setSkillTreeGenerating(false);
    }
  };

  // リセット
  const handleReset = () => {
    setState('idle');
    setChargeProgress(0);
    setRankResult(null);
    setError(null);
    setSkillTreeGenerating(false);
  };

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (chargeTimerRef.current) {
        clearInterval(chargeTimerRef.current);
      }
    };
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      {/* ゲーム調の装飾ボックス */}
      <div className="relative w-full max-w-2xl">
        {/* コーナー装飾 */}
        <div className="absolute -top-2 -left-2 w-8 h-8 bg-[#14532D] border-4 border-[#FCD34D]" />
        <div className="absolute -top-2 -right-2 w-8 h-8 bg-[#14532D] border-4 border-[#FCD34D]" />
        <div className="absolute -bottom-2 -left-2 w-8 h-8 bg-[#14532D] border-4 border-[#FCD34D]" />
        <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-[#14532D] border-4 border-[#FCD34D]" />
        
        <div className="relative bg-[#FDFEF0] p-12 border-8 border-[#14532D] shadow-[16px_16px_0_rgba(0,0,0,0.3)]" style={{ 
          backgroundImage: 'radial-gradient(circle, rgba(20,83,45,0.05) 1px, transparent 1px)',
          backgroundSize: '20px 20px'
        }}>
      {/* アイドル状態とチャージ中：測定ボタン */}
      {(state === 'idle' || state === 'charging') && (
        <div className="text-center space-y-6">
          <h2 className="text-4xl font-bold text-[#14532D] animate-pulse">
            🌱 あなたのスキルランクを判定します
          </h2>
          <p className="text-xl text-gray-600 leading-relaxed">
            ボタンを<span className="text-[#4ADE80] font-bold">じっくり</span>長押ししてください
          </p>
          <div className="flex justify-center gap-3 text-2xl mb-4">
            <span className="animate-bounce">💪</span>
            <span className="animate-bounce" style={{ animationDelay: '200ms' }}>🔥</span>
            <span className="animate-bounce" style={{ animationDelay: '400ms' }}>⚡</span>
          </div>
          <button
            onMouseDown={handlePressStart}
            onMouseUp={handlePressEnd}
            onMouseLeave={handlePressEnd}
            onTouchStart={handlePressStart}
            onTouchEnd={handlePressEnd}
            className="relative px-24 py-5 text-3xl font-bold text-white bg-[#14532D] border-8 border-[#14532D] shadow-[12px_12px_0_rgba(0,0,0,0.4)] hover:shadow-[16px_16px_0_rgba(0,0,0,0.4)] active:translate-y-2 active:shadow-[6px_6px_0_rgba(0,0,0,0.4)] transition-all cursor-pointer select-none overflow-visible"
            style={state === 'idle' ? { animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' } : {}}
          >
            {/* オーラエフェクト */}
            {state === 'charging' && chargeProgress > 0 && (
              <>
                <div 
                  className="absolute inset-0 rounded-lg animate-pulse"
                  style={{
                    boxShadow: `0 0 ${20 + chargeProgress * 0.5}px ${10 + chargeProgress * 0.3}px rgba(74, 222, 128, ${0.3 + chargeProgress * 0.005})`,
                    animation: 'pulse 1s ease-in-out infinite'
                  }}
                />
                <div 
                  className="absolute inset-0 rounded-lg"
                  style={{
                    boxShadow: `0 0 ${40 + chargeProgress}px ${20 + chargeProgress * 0.5}px rgba(252, 211, 77, ${0.2 + chargeProgress * 0.003})`,
                    animation: 'pulse 0.8s ease-in-out infinite'
                  }}
                />
              </>
            )}
            
            {/* チャージプログレスバー（ボタン内に表示） */}
            {state === 'charging' && (
              <div
                className="absolute left-0 bottom-0 h-full bg-linear-to-r from-[#4ADE80] to-[#FCD34D] transition-all duration-100 opacity-40"
                style={{ width: `${chargeProgress}%` }}
              />
            )}
            
            <div className="relative z-10 flex flex-col items-center gap-2">
              <span className="text-5xl">🎯</span>
              <span>ランクを測定</span>
              {state === 'idle' ? (
                <span className="text-lg opacity-80">長押しでスタート</span>
              ) : (
                <span className="text-lg opacity-90">{Math.floor(chargeProgress)}% チャージ中</span>
              )}
            </div>
          </button>
          {state === 'idle' ? (
            <p className="text-sm text-gray-500 mt-4">
              ※ GitHubの活動履歴からAIが自動判定します<br />
              <span className="text-xs opacity-75">気長にお待ちください...</span>
            </p>
          ) : (
            <div className="space-y-2 mt-4">
              <p className="text-sm text-gray-600 animate-pulse">
                ボタンを押し続けてください...
              </p>
              {/* 応援メッセージ（最初から余白確保） */}
              <div className="h-5">
                {chargeProgress > 50 && chargeProgress <= 80 && (
                  <p className="text-xs text-[#4ADE80] animate-pulse">
                    🌱 もうすぐです... あと少し！
                  </p>
                )}
                {chargeProgress > 80 && (
                  <p className="text-xs text-[#FCD34D] animate-bounce">
                    ✨ ラストスパート！
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* GitHub情報取得中 */}
      {state === 'fetching' && (
        <div className="text-center space-y-6 animate-fadeIn">
          <div className="text-6xl animate-bounce">📡</div>
          <h2 className="text-2xl font-bold text-[#14532D] animate-pulse">
            GitHub情報を取得中...
          </h2>
          <div className="flex gap-2 justify-center">
            <div className="w-3 h-3 bg-[#4ADE80] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-3 h-3 bg-[#4ADE80] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-3 h-3 bg-[#4ADE80] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <p className="text-sm text-gray-600">
            あなたのリポジトリを解析しています
          </p>
        </div>
      )}

      {/* AI分析中 */}
      {state === 'analyzing' && (
        <div className="text-center space-y-6 animate-fadeIn">
          <div className="text-6xl animate-pulse">🤖</div>
          <h2 className="text-2xl font-bold text-[#14532D]">
            AIが深層学習中...
          </h2>
          <div className="max-w-md mx-auto space-y-2">
            <div className="h-2 bg-gray-300 rounded overflow-hidden">
              <div className="h-full bg-[#4ADE80] animate-[width_2s_ease-in-out_infinite]" style={{ width: '70%' }} />
            </div>
            <p className="text-xs text-gray-500">コードの品質を分析中...</p>
          </div>
        </div>
      )}

      {/* ランク計算中 */}
      {state === 'calculating' && (
        <div className="text-center space-y-6 animate-fadeIn">
          <div className="text-6xl animate-spin">⚙️</div>
          <h2 className="text-2xl font-bold text-[#14532D] animate-pulse">
            ランクを計算中...
          </h2>
          <div className="flex flex-col gap-2 items-center">
            <div className="text-4xl">🌱 ➔ 🌿 ➔ 🌳</div>
            <p className="text-sm text-gray-600">
              あなたのスキルレベルを判定しています
            </p>
          </div>
        </div>
      )}

      {/* 最終確認中 */}
      {state === 'finalizing' && (
        <div className="text-center space-y-6 animate-fadeIn">
          <div className="text-6xl animate-pulse">✨</div>
          <h2 className="text-2xl font-bold text-[#14532D]">
            最終確認中...
          </h2>
          <div className="flex gap-3 justify-center text-3xl">
            {['📊', '📈', '📉', '💯'].map((emoji, i) => (
              <span
                key={i}
                className="animate-bounce"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                {emoji}
              </span>
            ))}
          </div>
          <p className="text-sm text-gray-600 animate-pulse">
            もうすぐ結果が出ます...！
          </p>
        </div>
      )}

      {/* ランク確定アニメーション */}
      {(state === 'revealing' || state === 'complete') && rankResult && (
        <div className="text-center space-y-8 animate-fadeIn">
          {/* 超豪華なランク表示 */}
          <div className="relative">
            {/* 背景グロー効果 */}
            <div className="absolute inset-0 bg-[#FCD34D] blur-3xl opacity-50 animate-pulse" />
            <div className="absolute inset-0 bg-[#4ADE80] blur-2xl opacity-30 animate-pulse" style={{ animationDelay: '500ms' }} />
            
            <div className="relative">
              {/* ランクアイコン */}
              <div className="text-9xl mb-4 animate-bounce animate-glow">
                🌳
              </div>
              
              {/* ファンファーレテキスト */}
              <div className="mb-4 text-6xl font-bold animate-pulse">
                🎉 ✨ 🎊
              </div>
              
              {/* ランク番号 */}
              <h2 className="text-7xl font-bold text-[#14532D] mb-4 [text-shadow:6px_6px_0_#FCD34D] animate-scaleIn">
                ランク {rankResult.rank}
              </h2>
              
              {/* ランク名 */}
              <p className="text-5xl font-bold text-[#4ADE80] [text-shadow:3px_3px_0_black] animate-pulse">
                {rankResult.rank_name}
              </p>
              
              {/* パーセンタイル */}
              <p className="mt-4 text-2xl text-gray-700 font-bold">
                上位 {100 - rankResult.percentile}% のスキルレベル！
              </p>
            </div>
          </div>

          {/* 超派手なパーティクルエフェクト */}
          <div className="flex justify-center gap-3 text-5xl flex-wrap max-w-2xl mx-auto">
            {['✨', '🎉', '⭐', '🌟', '💫', '🎊', '🎈', '🎆', '🔥', '💎', '👑', '🏆'].map((emoji, i) => (
              <span
                key={i}
                className="animate-bounce animate-sparkle"
                style={{ 
                  animationDelay: `${i * 120}ms`,
                  animationDuration: `${1.5 + (i % 3) * 0.3}s`
                }}
              >
                {emoji}
              </span>
            ))}
          </div>

          {/* カウントアップエフェクト風 */}
          <div className="flex justify-center gap-8 text-xl font-bold">
            <div className="text-center">
              <div className="text-4xl text-[#4ADE80] animate-pulse">🔥</div>
              <div>コミット数</div>
              <div className="text-2xl">計測中...</div>
            </div>
            <div className="text-center">
              <div className="text-4xl text-[#FCD34D] animate-pulse">⚡</div>
              <div>コード品質</div>
              <div className="text-2xl">A+</div>
            </div>
            <div className="text-center">
              <div className="text-4xl text-[#14532D] animate-pulse">🎯</div>
              <div>成長速度</div>
              <div className="text-2xl">高速</div>
            </div>
          </div>

          {/* 判定理由 */}
          <div className="max-w-lg mx-auto p-6 bg-white border-8 border-black shadow-[12px_12px_0_rgba(0,0,0,0.3)] animate-scaleIn">
            <h3 className="text-2xl font-bold text-[#14532D] mb-3 flex items-center justify-center gap-2">
              <span>📝</span>
              <span>AIの判定理由</span>
            </h3>
            <p className="text-gray-700 leading-relaxed text-lg">
              {rankResult.reasoning}
            </p>
          </div>

          {/* スキルツリー構築中表示（さらに目立つように） */}
          {skillTreeGenerating && (
            <div className="relative p-6 bg-[#14532D] text-white border-8 border-[#FCD34D] animate-pulse overflow-hidden">
              <div className="absolute inset-0 bg-linear-to-r from-transparent via-white/10 to-transparent animate-[shimmer_2s_infinite]" />
              <div className="relative flex items-center justify-center gap-4 text-2xl font-bold">
                <span className="text-4xl animate-bounce">🌲</span>
                <span>あなた専用のスキルツリーを構築中...</span>
                <span className="text-4xl animate-bounce" style={{ animationDelay: '300ms' }}>🌲</span>
              </div>
              <div className="mt-3 text-center text-sm opacity-75">
                GitHubのリポジトリを解析して、最適な学習パスを生成しています
              </div>
            </div>
          )}

          {/* 完了時のボタン */}
          {state === 'complete' && !skillTreeGenerating && (
            <button
              onClick={handleReset}
              className="px-12 py-4 text-xl font-bold text-white bg-[#4ADE80] border-8 border-black shadow-[8px_8px_0_black] hover:translate-y-2 hover:shadow-[4px_4px_0_black] transition-all animate-scaleIn"
            >
              🚀 ダッシュボードへ進む
            </button>
          )}
        </div>
      )}

      {/* エラー表示 */}
      {state === 'error' && (
        <div className="text-center space-y-6">
          <div className="text-6xl">❌</div>
          <h2 className="text-2xl font-bold text-red-600">
            エラーが発生しました
          </h2>
          <p className="text-gray-700">{error}</p>
          <button
            onClick={handleReset}
            className="px-8 py-3 font-bold text-white bg-gray-600 border-4 border-black shadow-[4px_4px_0_black] hover:translate-y-1 hover:shadow-[2px_2px_0_black] transition-all"
          >
            やり直す
          </button>
        </div>
      )}
        </div>
      </div>
    </div>
  );
}
