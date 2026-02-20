# Architecture Decision Records (ADR)

## 📜 概要

このディレクトリには、プロジェクトにおける**重要な技術的意思決定の記録（ADR）**を保管します。
「なぜこの技術を選んだのか」「どの代替案を検討したのか」を残すことで、将来のメンバーが文脈を理解し、同じ議論を繰り返さずに済むようにします。

## 📝 ADR作成のタイミング

以下のような決定を行う際に、ADRを作成してください：

- [ ] **アーキテクチャレベルの選択** (例: モノリス vs マイクロサービス、同期 vs 非同期)
- [ ] **主要ライブラリ・フレームワークの採用** (例: SQLAlchemy vs Raw SQL、LangChain 0.3 vs 0.2)
- [ ] **セキュリティ方針** (例: 認証方式、脆弱性スキャン戦略)
- [ ] **CI/CD戦略** (例: Grype→Trivy移行)
- [ ] **パフォーマンスとトレードオフ** (例: キャッシュ戦略、N+1問題の解決方法)

❌ **作成不要**: コーディング標準（変数名、関数名）、軽微なバグ修正

## 🚀 作成方法

### Step 1: 次のADR番号を確認

```bash
ls -1 .github/decisions/*.md | sort -V | tail -1
# 例: 001-ci-strategy.md → 次は 002
```

### Step 2: テンプレートからコピー

**軽量版（推奨）**: ハッカソンやMVP開発向け

```bash
cp .github/decisions/TEMPLATE-lightweight.md .github/decisions/002-your-decision.md
```

**詳細版**: 大規模プロジェクトや詳細な記録が必要な場合

```bash
# 既存の 001-ci-strategy.md を参考にフルフォーマットで作成
```

### Step 3: 内容を記入

- **タイトル**: 決定内容が一目で分かるように（例: `SQLAlchemyをORMとして採用`）
- **コンテキスト**: なぜこの決定が必要になったか
- **決定**: 何を採用するか
- **代替案**: 検討した他の選択肢と却下理由
- **結果**: この決定の影響（良い面・悪い面）

### Step 4: PRに含める

ADRは単独でPRを作らず、**実装PRに一緒に含める**ことを推奨。
実装とその背景が同時にレビューされることで、意思決定の妥当性が検証されます。

## 📂 ファイル命名規則

```
{3桁の連番}-{短い説明}.md
```

**例**:

- `001-ci-strategy.md`
- `002-sqlalchemy-orm.md`
- `003-langchain-version.md`

## 🔄 ADRのステータス

ADRは以下のステータスを持ちます：

- **提案中**: まだ決定していない、議論中の状態
- **決定**: 採用され、実装に進む
- **棄却**: 検討したが採用しない
- **非推奨**: 過去に採用したが、別の方法に置き換えられた（新しいADRへのリンクを記載）

## 📖 既存のADR

| ID    | タイトル                                           | ステータス | 日付       |
| ----- | -------------------------------------------------- | ---------- | ---------- |
| 001   | [CI Strategy & Tool Selection](001-ci-strategy.md) | 決定       | 2026-02-17 |
| 002   | [DB接続基盤とORM選定](002-database-orm-selection.md) | 決定       | 2026-02-19 |
| 003   | [CRUD実装パターン](003-crud-pattern.md) | 決定       | 2026-02-19 |
| 004   | [AI基盤とLLM統合戦略](004-ai-infrastructure-langchain.md) | 決定       | 2026-02-19 |
| 005-a | [APEXスタイルランク分布の採用](005-apex-legends-rank-distribution.md) | 決定       | 2026-02-19 |
| 005-b | [OAuth トークン暗号化戦略（Fernet + スレッドセーフ）](005-oauth-token-encryption.md) | 決定       | 2026-02-19 |
| 006   | [管理用API認証設計（API Key）](006-admin-api-authentication.md) | 決定       | 2026-02-19 |
| 007   | [SkillTree初期化タイミング（ユーザー作成時 vs 遅延初期化）](007-skilltree-initialization-timing.md) | 決定       | 2026-02-19 |
| 008   | [Alembicマイグレーション粒度](008-alembic-migration-granularity.md) | 決定       | 2026-02-19 |
| 009   | [DB設計方針（正規化・型選択・外部キー戦略）](009-database-design-strategy.md) | 決定       | 2026-02-19 |
| 010-a | [User API設計 - rankフィールドの管理方針](010-user-api-rank-management.md) | 決定       | 2026-02-19 |
| 010-b | [スキルツリーAPI実装後のテスト戦略 - モック vs 統合テスト](010-skill-tree-test-strategy-after-ai-migration.md) | 決定       | 2026-02-20 |
| 011   | [User API エンドポイント設計](011-user-api-endpoint-design.md) | 決定（ADR 015 により /users/me 移行）| 2026-02-20 |
| 013   | [Quest API エンドポイント設計](013-quest-api-endpoint-design.md) | 決定       | 2026-02-21 |
| 014   | [認証セッション管理方針（JWT + httpOnly Cookie）](014-auth-session-strategy.md) | 決定（httpOnly Cookie に更新）| 2026-02-21 |
| 015   | [/users/me エンドポイント移行方針](015-users-me-endpoint-migration.md) | 決定       | 2026-02-21 |

## 🎯 ADRの目的

1. **意思決定の透明性**: チーム全員が「なぜ」を共有できる
2. **知識の保存**: メンバーが入れ替わっても文脈が失われない
3. **議論の効率化**: 同じ議論を繰り返さずに済む
4. **失敗からの学習**: 過去の決定を振り返り、改善できる

## 📚 参考資料

- [adr.github.io](https://adr.github.io/) - ADRのコンセプトと事例
- [Documenting Architecture Decisions (Michael Nygard)](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
