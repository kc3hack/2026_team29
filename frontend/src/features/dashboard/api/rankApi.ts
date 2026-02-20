const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface RankAnalysisRequest {
  github_username: string;
  repository_count: number;
  total_commits: number;
  primary_languages: string[];
  years_of_experience: number;
}

export interface RankAnalysisResponse {
  user_id: number;
  rank: number;
  rank_label: string;
  reasoning: string;
  recommended_learning_paths: string[];
  analyzed_at: string;
}

export async function analyzeRank(
  request: RankAnalysisRequest
): Promise<RankAnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analyze/rank`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Rank analysis failed: ${response.statusText}`);
  }

  return response.json();
}
