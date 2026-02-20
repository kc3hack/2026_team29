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
          repository_count: 15,
          total_commits: 350,
          primary_languages: ["TypeScript", "Python"],
          years_of_experience: 2,
        };

        const result = await analyzeRank(mockData);
        setRank(result);
      } catch (err) {
        setError(err as Error);
        setRank({
          user_id: 1,
          rank: 0,
          rank_label: "初心者",
          reasoning: "ランク判定に失敗しました",
          recommended_learning_paths: [],
          analyzed_at: new Date().toISOString(),
        });
      } finally {
        setLoading(false);
      }
    };

    fetchRank();
  }, [githubUsername]);

  return { rank, loading, error };
}
