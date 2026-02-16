---
name: coding-standards
description: Error Handling, Logging (JSON), Type Safety (TypeScript/Python), Naming Conventions
---

# Coding Standards

## 1. General Principles

- **No Silent Failures**: エラーを握りつぶさない。必ずハンドリングするか、上位へ伝播させる。
- **Type Safety**:
  - **TypeScript**: `any` 型の使用は原則禁止。必要なら `unknown` を使い型ガードを行う。
  - **Python**: Type Hints (型ヒント) を必須とする。Pydanticモデルを積極的に利用する。

## 2. Backend (Python/FastAPI) Guidelines

### Error Handling & Logging

ログは構造化されたJSON形式で出力すること。

```python
from app.core.logger import logger

try:
    # 処理
    pass
except Exception as e:
    logger.error({
        "event": "skill_generation_failed",
        "error": str(e),
        "user_id": current_user.id,
        "stack_trace": traceback.format_exc()
    })
    raise HTTPException(status_code=500, detail="Internal Server Error")
```

### Dependency Injection

- グローバル変数は避け、FastAPIの `Depends` を使用してServiceやDBセッションを注入すること。

## 3. Frontend (Next.js/TypeScript) Guidelines

### Component Design

- **Container/Presentational Pattern**: データ取得ロジック（Server ComponentsまたはCustom Hooks）と、表示用コンポーネントを分離する。
- **Server Components**: 可能な限りServer Components (`app/`配下) でデータフェッチを行い、Client ComponentsにPropsで渡す。

### Error Boundary

- 予期せぬクラッシュを防ぐため、主要な機能ブロックごとに React Error Boundary を設置すること。

## 4. Naming Conventions

- **Variables/Functions**:
  - TS: `camelCase` (例: `fetchUserData`)
  - Python: `snake_case` (例: `fetch_user_data`)
- **Files**:
  - TS Components: `PascalCase.tsx` (例: `SkillCard.tsx`)
  - TS Utils: `camelCase.ts` or `kebab-case.ts`
  - Python Modules: `snake_case.py`
