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

### 1. `POST /auth/register` + `POST /auth/login` に責務を分離（初版から変更）

**初版の決定（upsert 方式）から変更。**
詳細は「変更履歴」セクションを参照。

```
POST /auth/register  { "username": "alice", "password": "secret" }
  → 新規登録専用。username 既存なら 409 Conflict。

POST /auth/login  { "username": "alice", "password": "secret" }
  → 認証専用。
  ケース1: username が存在しない → 401
  ケース2: username が存在 + hashed_password あり → PBKDF2-SHA256 検証 → 一致: 200 / 不一致: 401
  ケース3: username が存在 + hashed_password なし (GitHub OAuth ユーザー) → 401
           （403 にするとユーザー名の存在が確定してしまうため 401 に統一: User Enumeration 防止）
```

`POST /users` は**削除（責務重複のため Issue #59 にて廃止）**。
管理者用ユーザー操作は別 Issue で Admin API として再実装予定。

### 2. パスワードは PBKDF2-HMAC-SHA256 でハッシュ化して `users.hashed_password` に保存

- Python 標準ライブラリ `hashlib.pbkdf2_hmac` を使用（外部依存なし）。
- iterations = 600,000（OWASP 2024年推奨値）。
- `passlib[bcrypt]` は bcrypt 4.x との互換性問題（`bcrypt.__about__` 削除）があるため不採用。
- PBKDF2-SHA256 は OWASP・NIST 推奨のアルゴリズムであり、独自実装には該当しない。
- GitHub OAuth 経由で作成されたユーザーは `hashed_password = NULL`。
- GitHub OAuth ユーザーへの ID+パスワードログイン試行は **401** を返す
  （403 は「その username は存在する」ことを確定させるため、User Enumeration 防止のため 401 に統一）。

### 3. パスワードポリシー（MVP 方針）

- **最小長チェック: なし**（MVP 優先のため。UX を阻害しないことを重視）
  - 本番化前に要検討（OWASP 推奨は 8文字以上）
- **最大長チェック: 128文字**（PBKDF2 の DoS 耐性確保のため必須）
- **空文字チェック: あり**（実装済み）
- 複雑度要件（大文字・数字・記号の強制）: **なし**（OWASP 2021 は複雑度強制を非推奨）

> ⚠️ MVP トレードオフ: 最小長未設定のため短いパスワードが許容される。本番サービス化時には最小長（8文字以上）を追加すること（別 Issue 管理予定）。

### 3. Alembic マイグレーション `0003_add_hashed_password`

```sql
ALTER TABLE users ADD COLUMN hashed_password VARCHAR;  -- nullable
```

既存ユーザーは `hashed_password = NULL` のまま継続動作。

## 考慮したリスクと対応

| リスク | 対応 |
|--------|------|
| パスワードなし新規作成が可能だった | `POST /auth/register` の `password` フィールドを必須化 |
| GitHub OAuth ユーザーへのブルートフォース | 401 に統一（User Enumeration 防止）。rate-limit は将来対応 |
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
- ADR 016: GitHub OAuth 認証テスト戦略
- security SKILL.md §1: 独自暗号化実装の禁止
- `app/core/password.py`: PBKDF2-SHA256 ユーティリティ（`hashlib.pbkdf2_hmac`）

## 変更履歴

- 2026-02-21: 初版決定（`POST /auth/login` への upsert 方式、GitHub OAuth ユーザーは 403）
- 2026-02-21: **変更**—レビューにて以下を改定（Issue #59）
  - `POST /auth/login` を登録・認証の両責務から「認証専用」に切り出し、`POST /auth/register` を新設
  - GitHub OAuth ユーザーへの ID+パスワードログイン試行を **403 → 401** に変更
    - 理由: 403 は「その username が GitHub 登録済みで存在する」ことを漏洩し、User Enumeration 攻撃の糸口になるため、401 に統一して情報開示を最小化する
    - UX トレードオフ: 「GitHub から入ってください」のヒントは返せなくなるが、フロントエンド側の UI 誘導（GitHub ログインボタンの定常表示等）で補完する
  - パスワード最小長チェックを **削除**（MVP 優先。短いパスワードを許容し UX を優先。本番化前に要追加）
  - パスワード最大長 **128文字** チェックを**追加**（PBKDF2 DoS 対策）
- `app/api/endpoints/auth.py`: `POST /auth/login` 実装
- `alembic/versions/0003_add_hashed_password.py`: DBマイグレーション
