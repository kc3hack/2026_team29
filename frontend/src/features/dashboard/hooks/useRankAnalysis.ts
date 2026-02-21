'use client';

import { useState, useEffect } from "react";
import { analyzeRank, RankAnalysisResponse } from "../api/rankApi";

export function useRankAnalysis(githubUsername?: string) {
  const [rank, setRank] = useState<RankAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!githubUsername) return;

    const fetchRank = async () => {
      setLoading(true);
      try {
        const mockData = {
          github_username: githubUsername,
          portfolio_text: "個人サイト: https://example.com",
          qiita_id: "",
          other_info: "エンジニアコミュニティ活動",
        };

        const result = await analyzeRank(mockData);
        setRank(result);
      } catch (err) {
        setError(err as Error);
        setRank({
          percentile: 0,
          rank: 0,
          rank_name: "種子",
          reasoning: "ランク判定に失敗しました",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchRank();
  }, [githubUsername]);

  return { rank, loading, error };
}
