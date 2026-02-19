# ADR 004: AI基盤とLLM統合戦略

## ステータス

- [x] **決定**

## コンテ キスト (課題と背景)

PR #32 でAI機能（ランク判定、スキルツリー生成、演習生成）の基盤を構築する際、以下の要件がありました:

- OpenAIとAnthropicの両方を使用可能にしたい（コスト・性能比較のため）
- プロンプトエンジニアリングを容易にしたい（試行錯誤が頻繁）
- 同期/非同期の両方に対応したい（FastAPIの非同期エンドポイント対応）
- テスト時にLLM呼び出しをモック化したい
- 将来的にRAG（Retrieval-Augmented Generation）を追加する可能性

## 決定 (Decision)

**LangChain + ChatModel抽象化**を採用する:

### 1. LLMプロバイダー抽象化

```python
# app/core/llm.py
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel

def get_llm(model: str | None = None, temperature: float = 0.7) -> BaseChatModel:
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "openai":
        return ChatOpenAI(model=model or settings.OPENAI_MODEL, ...)
    elif provider == "anthropic":
        return ChatAnthropic(model=model or settings.ANTHROPIC_MODEL, ...)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
```

### 2. プロンプトテンプレート管理

```python
# app/core/prompts.py
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

RANK_ANALYSIS_TEMPLATE = PromptTemplate(
    input_variables=["github_data", "portfolio_data", "external_data"],
    template="""..."""
)
```

### 3. 同期/非同期呼び出し

```python
async def invoke_llm(prompt: str) -> str:
    llm = get_llm()
    response = await llm.ainvoke(prompt)
    return str(response.content)

def invoke_llm_sync(prompt: str) -> str:
    llm = get_llm()
    response = llm.invoke(prompt)
    return str(response.content)
```

## 代替案との比較 (Options)

### 1. OpenAI SDK直接利用

```python
import openai
response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)
```

- **Good**: 
  - シンプルで軽量
  - 公式SDKなので最新機能がすぐに使える
- **Bad**: 
  - Anthropic切り替えに大規模リファクタリングが必要
  - プロンプトテンプレート管理が煩雑
  - RAG等の高度な機能を自前実装する必要がある
  - **却下理由**: マルチプロバイダー対応と将来の拡張性が犠牲になる

### 2. LiteLLM (統一インターフェース)

```python
import litellm
response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)
```

- **Good**: 
  - OpenAI/Anthropic/Gemini等の統一API
  - プロンプトテンプレートなしでシンプル
- **Bad**: 
  - LangChainのエコシステム（RAG, Agents等）が使えない
  - プロンプトエンジニアリングツールが弱い
  - **却下理由**: 将来的なRAG対応や複雑なChain構築が困難

### 3. Haystack (AI Framework)

- **Good**: 
  - RAG特化（ドキュメント検索に強い）
  - パイプライン構築が得意
- **Bad**: 
  - LangChainより学習コストが高い
  - FastAPIとの統合例が少ない
  - **却下理由**: ハッカソンの時間制約で学習コストが高すぎる

### 4. 各プロバイダーSDKを環境変数で分岐

```python
if settings.LLM_PROVIDER == "openai":
    import openai
    response = openai.ChatCompletion.create(...)
elif settings.LLM_PROVIDER == "anthropic":
    import anthropic
    response = anthropic.messages.create(...)
```

- **Good**: 
  - 依存が少ない、公式SDKのみ
  - プロバイダー固有機能に簡単にアクセス可能
- **Bad**: 
  - 分岐処理が各所に散在し、保守性が低下
  - プロンプトテンプレート管理が各自実装になる
  - テストでモック化が困難
  - **却下理由**: コードの保守性とテスタビリティが犠牲になる

## 結果 (Consequences)

### Positive

- **マルチプロバイダー対応**: 環境変数1つでOpenAI⇄Anthropic切り替え可能
- **プロンプト管理**: `prompts.py` で一元管理、バージョン管理が容易
- **テスタビリティ**: `get_llm()` をモック化すれば、実際のAPI呼び出しなしでテスト可能
- **エコシステム**: LangChainのRAG, Agents, Memory等を将来追加しやすい
- **非同期対応**: FastAPIの非同期エンドポイントで効率的に実行可能

### Negative

- **依存関係の増加**: LangChain本体 + 各プロバイダーパッケージ（`langchain-openai`, `langchain-anthropic`）
  - **対処法**: 必要なパッケージのみインストール（`langchain-core` のみで開発可能）
- **LangChainバージョン管理**: 頻繁にBreaking Changesが発生する
  - **対処法**: `pyproject.toml` でバージョン固定（`langchain = "^0.3.0"`）
  - **CVE対応**: 定期的に脆弱性スキャン（Trivy）+ Dependabot
- **学習コスト**: LangChainの概念（Chain, Runnable, LCEL等）を理解する必要がある
  - **対処法**: MVP段階では `invoke()` / `ainvoke()` のみ使用し、複雑な機能は後回し
- **パフォーマンス**: 薄いラッパー層だが、公式SDKより若干のオーバーヘッドがある
  - **影響**: ネットワークレイテンシ（数百ms〜数秒）に比べて無視できるレベル

### 実装ガイドライン

- **プロンプトテンプレート**: 全て `app/core/prompts.py` に集約
- **API呼び出し**: エンドポイントでは `invoke_llm()` / `invoke_llm_sync()` を使用
- **エラーハンドリング**: LLM呼び出しは必ず try-except でラップ（タイムアウト、レート制限対策）
- **テスト戦略**:
  - 単体テスト: `get_llm()` をモック化
  - 統合テスト: 実際のAPI呼び出し（CI/CD外、手動実行）
- **コスト管理**: 
  - 開発環境では `gpt-4o-mini` (安価)
  - 本番環境では `claude-3-5-sonnet-20241022` (高性能)

### 脆弱性対応履歴

- **CVE-2025-68664, CVE-2025-65106**: `langchain-core ^0.3.81` で対応（PR #32）
- **CVE-2025-62727**: `starlette ^0.49.1` で対応（PR #32）

### Future Enhancements

- **RAG対応**: ドキュメント検索からの演習生成
- **Streaming**: リアルタイムレスポンス表示
- **Agent実装**: 複数ステップの自動実行
- **Memory**: ユーザーとの会話履歴管理
