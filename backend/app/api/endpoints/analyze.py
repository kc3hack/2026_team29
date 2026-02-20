"""
ランク判定APIエンドポイント

Issue #35: AI実装Phase 2 - モックAPIエンドポイント
Issue #36: AI実装Phase 3 - ランク判定AI（LLM実装）
Issue #54: AI実装Phase 3 - スキルツリー生成（LLMパーソナライゼーション）
Issue #57: AI実装Phase 3 - 演習生成（LLM実装）

POST /api/v1/analyze/rank - ユーザーランクの判定（LLM実装、issue #36）
POST /api/v1/analyze/skill-tree - スキルツリー生成（LLM実装、issue #54）
POST /api/v1/analyze/quest - 演習生成（LLM実装、issue #57）
"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.analyze import (
    RankAnalysisRequest,
    RankAnalysisResponse,
    SkillTreeRequest,
    SkillTreeResponse,
    QuestGenerationRequest,
    QuestGenerationResponse,
    QuestResource,
)
from app.services.rank_service import analyze_user_rank
from app.services.skill_tree_service import generate_skill_tree_ai
from app.services.quest_service import generate_handson_quest
from app.crud.user import get_user
from app.db.session import get_db

router = APIRouter()


@router.post("/rank", response_model=RankAnalysisResponse)
async def analyze_rank(request: RankAnalysisRequest) -> RankAnalysisResponse:
    """
    ユーザーのランクをLLMで判定

    Args:
        request: ランク判定リクエスト

    Returns:
        RankAnalysisResponse: ランク判定結果

    Raises:
        HTTPException 500: LLM呼び出し失敗時

    Example:
        Request:
            {
                "github_username": "octocat",
                "portfolio_text": "個人サイト: https://example.com",
                "qiita_id": "example_user",
                "other_info": "LeetCode参加者"
            }

        Response:
            {
                "percentile": 65.0,
                "rank": 4,
                "rank_name": "母樹",
                "reasoning": "複数の技術スタックでの実装経験が確認されました。"
            }
    """
    try:
        result = await analyze_user_rank(
            github_username=request.github_username,
            portfolio_text=request.portfolio_text,
            qiita_id=request.qiita_id,
            other_info=request.other_info,
        )
        return RankAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rank analysis failed: {str(e)}")


@router.post("/skill-tree", response_model=SkillTreeResponse)
async def generate_skill_tree(
    request: SkillTreeRequest, db: Session = Depends(get_db)
) -> SkillTreeResponse:
    """
    スキルツリー生成（LLM実装 - Issue #54）

    Args:
        request: スキルツリー生成リクエスト（user_id, category）
        db: DBセッション

    Returns:
        SkillTreeResponse: パーソナライズされたスキルツリーデータ

    Note:
        - user_id から Profile と SkillTree テーブルを参照
        - GitHub APIでリポジトリを分析（習得済みスキル推定）
        - LLMでパーソナライズされたロードマップを生成
        - キャッシュ機能（7日間）: generated_atが新しければDBから返却

    Example:
        Request:
            {
                "user_id": 1,
                "category": "web"
            }

        Response:
            {
                "category": "web",
                "tree_data": {
                    "nodes": [...],
                    "edges": [...],
                    "metadata": {...}
                },
                "generated_at": "2026-02-20T12:00:00+09:00"
            }
    """
    try:
        result = await generate_skill_tree_ai(
            user_id=request.user_id, category=request.category, db=db
        )
        return result
    except HTTPException:
        # HTTPExceptionはそのまま再送出
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Skill tree generation failed: {str(e)}"
        )


@router.post("/quest", response_model=QuestGenerationResponse)
async def generate_quest(
    request: QuestGenerationRequest, db: Session = Depends(get_db)
) -> QuestGenerationResponse:
    """
    演習生成（LLM実装 - Issue #57）

    Args:
        request: 演習生成リクエスト（user_id, category, difficulty, document_text）
        db: DBセッション

    Returns:
        QuestGenerationResponse: LLMで生成された演習データ

    Note:
        実装内容:
        - user_id からユーザーのrankを取得
        - LLM（Claude/GPT/Gemini）でdocument_textから演習を生成
        - temperature=0.7で創造的な演習を生成

    Example:
        Request:
            {
                "user_id": 1,
                "category": "web",
                "difficulty": 4,
                "document_text": "FastAPIのドキュメント..."
            }

        Response:
            {
                "id": 101,
                "title": "FastAPI認証付きTodo API構築",
                "description": "JWT認証を実装し...",
                "difficulty": 4,
                "category": "web",
                "is_generated": true,
                "steps": ["1. FastAPIプロジェクト初期化", ...],
                "estimated_time_minutes": 120,
                "resources": [...],
                "created_at": "2026-02-20T12:00:00+09:00"
            }
    """
    try:
        # ユーザーのrankを取得
        user = get_user(db, request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # LLMでクエスト生成
        llm_result = await generate_handson_quest(
            document_content=request.document_text or "基礎的な内容",
            user_rank=user.rank,
            user_skills="",  # 今後、skill_treeやbadgeから推測可能
        )

        # LLM出力をAPIレスポンスにマッピング
        difficulty_map = {
            "beginner": max(0, min(2, request.difficulty)),
            "intermediate": max(3, min(5, request.difficulty)),
            "advanced": max(6, min(9, request.difficulty)),
        }
        mapped_difficulty = difficulty_map.get(
            llm_result.get("difficulty", "intermediate"), request.difficulty
        )

        # steps: list[dict] → list[str]
        steps_list = []
        for step in llm_result.get("steps", []):
            if isinstance(step, dict):
                step_text = f"{step.get('step_number', '')}. {step.get('title', '')} - {step.get('description', '')}"
                steps_list.append(step_text)
            else:
                steps_list.append(str(step))

        # resources: list[str] → list[QuestResource]
        resources_list = []
        for res in llm_result.get("resources", []):
            if isinstance(res, str):
                resources_list.append(QuestResource(title=res, url="#"))
            elif isinstance(res, dict):
                resources_list.append(
                    QuestResource(
                        title=res.get("title", "参考資料"), url=res.get("url", "#")
                    )
                )

        # description: learning_objectives → 文字列
        learning_objectives = llm_result.get("learning_objectives", [])
        description = (
            ", ".join(learning_objectives)
            if learning_objectives
            else "LLMで生成された演習"
        )

        return QuestGenerationResponse(
            id=999,  # DBに保存しないため仮のID
            title=llm_result.get("title", "演習"),
            description=description,
            difficulty=mapped_difficulty,
            category=request.category,
            is_generated=True,
            steps=steps_list,
            estimated_time_minutes=llm_result.get("estimated_time_minutes", 60),
            resources=resources_list,
            created_at=datetime.now(timezone.utc),
        )

    except HTTPException:
        # HTTPExceptionはそのまま再送出
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Quest generation failed: {str(e)}"
        )
