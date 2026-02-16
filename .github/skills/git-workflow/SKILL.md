---
name: git-workflow
description: Git Commit Guidelines (Conventional Commits), Pull Request Templates, Atomic PRs
---

# Git & Commit Guidelines

コードの変更理由を明確にするため、以下のルールに従ってコミットメッセージやPRを作成してください。

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

## 3. Pull Request (PR) Rules

- **Template Compliance**: PR作成時は必ずリポジトリの `PULL_REQUEST_TEMPLATE.md` を使用し、全ての項目（特にセキュリティ自己評価）を埋めてください。
- **Atomic PRs**: 1つのPRには1つの機能・修正のみを含めてください。巨大なPRはレビュー負荷が高まるため拒否します。
- **Self-Review**: PRを作成する前に、あなた自身で生成されたコードを見直し、不要なデバッグ出力やコメントアウトされたコードが残っていないか確認してください。
