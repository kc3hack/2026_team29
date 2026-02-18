````skill
---
name: product-spec
description: Application Specification (User Flow, Rank System, Badge System, Skill Tree)
---

# アプリケーション仕様書

## 1. 概要

ユーザーの外部サービス活動実績とポートフォリオを元に、現在のエンジニアとしての立ち位置（ランク）を判定し、RPG風の成長要素（スキルツリー・バッジ）と、そこから導き出される「パーソナライズされた演習生成」を提供する。

## 2. 画面遷移と主要機能 (UX Flow)

### 2.1. ログイン / オンボーディング

1. **Login**: GitHub OAuth または ID入力でログイン。
2. **Profile Setup**:
   - 連携情報の入力 (Qiita ID, Connpass ID)。
   - ポートフォリオ/経歴の入力 (URL または テキスト)。
   - AIによる初回分析実行。

### 2.2. メイン画面 (Dashboard)

- **Status**: 現在のランク（画像表示）、次のランクまでの目安。
- **Skill Tree**: 現在の習得状況と、次に目指すべきノードの可視化。
- **Badges**: 獲得したバッジの一覧表示。

### 2.3. 演習選択 (Quest Hub)

- **Document Generation (優先度: 高)**:
  - ユーザーが学びたい技術のドキュメントやテキストを入力。
  - AIが内容を解析し、ランクに見合ったハンズオン演習を自動生成する。
- **Normal Quest (優先度: 低)**:
  - 事前に用意された標準的な演習シナリオ（MVPでは実装しないか、最小限）。

### 2.4. 演習実行 (Quest Play)

- 生成されたハンズオンの手順表示。
- クリア後の振り返り、経験値獲得。

## 3. 外部連携・入力ソース

### 3.1. GitHub (必須)

- **取得方法**: OAuth 2.0 連携
- **利用データ**:
  - リポジトリの言語構成、コミット頻度、Star数
  - READMEの内容（プロジェクトの質）
  - 寄与活動 (Contribution Graph)

### 3.2. その他サービス・ポートフォリオ

- **Qiita / Connpass**: ユーザーIDまたはURL入力。
- **ポートフォリオ/経歴**: テキスト入力 または URL入力。
- **利用方針**: GitHub情報と合わせてAIへの入力プロンプトに含める。

## 4. ランク判定ロジック (AI主導)

### 4.1. 判定基準

- **相対評価**: 取得した情報を総合的に分析し、「エンジニア全体の上位何％に位置するか」をAIが推定する。
- **ランク分け**: 推定されたパーセンタイルを元に、以下の10段階（植物の成長）にマッピングする。
  1. 種子 (初心者/未経験)
  2. 苗木
  3. 若木
  4. 巨木
  5. 母樹
  6. 林
  7. 森
  8. 霊樹
  9. 古樹
  10. 世界樹 (Top Tier)

### 4.2. ランクアップ

- **MVP段階**: 初回分析時のランク決定のみ実装。
- **Future**: ポイント制や特定条件達成によるランクアップ機能。

## 5. バッジシステム (Gamification)

ユーザーの特定の活動実績に基づき、プロフィールに飾れるバッジを付与する。

| バッジカテゴリ | 取得条件の目安 (AIまたはルールベース判定) |
| :--- | :--- |
| **Commit** | GitHubの総コミット数、またはContributionの濃さ |
| **Days** | 継続学習日数、またはアプリ利用継続日数 |
| **Builder** | 作成したアプリの数 (リポジトリ数やポートフォリオ記述から判定) |
| **Writer** | 技術記事の執筆数 (Qiita/Zenn等の投稿数) |
| **Seeker** | 本アプリ内での演習（クエスト）完了数・進捗率 |

## 6. スキルツリー生成ロジック

### 6.1. ロードマップ生成

- ユーザーの現状（ランク）から、次のランクへ進むための「通過点（マイルストーン）」をAIが生成する。
- 生成カテゴリ:
  - Web/モバイルアプリ
  - AI
  - セキュリティ
  - ネットワーク/インフラ
  - デザイン
  - ゲーム

