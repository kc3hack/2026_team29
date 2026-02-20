"""
ハンズオン演習生成サービスの統合テスト

実際のLLM APIを使用してquest_serviceをテスト。
環境変数に有効なAPIキーが必要。

実行方法:
    pytest tests/test_services/test_quest_service_integration.py -v -s
"""

import pytest
from app.services.quest_service import generate_handson_quest
from app.core.config import settings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_handson_quest_real_api():
    """
    実際のLLM APIを使用した演習生成テスト

    検証項目:
    - LLM APIが正常に応答する
    - レスポンスが正しいJSONスキーマに従っている
    - 必須フィールド（title, difficulty, steps）が含まれる
    """
    # APIキーが設定されているか確認
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set. Please set it in .env file.")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set. Please set it in .env file.")
    elif settings.LLM_PROVIDER.lower() == "gemini":
        if not settings.GEMINI_API_KEY or "REPLACE" in settings.GEMINI_API_KEY:
            pytest.skip("GEMINI_API_KEY not set. Please set it in .env file.")

    # テストリクエスト
    document_content = """
# Reactの基礎

Reactはユーザーインターフェースを構築するためのJavaScriptライブラリです。

## コンポーネント
Reactアプリケーションは再利用可能なコンポーネントで構成されます。

## State
コンポーネントの状態を管理するためにuseStateフックを使用します。

```jsx
const [count, setCount] = useState(0);
```
"""

    result = await generate_handson_quest(
        document_content=document_content,
        user_rank=3,
        user_skills="JavaScript, HTML/CSS",
    )

    # レスポンス検証
    assert isinstance(result, dict), "Result must be a dictionary"

    # 必須フィールドの存在確認
    assert "title" in result, "title field is missing"
    assert "difficulty" in result, "difficulty field is missing"
    assert "steps" in result, "steps field is missing"

    # フィールドの型確認
    assert isinstance(result["title"], str), "title must be string"
    assert len(result["title"]) > 0, "title must not be empty"

    assert isinstance(result["difficulty"], str), "difficulty must be string"
    assert result["difficulty"] in [
        "beginner",
        "intermediate",
        "advanced",
    ], "difficulty must be valid"

    assert isinstance(result["steps"], list), "steps must be list"
    assert len(result["steps"]) > 0, "steps must not be empty"

    # stepsの構造確認
    for step in result["steps"]:
        assert "step_number" in step, "step must have step_number"
        assert "title" in step, "step must have title"
        assert "description" in step, "step must have description"

    # デバッグ出力
    print("\n=== Quest Generation API Response ===")
    print(f"Title: {result['title']}")
    print(f"Difficulty: {result['difficulty']}")
    print(f"Steps: {len(result['steps'])} steps")
    if "estimated_time_minutes" in result:
        print(f"Estimated Time: {result['estimated_time_minutes']} minutes")

    # 各ステップの詳細を出力
    print("\n--- Steps Detail ---")
    for i, step in enumerate(result["steps"], 1):
        print(f"\nStep {i}: {step.get('title', 'N/A')}")
        print(f"  Description: {step.get('description', 'N/A')[:100]}...")
        if step.get("code_example"):
            print(f"  Code: {step.get('code_example')[:50]}...")

    # 学習目標とリソース
    if "learning_objectives" in result:
        print(f"\nLearning Objectives: {', '.join(result['learning_objectives'])}")
    if "resources" in result and result["resources"]:
        print(f"Resources: {len(result['resources'])} items")

    print("=" * 40)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_handson_quest_python_beginner():
    """
    初心者向けPython演習生成テスト
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "gemini":
        if not settings.GEMINI_API_KEY or "REPLACE" in settings.GEMINI_API_KEY:
            pytest.skip("GEMINI_API_KEY not set")

    document_content = """
# Python入門

Pythonはシンプルで読みやすいプログラミング言語です。

## 変数
```python
name = "太郎"
age = 25
```

## 関数
```python
def greet(name):
    return f"こんにちは、{name}さん!"
```
"""

    result = await generate_handson_quest(
        document_content=document_content, user_rank=1, user_skills=""
    )

    assert isinstance(result, dict)
    assert "title" in result
    assert "difficulty" in result
    assert "steps" in result

    print("\n=== Beginner Python Quest ===")
    print(f"Title: {result['title']}")
    print(f"Difficulty: {result['difficulty']}")
    print(f"Steps: {len(result['steps'])}")
    if "estimated_time_minutes" in result:
        print(f"Estimated Time: {result['estimated_time_minutes']} minutes")

    # 各ステップの詳細内容を表示
    print("\n--- Steps Detail ---")
    for i, step in enumerate(result["steps"], 1):
        print(f"\n【Step {i}】 {step.get('title', 'N/A')}")
        print(f"  説明: {step.get('description', 'N/A')}")
        if step.get("code_example"):
            print(f"  コード例:\n{step.get('code_example')}")
        if step.get("checkpoints"):
            print(f"  チェックポイント: {', '.join(step.get('checkpoints', []))}")

    # 学習目標とリソース
    if "learning_objectives" in result and result["learning_objectives"]:
        print("\n学習目標:")
        for obj in result["learning_objectives"]:
            print(f"  - {obj}")

    if "resources" in result and result["resources"]:
        print("\nリソース:")
        for res in result["resources"]:
            if isinstance(res, str):
                print(f"  - {res}")
            elif isinstance(res, dict):
                print(f"  - {res.get('title', 'N/A')}: {res.get('url', 'N/A')}")

    print("=" * 40)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_handson_quest_advanced_fastapi():
    """
    上級者向けFastAPI演習生成テスト
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "gemini":
        if not settings.GEMINI_API_KEY or "REPLACE" in settings.GEMINI_API_KEY:
            pytest.skip("GEMINI_API_KEY not set")

    document_content = """
# FastAPI Advanced Patterns

## Dependency Injection
FastAPIの依存性注入システムは強力で柔軟です。

## Background Tasks
バックグラウンドタスクで非同期処理を実装できます。

## WebSocket Support
リアルタイム通信をWebSocketで実現します。
"""

    result = await generate_handson_quest(
        document_content=document_content,
        user_rank=8,
        user_skills="Python, FastAPI, PostgreSQL, Docker",
    )

    assert isinstance(result, dict)
    assert "title" in result
    assert "difficulty" in result
    assert "steps" in result

    print("\n=== Advanced FastAPI Quest ===")
    print(f"Title: {result['title']}")
    print(f"Difficulty: {result['difficulty']}")
    print(f"Steps: {len(result['steps'])}")
    if "estimated_time_minutes" in result:
        print(f"Estimated Time: {result['estimated_time_minutes']} minutes")

    # 各ステップの詳細内容を表示
    print("\n--- Steps Detail ---")
    for i, step in enumerate(result["steps"], 1):
        print(f"\n【Step {i}】 {step.get('title', 'N/A')}")
        print(f"  説明: {step.get('description', 'N/A')[:150]}...")
        if step.get("checkpoints"):
            print(f"  チェックポイント: {', '.join(step.get('checkpoints', []))}")

    print("=" * 40)
