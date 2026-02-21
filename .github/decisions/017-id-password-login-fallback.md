# ADR 017: ID+パスワード認証の追加（GitHub OAuth フォールバック）

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

product-spec §2.1 には「**GitHub OAuth または ID入力でログイン**」と明記されている。

しかし ADR 014（認証セッション管理）では GitHub OAuth のみを実装対象とし、
**ID入力ログインは未実装のまま放置されていた。**

以下の状況でこの欠落が問題になる:

1. **GitHub の Client ID/Secret が未設定の開発環境** → OAuth フロー全体が 503 で動かない。
2. **ハッカソン審査・デモ**: 審査員が GitHub アカウントを使いたくない場面でも動作を確認できる必要がある。
3. **GitHub OAuth 側のバグ/仕様変更**: 万一 OAuth が機能しなくても最低限の認証フローが維持できる。

### 当初 OAuth 実装が ID ログインを含まなかった理由

- 初期実装（Issue #59）では GitHub OAuth を主経路と定め、ID入力は将来対応として先送りした。
- `POST /users` が認証不要の公開エンドポイントとして残っており、
  テスト目的では `POST /users` → `POST /auth/login`（既存ユーザーのみ許可）の
  2ステップで動いていたが、**product-spec のログインフローとは別物**だった。

## 決定 (Decision)

### 1. `POST /auth/login` を「新規登録 + ログイン」の1ステップ upsert に変更

```
POST /auth/login  { "username": "alice", "password": "secret" }

ケース1: username が存在しない → 新規 User 作成 → JWT Cookie 発行 (200)
ケース2: username が存在 + hashed_password あり → PBKDF2-SHA256 検証 → 一致: 200 / 不一致: 401
ケース3: username が存在 + hashed_password なし (GitHub OAuth ユーザー) → 403
         （GitHub OAuthで登録したことをユーザーに示す）
```

`POST /users` は**後方互換・管理者用**として残存するが、通常のユーザー登録経路は使用しない。

### 2. パスワードは PBKDF2-HMAC-SHA256 でハッシュ化して `users.hashed_password` に保存

- Python 標準ライブラリ `hashlib.pbkdf2_hmac` を使用（外部依存なし）。
- iterations = 600,000（OWASP 2024年推奨値）。
- `passlib[bcrypt]` は bcrypt 4.x との互換性問題（`bcrypt.__about__` 削除）があるため不採用。
- PBKDF2-SHA256 は OWASP・NIST 推奨のアルゴリズムであり、独自実装には該当しない。
- GitHub OAuth 経由で作成されたユーザーは `hashed_password = NULL`。
- GitHub OAuth ユーザーへの ID+パスワードログイン試行は **403** を返す
  （アカウント存在の暴露になるが、GitHub ログインへ誘導する UX が優先）。

### 3. Alembic マイグレーション `0003_add_hashed_password`

```sql
ALTER TABLE users ADD COLUMN hashed_password VARCHAR;  -- nullable
```

既存ユーザーは `hashed_password = NULL` のまま継続動作。

## 考慮したリスクと対応

| リスク | 対応 |
|--------|------|
| パスワードなし新規作成が可能だった | `POST /auth/login` の `password` フィールドを必須化 |
| GitHub OAuth ユーザーへのブルートフォース | 403 を返して「GitHub で登録済み」と明示。rate-limit は将来対応 |
| パスワードの平文保存 | `hashlib.pbkdf2_hmac`（PBKDF2-SHA256、iterations=600,000）でハッシュ化。CRUD 層で即時変換 |
| タイミング攻撃 | `verify_password` は `secrets.compare_digest` による定数時間比較を使用 |
| state リプレイ攻撃 | HMAC ベースの state はステートレスのため、10分ウィンドウ内なら同一 state を再利用可能。MVP トレードオフとして許容（本番化時は Redis 等でワンタイム管理へ移行すること） |

## Product-Spec との整合

| product-spec §2.1 | 実装状態 |
|---|---|
| GitHub OAuth でログイン | ✅ ADR 014 実装済み |
| **ID入力でログイン** | ✅ **本 ADR で実装** |

## 代替案との比較 (Options)

### 1. OAuth のみ維持し、ID入力は実装しない

- **Good**: 実装がシンプル。パスワード管理のリスクがない。
- **Bad**: product-spec §2.1 に明記された機能を満たさない。
  デモ・審査環境で OAuth が使えない場合に詰む。**→ 却下**

### 2. JWT をレスポンスボディで返し、フロントが localStorage に保存

- **Bad**: ADR 014 で XSS リスクとして却下済み。Cookie 方式を継続。**→ 却下**

### 3. メールアドレス + パスワード認証

- **Good**: 一般的な認証形式。
- **Bad**: メール確認フロー・パスワードリセット等の追加実装が必要。
  ハッカソン MVP のスコープ外。**→ 却下**（username のみで簡略化）

## 参照

- product-spec §2.1: "GitHub OAuth または ID入力でログイン"
- ADR 014: 認証セッション管理方針（JWT + httpOnly Cookie）
- security SKILL.md §1: 独自暗号化実装の禁止
- `app/core/password.py`: PBKDF2-SHA256 ユーティリティ（`hashlib.pbkdf2_hmac`）
- `app/api/endpoints/auth.py`: `POST /auth/login` 実装
- `alembic/versions/0003_add_hashed_password.py`: DBマイグレーション
