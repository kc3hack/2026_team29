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
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import asyncio

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
from app.dependencies.auth import get_current_user
from app.models.user import User
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
    request: SkillTreeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SkillTreeResponse:
    """
    スキルツリー生成（LLM実装 - Issue #54, 認証必須 - Issue #61）

    Args:
        request: スキルツリー生成リクエスト（category）
        current_user: 認証済みユーザー（Cookieから自動取得）
        db: DBセッション

    Returns:
        SkillTreeResponse: パーソナライズされたスキルツリーデータ

    Note:
        - 認証済みユーザーのProfile と SkillTree テーブルを参照
        - GitHub APIでリポジトリを分析（習得済みスキル推定）
        - LLMでパーソナライズされたロードマップを生成
        - キャッシュ機能（10分）: generated_atが新しければDBから返却

    Example:
        Request:
            {
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
            user_id=current_user.id, category=request.category, db=db
        )
        return result
    except HTTPException:
        # HTTPExceptionはそのまま再送出
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Skill tree generation failed: {str(e)}"
        )


@router.get("/skill-tree/stream")
async def stream_skill_tree(
    category: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    スキルツリー生成（ストリーミング版 - プログレッシブ表示）

    Args:
        category: スキルカテゴリ (web, ai, game, etc.)
        current_user: 認証済みユーザー
        db: DBセッション

    Returns:
        StreamingResponse: Server-Sent Events (SSE) 形式でノード単位にストリーミング

    Note:
        - JSON Lines形式でLLMがノードを生成するたびに送信
        - フロントエンドで EventSource を使用してリアルタイム表示
        - 完了後はDBにキャッシュ保存

    Example:
        GET /api/v1/analyze/skill-tree/stream?category=web

        Response (SSE):
            data: {"type":"node","id":"html-css","name":"HTML/CSS基礎",...}

            data: {"type":"node","id":"javascript","name":"JavaScript基礎",...}

            data: {"type":"metadata","total_nodes":15,...}

            data: {"type":"done"}
    """
    from app.models.enums import SkillCategory
    from app.core.prompts_streaming import SKILL_TREE_STREAMING_TEMPLATE
    from app.core.llm import stream_llm
    from app.services.skill_tree_service import (
        RANK_NAMES,
        _load_baseline_json,
        _simplify_baseline_for_prompt,
    )
    from app.crud.profile import get_profile_by_user_id
    from app.services.github_service import analyze_github_profile
    from app.crud.skill_tree import update_skill_tree

    try:
        # カテゴリをenumに変換
        try:
            category_enum = SkillCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

        # ユーザー情報収集
        profile = get_profile_by_user_id(db, current_user.id)
        if profile is None:
            raise HTTPException(
                status_code=404, detail=f"User {current_user.id} not found"
            )

        # GitHub分析
        github_analysis = await analyze_github_profile(profile.github_username)

        # 習得済みスキル抽出
        acquired_skills = [
            skill_id
            for skill_id, completed in github_analysis.get(
                "completion_signals", {}
            ).items()
            if completed
        ]

        # ランク取得
        user_rank = profile.user.rank if profile.user else 0
        rank_name = RANK_NAMES.get(user_rank, "不明")

        # ベースライン簡略化
        baseline_data = _load_baseline_json(category_enum)
        simplified_baseline = _simplify_baseline_for_prompt(baseline_data)

        # プロンプト生成
        prompt = SKILL_TREE_STREAMING_TEMPLATE.format(
            rank=user_rank,
            rank_name=rank_name,
            github_username=profile.github_username or "未設定",
            tech_stack=", ".join(github_analysis.get("tech_stack", [])) or "なし",
            acquired_skills=", ".join(acquired_skills) or "なし",
            category=category_enum.value,
            baseline_json=simplified_baseline,
        )

        # ストリーミング生成
        async def generate_sse():
            """SSE形式でノードを順次送信"""
            buffer = ""
            nodes = []
            edges = []
            metadata = {}

            try:
                async for chunk in stream_llm(prompt, temperature=0.2):
                    buffer += chunk

                    # 改行ごとにJSON Lines をパース
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()

                        if not line or line.startswith("#"):
                            continue

                        try:
                            # JSONパース
                            data = json.loads(line)
                            data_type = data.get("type")

                            if data_type == "node":
                                nodes.append(data)
                                # SSE形式で送信
                                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                                await asyncio.sleep(
                                    0.1
                                )  # フロントエンドでの表示を見やすく

                            elif data_type == "edge":
                                edges.append(data)

                            elif data_type == "metadata":
                                metadata = data
                                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

                        except json.JSONDecodeError:
                            # JSON不完全の場合はスキップ
                            continue

                # 残りのバッファをチェック
                if buffer.strip():
                    try:
                        data = json.loads(buffer.strip())
                        data_type = data.get("type")
                        if data_type == "node":
                            nodes.append(data)
                            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                        elif data_type == "edge":
                            edges.append(data)
                        elif data_type == "metadata":
                            metadata = data
                            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    except json.JSONDecodeError:
                        pass

                # 完了通知 + DBキャッシュ保存
                tree_data = {"nodes": nodes, "edges": edges, "metadata": metadata}

                # 既存のスキルツリーを取得、なければ新規作成
                from app.crud.skill_tree import get_skill_tree_by_user_category
                from app.models.skill_tree import SkillTree as SkillTreeModel

                existing_tree = get_skill_tree_by_user_category(
                    db, current_user.id, category_enum
                )
                if existing_tree:
                    # 既存レコードを更新
                    update_skill_tree(db, current_user.id, category_enum, tree_data)
                else:
                    # 新規作成
                    new_tree = SkillTreeModel(
                        user_id=current_user.id,
                        category=category_enum.value,
                        tree_data=tree_data,
                        generated_at=datetime.now(timezone.utc),
                    )
                    db.add(new_tree)
                    db.commit()
                    db.refresh(new_tree)

                yield f'data: {{"type":"done","total_nodes":{len(nodes)}}}\n\n'

            except Exception as e:
                # エラー通知
                error_msg = json.dumps(
                    {"type": "error", "message": str(e)}, ensure_ascii=False
                )
                yield f"data: {error_msg}\n\n"

        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # nginx buffering無効化
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Stream generation failed: {str(e)}"
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
