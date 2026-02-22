# ADR-0001: Sentryをエラー追跡ツールとして選定

## ステータス

提案中（Proposed）

## コンテキスト

### 背景

学生ハッカソンのプロジェクトにおいて、以下の課題が発生：

1. **エラー検知の遅延**: ユーザーからの報告があるまでエラーに気づかない
2. **デバッグ情報の不足**: Render標準ログだけでは再現条件が不明
3. **予算制約**: 学生予算では月$50以上の監視ツールは導入不可
4. **運用負荷**: 3人チームで自前の監視基盤を構築・運用する余裕がない

### 要件

- ✅ Python例外の自動キャプチャ
- ✅ スタックトレース・リクエストコンテキストの保存
- ✅ メール通知（緊急度：高エラー）
- ✅ 無料枠で運用可能（学生予算: $0-10/月）
- ✅ 実装コスト: 1-2時間以内
- ✅ 学習コスト: 低（公式ドキュメントが充実）

### 検討候補

#### 1. Sentry

- **無料枠**: 5,000イベント/月
- **統合方法**: Python SDK（`pip install sentry-sdk`）
- **実装コスト**: 10行のコード追加
- **学習コスト**: 低（FastAPI公式ドキュメントに記載）
- **コミュニティ**: 大規模（GitHub 36k+ stars）
- **有料化後**: Developer Plan $26/月（エラーが増えたら検討）

#### 2. Rollbar

- **無料枠**: 5,000イベント/月
- **統合方法**: Python SDK
- **実装コスト**: Sentryとほぼ同等
- **学習コスト**: 中（ドキュメントがSentryより少ない）
- **コミュニティ**: 中規模
- **有料化後**: Essentials Plan $49/月（Sentryより高い）

#### 3. BugSnag

- **無料枠**: 7,500イベント/月（最も多い）
- **統合方法**: Python SDK
- **実装コスト**: Sentryとほぼ同等
- **学習コスト**: 中
- **コミュニティ**: 小規模
- **有料化後**: Standard Plan $59/月（最も高い）

#### 4. 自前実装（ログ集約 + アラート）

- **コスト**: $0
- **実装コスト**: 2-3日（チーム3人 × 2-3日 = 6-9人日）
- **運用コスト**: 高（バグ修正、メンテナンス）
- **機能**: Sentryより劣る（スタックトレース解析、コンテキスト保存が弱い）
- **結論**: **学生ハッカソンでは過剰投資**

## 決定

**Sentryを採用する**（ただしオプション扱い）

### 理由

#### 1. 無料枠の充実度（★★★★★）

- 5,000イベント/月は学生ハッカソン（ユーザー10-50人）には十分
- 実際のエラー発生: 推定100-500イベント/月（余裕あり）
- Rollbar/BugSnagと同等以上

#### 2. 学習コストの低さ（★★★★★）

- FastAPI公式ドキュメントに統合例あり
  - https://fastapi.tiangolo.com/deployment/concepts/#monitoring
- コミュニティ記事が豊富（Qiita、Stack Overflow）
- 実装時間: 30分-1時間

#### 3. 実装の簡潔さ（★★★★★）

```python
# 10行で完了
import sentry_sdk

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,  # 10%のみ追跡でコスト削減
        environment="production",
    )
```

#### 4. コミュニティの規模（★★★★★）

- GitHub: 36,000+ stars
- 大手企業での採用実績多数
- セキュリティ的にも信頼性が高い

#### 5. 有料化後のコスト（★★★★☆）

- Developer Plan: $26/月（Rollbar $49、BugSnag $59より安い）
- 卒業後も継続運用可能な価格帯

#### 6. 技術スタック適合性（★★★★★）

- Python/FastAPI公式サポート
- Next.js（JavaScript）も同じSentryプロジェクトで管理可能
- フロントエンド・バックエンド統合監視が実現

### オプション扱いとする理由

1. **必須ではない**:
   - UptimeRobot（死活監視）とRenderログ（基本ログ）で最低限カバー可能
   - Sentryはエラー追跡の「強化版」
2. **設定の手間**:
   - Sentry登録（5分）+ DSN設定（5分）= 10分必要
   - 5分タスク（OpenAI上限設定、UptimeRobot）の後に検討でOK
3. **poetry add sentry-sdk**:
   - 依存追加が必要（pyproject.toml更新）
   - デプロイ時間が若干増加

## 実装方針

### Phase 1（現在）: 統合準備のみ

```python
# backend/app/main.py
if settings.SENTRY_DSN:
    sentry_sdk.init(...)  # DSNが設定されている場合のみ有効化
```

**状態**:

- コードは実装済み
- SENTRY_DSN環境変数は未設定
- Sentryは無効（影響ゼロ）

### Phase 2（オプション）: 実際の統合

```bash
# 1. Sentry登録・DSN取得
# 2. 依存追加
cd backend
poetry add sentry-sdk

# 3. 環境変数設定（Render Dashboard）
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# 4. 再デプロイ（自動）
git push origin main
```

