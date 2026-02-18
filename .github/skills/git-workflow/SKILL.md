---
name: git-workflow
description: Git Commit Guidelines (Conventional Commits), Pull Request Templates, Atomic PRs, Evidence Requirements
---

# Git & Commit Guidelines

コードの変更理由を明確にし、レビューコストを下げるため、以下のルールに従ってコミットメッセージやPRを作成してください。

## 1. Conventional Commits

コミットメッセージのプレフィックスには以下を適切に使用してください。

- `feat:`: 新機能
- `fix:`: バグ修正
- `docs:`: ドキュメントのみの変更
- `refactor:`: リファクタリング（機能追加やバグ修正を含まない）
- `test:`: テストの追加・修正
- `chore:`: ビルドプロセスやツールの変更

## 2. Commit Body (Explain "Why")

変更理由はコード内のコメントではなく、**コミットメッセージの本文（Body）**に記述してください。
「何をしたか」だけでなく**「なぜその変更が必要だったか」「なぜその実装を選択したか」**を記述してください。

### 良い例

```text
fix: ユーザー登録時のバリデーションロジックを修正

正規表現の不備により、特定のメールアドレス形式でReDoS脆弱性の懸念があったため、
バリデーションライブラリ `validator.js` の標準関数に置き換えを実施。
自作正規表現よりも保守性とセキュリティが担保されるため。
```

## 3. Branch Naming Convention

**必須ルール**: すべてのブランチ名にIssue番号を含めること

### Feature branches（新機能）
```
feature/issue-{issue_number}-{short-description}
```
**例**:
- `feature/issue-36-rank-ai`
- `feature/issue-32-ai-setup`
- `feature/issue-27-db-setup`

### Bugfix branches（バグ修正）
```
fix/issue-{issue_number}-{short-description}
```
**例**:
- `fix/issue-42-login-error`

### Hotfix branches（緊急修正）
```
hotfix/{short-description}
```
**例**:
- `hotfix/security-patch`
- `hotfix/production-crash`

**注**: Issueが存在しない緊急修正のみ、Issue番号なしで可

### 命名ガイドライン
- `{short-description}`: 3-4単語以内、ケバブケース（kebab-case）
- 英語推奨、日本語の場合はローマ字
- ブランチ名だけで内容が推測できること

### 禁止パターン
- ❌ `feature/new-feature`（Issue番号なし）
- ❌ `my-branch`（個人名）
- ❌ `test`（抽象的）
- ❌ `feature/issue-36`（説明なし）

## 4. Pull Request (PR) Rules

- **Evidence of Functionality (Must)**: 機能追加やバグ修正を行った場合は、**動作を保証する客観的な証拠**を必ずPRに添付してください。証拠がないPRはレビューしません（Closeします）。
  - **UI等の視覚的な変更**: 変更前後のスクリーンショット、または操作動画（GIF/MP4）。
  - **API/ロジックの変更**: テストスイートがPassしたログ、またはcURL等の実行コマンドとそのレスポンス結果。
- **Template Compliance**: PR作成時は必ずリポジトリの `PULL_REQUEST_TEMPLATE.md` を使用し、全ての項目（特に以下の2つ）を埋めてください。
  - **🔧 技術的な意思決定とトレードオフ（最重要）**: 採用したアプローチとそのメリット/デメリット、却下した代替案とその理由を明記。
  - **🧪 テスト戦略と範囲**: 追加したテストケース（正常系・異常系）と、**意図的にテストしていないこと**を明記。
- **Trade-off Visibility (Must)**: すべてのPRは「採用したアプローチのデメリット」と「却下した代替案」を明記してください。これにより、レビュワーは文脈を理解し、より建設的なフィードバックが可能になります。
- **Test Gap Declaration (Must)**: テストケースを追加する際は、「何をテストしたか」だけでなく、「**何をテストしていないか**」も明記してください。これにより、将来のリスクが可視化されます。
  - 例: 「外部APIのレート制限」「同時接続数1000件」「ブラウザ互換性（IE11）」
- **Atomic PRs**: 1つのPRには1つの機能・修正のみを含めてください。巨大なPRはレビュー負荷が高まるため拒否します。
- **Self-Review**: PRを作成する前に、あなた自身で生成されたコードを見直し、不要なデバッグ出力やコメントアウトされたコードが残っていないか確認してください。

## 4. Architecture Decision Record (ADR)

重要な技術的意思決定（ライブラリ選定、アーキテクチャ方針、セキュリティ戦略等）を行う際は、ADRを作成してください。

- **目的**: 「なぜこの技術を選んだのか」を記録し、将来のメンバーが文脈を理解できるようにする。
- **場所**: `.github/decisions/` ディレクトリ
- **テンプレート**: `.github/decisions/TEMPLATE-lightweight.md` を使用（ハッカソン向け軽量版）
- **含める内容**:
  - コンテキスト（なぜこの決定が必要か）
  - 決定内容（何を採用するか）
  - 代替案との比較（なぜ他の選択肢を却下したか）
  - 結果（この決定の影響：メリット/デメリット）
- **PRへの含め方**: ADRは単独でPRを作らず、実装PRに一緒に含めることを推奨。

詳細は [.github/decisions/README.md](../../decisions/README.md) を参照してください。
