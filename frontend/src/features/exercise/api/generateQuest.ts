/**
 * AI Quest Generation API Client（Issue #98）
 * POST /api/v1/quest/generate
 */

import type { QuestGenerationRequest, QuestGenerationResponse } from "../types";

function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

/**
 * ドキュメントからAIハンズオン演習を生成する
 *
 * @param req - 生成リクエスト（document_content のみ送信。user_rank は別 Issue で対応）
 * @returns 生成されたQuestGenerationResponse
 * @throws APIエラー時にエラーをスロー
 */
export async function generateQuest(
  req: QuestGenerationRequest,
): Promise<QuestGenerationResponse> {
  const url = `${getApiBaseUrl()}/api/v1/quest/generate`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    const errorText = await response.text();
    let detail = `ステータス: ${response.status}`;
    try {
      const json = JSON.parse(errorText);
      if (json.detail) {
        // FastAPIの422バリデーションエラーは配列の場合がある
        if (Array.isArray(json.detail)) {
          detail = json.detail
            .map(
              (err: { loc?: string[]; msg: string }) =>
                `${err.loc?.join(".") || "field"}: ${err.msg}`,
            )
            .join(", ");
        } else if (typeof json.detail === "string") {
          detail = json.detail;
        } else {
          detail = JSON.stringify(json.detail);
        }
      }
    } catch {
      detail = errorText || detail;
    }
    throw new Error(`演習の生成に失敗しました。${detail}`);
  }

  return response.json() as Promise<QuestGenerationResponse>;
}