**判断タイミング**:

- デモ発表前: 不要（余計なエラー通知が来ると混乱）
- ハッカソン審査通過後: 検討（継続運用する場合のみ）
- 3ヶ月後: 再評価（ユーザー数・エラー頻度を見て判断）

## トレードオフ

### Sentryを採用するメリット

- ✅ エラー発生時の詳細なコンテキスト（ユーザーID、リクエストパラメータ等）
- ✅ スタックトレースの自動解析
- ✅ 同じエラーの集約（Grouping）→ ノイズ削減
- ✅ エラーの優先度・頻度の可視化
- ✅ フロントエンド（Next.js）とバックエンド（FastAPI）を統合管理

### Sentryを採用するデメリット

- ❌ 外部サービス依存（Sentry障害時は通知されない）
- ❌ センシティブ情報の流出リスク（パスワード、トークン等）
  - **対策**: `before_send`フックでフィルタリング実装必要
- ❌ 無料枠超過時の対応（5,000イベント/月以上）
  - **対策**: `sample_rate=0.1`（10%のみ追跡）で10倍に拡張

### 自前実装と比較したトレードオフ

| 項目       | Sentry                                     | 自前実装                     |
| ---------- | ------------------------------------------ | ---------------------------- |
| 実装時間   | 30分-1時間                                 | 2-3日                        |
| 運用コスト | 低（外部サービス任せ）                     | 高（バグ修正、メンテナンス） |
| 機能       | 高（スタックトレース、コンテキスト、集約） | 低（単純なログ集約のみ）     |
| 学習コスト | 低（公式ドキュメント充実）                 | 中（自前設計の理解が必要）   |
| 金銭コスト | $0-26/月                                   | $0                           |
| **結論**   | ✅ 学生ハッカソンに最適                    | ❌ オーバーエンジニアリング  |

## セキュリティ考慮事項

### センシティブ情報の除外

```python
def before_send(event, hint):
    """Sentryに送信する前にセンシティブ情報を除外"""
    # パスワード、トークン、APIキーを削除
    if 'request' in event:
        if 'data' in event['request']:
            sensitive_keys = ['password', 'token', 'api_key', 'secret']
            for key in sensitive_keys:
                if key in event['request']['data']:
                    event['request']['data'][key] = '[Filtered]'
    return event

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    before_send=before_send,  # フィルター適用
)
```

**実装時期**: Phase 2（実際の統合時）に追加

### データの保持期間

- Sentry無料枠: 30日間保持
- 30日経過後は自動削除（GDPR準拠）

## 代替案の再評価条件

### Sentryを **やめる** 条件

1. **無料枠超過が頻繁**: 月5,000イベント超過が3ヶ月連続
   - **対策**: `sample_rate`を0.1 → 0.05に下げる
   - **代替**: Rollbar（無料枠同等）に乗り換え検討
2. **センシティブ情報の流出**: `before_send`でも防げない漏洩
   - **代替**: 自前ログ集約に切り替え
3. **Sentry障害が多発**: 月1回以上のダウンタイム
   - **代替**: Rollbar + 自前ログ集約の併用

### Sentryを **強化する** 条件

1. **有料化が必要**: 無料枠超過が常態化
   - **判断**: ユーザー数100人以上、月間売上$100以上で検討
2. **フロントエンド統合**: Next.jsのエラーも追跡したい
   - **実装**: `@sentry/nextjs`パッケージ追加

## 参考資料

### 公式ドキュメント

- [Sentry FastAPI Integration](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [Sentry Pricing](https://sentry.io/pricing/)
- [FastAPI Monitoring Best Practices](https://fastapi.tiangolo.com/deployment/concepts/#monitoring)

### 比較記事

- [Sentry vs Rollbar vs BugSnag (2025)](https://stackshare.io/sentry-vs-rollbar-vs-bugsnag)
- [Error Tracking Tools for Startups](https://dev.to/...)

### 学生向けリソース

- [GitHub Education Pack](https://education.github.com/pack) - Sentry Business Plan 6ヶ月無料
  - **注意**: 要学生認証（.ac.jpメールアドレス）

## 決定日

2026年2月22日

## 決定者

- チーム開発者（実装担当）
- レビュワー（セキュリティ・アーキテクチャ責任者）

## レビュー予定日

- **Phase 1完了後**: 2026年2月末（コード統合のみ、実運用なし）
- **Phase 2判断**: 2026年3月末（デモ発表後、継続運用するか決定）
- **3ヶ月後再評価**: 2026年5月末（無料枠超過・コスト・効果を検証）

## 関連ADR

- なし（初回のADR）

## 今後のADR候補

- ADR-0002: レート制限の実装方針（OpenAIコスト削減）
- ADR-0003: PostgreSQL → Supabase移行の判断基準
- ADR-0004: フロントエンド監視（Sentry Next.js統合）
