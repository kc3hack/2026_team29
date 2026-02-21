const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface RankAnalysisRequest {
  github_username: string;
  portfolio_text?: string;
  qiita_id?: string;
  other_info?: string;
}

export interface RankAnalysisResponse {
  percentile: number;
  rank: number;
  rank_name: string;
  reasoning: string;
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
