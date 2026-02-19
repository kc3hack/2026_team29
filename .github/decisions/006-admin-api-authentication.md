# ADR 006: 管理用API認証設計（API Key vs DB based認証）

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

issue #31でランク不整合修正API（`POST /admin/fix-user-ranks`）を実装する際、以下の課題がありました:

- **セキュリティ**: 管理APIは誰でも実行できてはならない（ランク改ざんのリスク）
- **認証テーブル未定義**: issue #31には管理者テーブル（Admin, Role等）の仕様が含まれていない
- **ハッカソン期間と優先度**: 4人チーム全員が管理者であり、複雑な権限管理は不要
- **責務分離**: 通常API（`/api/v1`）と管理API（`/admin`）は認証方式が異なる
- **Swagger UI公開範囲**: 管理APIの仕様を外部に露出すべきか

## 決定 (Decision)

**API Key認証（環境変数 `ADMIN_API_KEY`）+ 独立FastAPI app**を採用する:

```python
# app/api/admin.py
from fastapi import FastAPI, Header, HTTPException

admin_app = FastAPI(
    title="Team29 Admin API",
    docs_url=None,
    redoc_url=None,
)

def verify_admin_key(x_admin_key: str = Header(...)) -> None:
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")

@admin_app.get("/docs", include_in_schema=False)
async def admin_docs(request: Request, _: None = Depends(verify_admin_key)):
    return get_swagger_ui_html(openapi_url="/admin/openapi.json", ...)

@admin_app.post("/fix-user-ranks")
def fix_user_ranks(db: Session = Depends(get_db), _: None = Depends(verify_admin_key)):
    ...
```

```python
# app/main.py
from app.api.admin import admin_app

app.mount("/admin", admin_app)
```

### 実装原則

- **認証方式**: `X-Admin-Key` ヘッダーで環境変数 `ADMIN_API_KEY` と照合
- **FastAPI sub-application**: 管理APIを独立したFastAPIインスタンスとして分離
- **Swagger UI認証**: `/admin/docs` も `X-Admin-Key` 認証が必要（通常の `/docs` とは別）
- **責務分離**: `/api/v1`（通常API）と `/admin`（管理API）を明確に分離

## 代替案との比較 (Options)

### 1. DBテーブルで管理者を管理（Admin, Role, Permission等）

- **Good**:
  - 複数管理者のアカウント管理が可能（追加・削除・権限変更）
  - 監査ログ（誰がいつ実行したか）を記録できる
  - Role-Based Access Control（RBAC）で細かい権限管理
- **Bad**:
  - Admin, Role, Permissionテーブルの設計・実装が必要（issue #31のスコープ外）
  - ハッカソン期間中にDB設計・マイグレーション・CRUD実装する時間がない
  - 4人チーム全員が管理者であり、複雑な権限管理は不要
  - アプリの本質的な機能（ゲーミフィケーション）ではない
  - **却下理由**: ハッカソンでは優先度が低い、オーバーエンジニアリング

### 2. JWT認証（通常APIと同じ認証方式）

- **Good**:
  - 通常APIと認証方式を統一できる
  - ユーザー単位で管理API実行権限を付与可能
- **Bad**:
  - Userテーブルに `is_admin` フラグを追加する必要がある
  - 管理APIと通常APIの責務が混在する（認証ロジックが複雑化）
  - ハッカソン期間中はユーザー登録すら未実装
  - **却下理由**: 通常APIと管理APIは責務が異なる、混在させるべきではない

### 3. 認証なし（内部ネットワークのみで実行）

- **Good**: 実装が最速、テストが簡単
- **Bad**:
  - 本番環境で外部公開する場合、ランク改ざんのリスク
  - SwaggerUIで誰でも管理APIを実行できる
  - セキュリティの基本原則違反
  - **却下理由**: 最低限の認証は必須

### 4. 通常APIと同じFastAPIインスタンスで管理APIを実装

```python
# app/api/api.py
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
```

- **Good**: 実装がシンプル、1つのSwagger UIで全API確認可能
- **Bad**:
  - 通常APIと管理APIの責務が混在する
  - Swagger UI（`/docs`）で管理APIの仕様が外部に露出する
  - 認証方式が異なるAPIを1つのインスタンスにまとめるのは設計が不適切
  - **却下理由**: 単なる責務分離の問題にとどまらず、セキュリティリスクの増大や1つのインスタンスにしてしまうと柔軟な制御が効かない

## 結果 (Consequences)

### Positive

- **実装速度**: 環境変数1つで認証が完結、DBテーブル・マイグレーション不要
- **責務分離**: `/api/v1`（通常API）と `/admin`（管理API）が明確に分離
- **Swagger UI分離**: `/docs`（通常API）と `/admin/docs`（管理API）が独立、管理APIの仕様が外部に露出しない
- **十分なセキュリティ**: 十分に長いランダムキー（64文字以上推奨）であれば、ブルートフォース攻撃は非現実的

### Negative

- **単一キー**: 管理者全員が同じキーを共有（個別アカウント管理不可）
  - **対処法**: Phase 2以降でAdmin/Roleテーブルを追加
- **監査ログなし**: 誰がいつ管理APIを実行したか記録できない
  - **対処法**: 将来的にAdmin DBテーブル + 実行ログテーブルを追加
- **キーローテーション**: 環境変数変更時、全管理者に新キーを配布する必要がある
  - **対処法**: ハッカソン期間中は固定キーで運用、本番環境では秘密管理ツール推奨
- **ブルートフォース対策なし**: レートリミット未実装
  - **対処法**: Phase 2以降でFastAPI Limiterを導入

### 実装ガイドライン

- **開発環境**: `.env` で `ADMIN_API_KEY=test` （簡易設定）
- **本番環境**: 64文字以上のランダムキーを設定（例: `openssl rand -base64 48`）
- **責務分離**: 管理APIは `/admin` 配下に配置、通常APIと混在させない
- **Phase 2方針**: ユーザー認証実装後、Admin/Roleテーブルを追加してRBAC対応
