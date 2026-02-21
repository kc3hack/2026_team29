"""
ハンズオン演習生成サービス

LLMを使用してドキュメントからハンズオン演習を生成するビジネスロジック
"""

import json
from app.core.llm import invoke_llm
from app.core.prompts import QUEST_GENERATION_TEMPLATE


async def generate_handson_quest(
    document_content: str,
    user_rank: int = 0,
    user_skills: str = "",
) -> dict:
    """
    LLMを使用してハンズオン演習を生成

    Args:
        document_content: 学習対象のドキュメント
        user_rank: ユーザーのランク（0-9、デフォルト=0）
        user_skills: ユーザーの得意分野（オプション）

    Returns:
        {
            "title": str,
            "difficulty": str,
            "estimated_time_minutes": int,
            "learning_objectives": list[str],
            "steps": list[dict],
            "resources": list[str]
        }

    Note:
        - JSONパースエラー時はデフォルト値を返す
        - 生成品質の向上は後続Issueで対応
    """
    # プロンプトテンプレートに入力値を埋め込む
    prompt = QUEST_GENERATION_TEMPLATE.format(
        document_content=document_content,
        user_rank=user_rank,
        user_skills=user_skills or "未指定",
    )

    # LLMに非同期で呼び出し (temperature=0.7で創造性を持たせる)
    response = await invoke_llm(prompt=prompt, temperature=0.7)

    # Markdownコードブロックを除去（LLMが```json ... ```で囲む場合がある）
    cleaned_response = response.strip()
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:]  # "```json" を削除
    elif cleaned_response.startswith("```"):
        cleaned_response = cleaned_response[3:]  # "```" を削除
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]  # 末尾の "```" を削除
    cleaned_response = cleaned_response.strip()

    # JSONパース（エラーハンドリング付き）
    try:
        result = json.loads(cleaned_response)
        # 必須フィールドの存在確認
        required_fields = ["title", "difficulty", "steps"]
        if not all(k in result for k in required_fields):
            raise ValueError("Missing required fields in LLM response")
        return result
    except (json.JSONDecodeError, ValueError) as e:
        # LLMがJSON以外を返した場合のフォールバック
        print(f"❌ JSON parse error: {e}")
        print(f"📝 LLM Response (first 500 chars): {response[:500]}")
        print(f"📝 LLM Response (last 500 chars): {response[-500:]}")
        print("⚠️  Returning fallback response.")
        return {
            "title": "演習生成エラー",
            "difficulty": "beginner",
            "estimated_time_minutes": 30,
            "learning_objectives": ["ドキュメントの内容理解"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "ドキュメントを読む",
                    "description": "提供されたドキュメントを読んで理解を深めてください。",
                    "code_example": "",
                    "checkpoints": ["ドキュメントの概要を理解した"],
                }
            ],
            "resources": [],
        }
