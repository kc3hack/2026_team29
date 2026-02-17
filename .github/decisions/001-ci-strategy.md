# ADR 001: CI Strategy & Tool Selection

## Status

Accepted

## Context

プロジェクトの初期段階において、Backend (FastAPI) と Frontend (Next.js) のコード品質とデプロイ可能性を保証するためのCIパイプラインが必要でした。
特に、Python環境におけるリンター/フォーマッターの選定と、Next.jsビルド時の環境変数依存性が課題となっていました。

## Decision

### 1. Backend: Ruff & Pytest

- **Decision**: Pythonのリンター/フォーマッターとして `Ruff` を採用し、テストランナーとして `pytest` を採用する。
- **Reason**:
  - `Ruff` は Rust製で極めて高速であり、従来の `Flake8`, `Black`, `isort` などの機能を単体でカバーできるため、CI時間を短縮し設定を簡素化できる。
  - `pytest` はPythonエコシステムのデファクトスタンダードであり、将来的な拡張性が高い。

### 2. Frontend: npm ci & Mock Env

- **Decision**: 依存関係インストールに `npm ci` を使用し、ビルド時にダミーの環境変数を注入する。
- **Reason**:
  - `npm ci` は `package-lock.json` に厳密に基づいたインストールを行うため、CI環境での再現性が保証される。
  - Next.jsのビルドプロセス（Static Generation等）でAPI URLなどの環境変数が参照される可能性があるため、CI上ではダミー値を設定してビルドエラーを防ぐ戦略をとる。

### 3. Workflow Separation

- **Decision**: `backend.yml` と `frontend.yml` にワークフローを分離し、`paths` フィルタを設定する。
- **Reason**:
  - モノレポ構成において、関連しない変更（例：Frontendのみの修正）でBackendのCIが走ることを防ぎ、リソース消費とフィードバック時間を最適化するため。

### 4. Dependency Version Pinning (Supply Chain Security)

- **Decision**: Python依存関係を `*` (any version) から具体的なバージョン範囲 (例: `^0.115.0`) に固定する。
- **Reason**:
  - `*` 指定では、PyPIから常に最新版が取得されるため、パッケージが乗っ取られた場合（supply-chain attack）、悪意あるコードがCI環境や本番環境で実行されるリスクがある。
  - バージョン範囲を固定することで、依存関係の更新を意図的・管理的に行い、セキュリティリスクを低減する。

### 5. GitHub Actions Version Pinning

- **Decision**: `trufflesecurity/trufflehog@main` をタグバージョン（例: `@v3.82.13`）に固定する。
- **Reason**:
  - `@main` ブランチ参照は上流の変更によってCI動作が予期せず変わる可能性があり、サプライチェーンリスクが高い。
  - タグやコミットSHAに固定することで、CI実行内容の不変性と再現性を担保する。

### 6. Test Exit Code Handling

- **Decision**: `pytest || echo ...` の代わりに、exit code 5（テスト未検出）のみを許容し、実際のテスト失敗は検知する。
- **Reason**:
  - `|| echo` は全てのエラーを握りつぶしてしまい、テストが実際に失敗してもCIが成功扱いになる。
  - exit code を判定することで、「テストがまだない状態」と「テストが失敗した状態」を正確に区別できる。

### 7. Event-Specific Git References in Security Scan

- **Decision**: `github.head_ref` / `github.event.repository.default_branch` の代わりに、イベント種別に応じた適切なSHA参照を使用する。
- **Reason**:
  - `github.head_ref` は push イベントでは空文字になるため、差分スキャンが成立しない。
  - PR時は `github.event.pull_request.{base,head}.sha`、push時は `github.event.before` / `github.sha` を使用することで、正確な差分スキャンを実現する。

### 8. Lightweight Security Strategy (3-Layer Approach)

- **Decision**: 重量級スキャン（Syft+Grype）を週次実行に変更し、PR時は軽量ツールを使用する。
- **Reason**:
  - Syft+Grypeは3〜5分かかり、PR体験を損なう。
  - ビルトインツール（pip-audit / npm audit）は数秒で完了。
  - Dependabotが常時監視し、自動PR作成。
- **3層構造**:
  1. **Dependabot（常時）**: GitHub標準機能、CI負荷ゼロ、自動PR作成
  2. **pip-audit / npm audit（PR時）**: 秒単位、PRをブロックしない（continue-on-error）
  3. **Syft+Grype（週次）**: 詳細スキャン、結果をIssue化して追跡

### 9. Vulnerability Exception Management

- **Decision**: `.grype.yaml` でCritical脆弱性の除外設定を許可する。
- **Reason**:
  - すべての脆弱性が実際のリスクとなるわけではない（未使用機能、誤検知等）。
  - 修正が存在しない場合や、他の制御で緩和されている場合の対応が必要。
  - 除外には文書化された正当な理由（notes）を必須とし、四半期ごとにレビューする運用を前提とする。

## Consequences

- Backend開発者はローカルでも `ruff` を使用してコード規約を遵守する必要がある。
- FrontendビルドがCIで成功しても、実行時エラー（環境変数設定ミスなど）は検知できないため、別途E2Eテストなどの検討が必要になる可能性がある。
- 依存関係のバージョンを固定したため、定期的なアップデート戦略（Dependabotなど）が必要になる。
- TruffleHogなどのツールバージョンを固定したため、新機能や修正を取り込むには手動更新が必要。
- **PR CI時間が大幅短縮**: 重量級スキャンを週次に移行したことで、PRのCI時間が5分短縮される。
- **Dependabotが常時監視**: GitHub標準機能により、CI負荷なしで脆弱性を検出し自動PR作成。
- **週次スキャンは追跡**: Grypeの結果はIssueとして記録され、チームで対応を追跡できる。
- `.grype.yaml` での除外管理には厳格な運用ルール（文書化、定期レビュー）が必須。
