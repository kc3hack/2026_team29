# ADR 005: OAuth トークン暗号化戦略（Fernet対称暗号 + スレッドセーフ対応）

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

issue #31でOAuthAccountテーブル（GitHubトークン等）を実装する際、以下の課題がありました:

- **セキュリティ基準**: IPAセキュア・プログラミング講座では、OAuth トークンの平文保存は禁止されている
- **本番環境リスク**: DBが漏洩した場合、平文トークンで外部サービス（GitHub等）に不正アクセスされるリスク
- **実装速度 vs 安全性**: ハッカソン期間中に独自暗号化実装は危険（脆弱性を生むリスク）
- **スレッドセーフ**: FastAPI (uvicorn) はマルチスレッドで動作し、複数リクエストが同時に暗号化・復号を行う

## 決定 (Decision)

**Fernet対称暗号（cryptographyライブラリ）+ スレッドセーフ対応**を採用する:

```python
# app/core/encryption.py
import threading
from cryptography.fernet import Fernet

_fernet: Fernet | None = None
_fernet_lock = threading.Lock()

def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        with _fernet_lock:
            if _fernet is None:  # Double-checked locking
                key = settings.ENCRYPTION_KEY
                if not key:
                    raise ValueError("ENCRYPTION_KEY is not set.")
                _fernet = Fernet(key.encode())
    return _fernet
```

### 実装原則

- **暗号化キー管理**: 環境変数 `ENCRYPTION_KEY` で管理（`.env` で設定、リポジトリに含めない）
- **スレッドセーフ**: `threading.Lock` + double-checked lockingパターンでFernetインスタンスを保護
- **本番環境検証**: `ENV=production` の場合のみ、起動時に `ENCRYPTION_KEY` の存在を検証

## 代替案との比較 (Options)

### 1. AES-256直接実装（独自実装）

- **Good**: 学習になる、カスタマイズ自由度が高い
- **Bad**:
  - 暗号化実装は専門知識が必要で、脆弱性を生むリスクが高い
  - ハッカソン期間中に実装・テストする時間がない
  - IPA基準でも「独自実装を避ける」ことが推奨されている
  - **却下理由**: 時間がかかり、安全性の担保ができない

### 2. AWS KMS（クラウド秘密管理サービス）

- **Good**: 暗号化キーのローテーション自動化、監査ログ、高セキュリティ
- **Bad**:
  - AWSアカウント・IAM設定が必要（チーム全体への影響が大きい）
  - ローカル開発環境でのセットアップが煩雑
  - ハッカソン期間中にインフラ構築する余裕がない
  - **却下理由**: 他システムへの影響が大きい、オーバーエンジニアリング

### 3. HashiCorp Vault（秘密管理ツール）

- **Good**: オンプレミスでも使える、多様な認証方法、秘密のバージョニング
- **Bad**:
  - Vault サーバーのセットアップ・運用が必要
  - チーム全体がVaultの使い方を学ぶ必要がある
  - ハッカソンのスコープを超える
  - **却下理由**: インフラ構築・学習コストが高すぎる

### 4. bcrypt / Argon2（パスワードハッシュ系）

- **Good**: パスワード保存のベストプラクティス
- **Bad**:
  - ハッシュは一方向関数のため、復号ができない
  - OAuth トークンは復号して外部API呼び出しに使う必要がある
  - **却下理由**: 用途が異なる（ハッシュ vs 暗号化）

### 5. スレッドセーフ対応なし（シングルトンFernetインスタンス）

- **Good**: 実装がシンプル
- **Bad**:
  - uvicornはマルチスレッドで動作し、複数リクエストが同時にFernetインスタンスを初期化する可能性
  - 競合状態（race condition）により、暗号化・復号が失敗するリスク
  - **却下理由**: 複数リクエストを捌くAPIとして致命的

## 結果 (Consequences)

### Positive

- **セキュリティ**: DB漏洩時もトークンが暗号化されているため、二次被害を防止
- **IPA基準準拠**: 独自実装を避け、業界標準ライブラリ（cryptography）を使用
- **実装速度**: Fernetは知名度が高く、採用例・資料が豊富で実装が早い
- **スレッドセーフ**: double-checked lockingにより、複数リクエスト同時実行でも安全

### Negative

- **暗号化キー管理の責任**: `ENCRYPTION_KEY` の漏洩防止は開発者の責任
  - **対処法**: `.env.example` にテンプレート記載、本番環境では秘密管理ツール（AWS Secrets Manager等）推奨
- **暗号化/復号のオーバーヘッド**: 数ms程度の遅延が発生
  - **対処法**: OAuth トークン取得は初回のみ、以降はキャッシュ（将来的にRedis等で対応）
- **キーローテーション未対応**: 暗号化キーを変更すると、既存の暗号化トークンが復号不可
  - **対処法**: Phase 2以降で対応（KMSやVault導入時に検討）

### 実装ガイドライン

- **開発環境**: conftest.py でダミーキー（`TEST_ENCRYPTION_KEY`）を設定
- **本番環境**: `ENV=production` の場合のみ、main.py で `validate_encryption_key()` を実行
- **スレッドセーフ**: グローバル変数初期化時は必ず `threading.Lock` で保護