### 6.2. スキル習得判定

- 生成された通過点に対し、現状の実績で「既に満たしているか」をAIが判定し、初期状態でクリア済み（チェック付き）にする。
- **MVP制限**: その後の活動による自動追従は実装せず、手動更新または再分析とする。

## 7. 開発方針

### Phase 1 (MVP)

- **GitHub OAuth実装**: ユーザー認証とリポジトリ情報取得
- **ドキュメントからの演習生成**: 通常演習は後回し、ドキュメント入力→AI生成を優先
- **一連のフロー構築**: プロフィール入力→AI分析→ランク・ツリー表示
- **動くことを優先**: 判定精度よりも「最初から最後まで動く体験」を重視

### Future Enhancements

- 通常演習（Normal Quest）の拡充
- リアルタイムランクアップ機能
- 自動スキルツリー更新
- コミュニティ機能（ランキング、他ユーザーとの比較）

## 8. データモデル

### 8.1. User (既存)

```python
- id: int
- username: str
- level: int (ランクに対応)
- exp: int (経験値)
- rank: int (0-9: 種子〜世界樹)
- skills: JSON (習得済みスキルのリスト)
- created_at: datetime
- updated_at: datetime
```

### 8.2. 追加予定モデル

#### Profile (外部連携情報)

```python
- user_id: FK
- github_username: str
- qiita_id: str (optional)
- connpass_id: str (optional)
- portfolio_text: text (optional)
- portfolio_url: str (optional)
- last_analyzed_at: datetime
```

#### Badge

```python
- id: int
- user_id: FK
- category: enum (Commit/Days/Builder/Writer/Seeker)
- tier: int (1-3: Bronze/Silver/Gold)
- earned_at: datetime
```

#### Quest

```python
- id: int
- title: str
- description: text
- difficulty: int (対象ランク)
- category: str (Web/AI/Security/etc)
- is_generated: bool (AI生成 or プリセット)
- created_at: datetime
```

#### QuestProgress

```python
- id: int
- user_id: FK
- quest_id: FK
- status: enum (NotStarted/InProgress/Completed)
- started_at: datetime
- completed_at: datetime
```

## 9. 技術スタック

### Backend
- FastAPI
- SQLAlchemy (ORM)
- Alembic (Migration)
- LangChain (LLM連携)
- OpenAI API / Anthropic API

### Frontend
- Next.js (App Router)
- TypeScript
- TailwindCSS
- shadcn/ui

### Infrastructure
- Docker / Docker Compose
- PostgreSQL (Production)
- SQLite (Development)

## 10. セキュリティ要件

- GitHub OAuth 2.0による安全な認証
- APIキーは環境変数で管理（`.env`）
- CORS設定の適切な管理
- SQLインジェクション対策（SQLAlchemy ORM使用）
- XSS対策（Next.jsの自動エスケープ）
- CSRF対策（FastAPIのCORSミドルウェア）

## 11. パフォーマンス要件

- AI分析: 初回30秒以内
- 演習生成: 15秒以内
- 通常APIレスポンス: 200ms以内
- フロントエンド初期表示: 2秒以内

## 12. テスト方針

- **Backend**: pytest + pytest-cov (カバレッジ80%以上)
- **Frontend**: Jest + React Testing Library
- **E2E**: Playwright (主要フロー)
- **LLM**: モック化 + 実際のAPI呼び出しテスト

## 13. デプロイ戦略

- **CI/CD**: GitHub Actions
- **環境**: Development / Staging / Production
- **モニタリング**: ログ集約、エラートラッキング
- **バックアップ**: DBの定期バックアップ

---

## 参考資料

- Architecture SKILL: `.github/skills/architecture/SKILL.md`
- Security SKILL: `.github/skills/security/SKILL.md`
- Git Workflow SKILL: `.github/skills/git-workflow/SKILL.md`

````
