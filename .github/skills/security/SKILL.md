---
name: security
description: Security Standard, Vulnerability Prevention (SQLi, XSS, CSRF), IPA Guidelines
---

# Security First Guidelines

セキュリティに関わる実装（認証、DB操作、外部入力の処理など）を行う際は、以下の基準を遵守してください。

## 1. Vulnerability Prevention

- **基本方針**: SQLインジェクション、XSS、CSRF等の基本的な脆弱性が混入しないよう、常に検証済みのライブラリやフレームワーク標準の関数を使用してください。
- **独自実装の禁止**: 暗号化ロジックやサニタイズ処理を独自に実装せず、信頼できるライブラリを使用してください。

## 2. Security Standard (IPA)

日本のIPA（情報処理推進機構）が発行する**『安全なウェブサイトの作り方』**のセキュリティ要件に準拠します。
実装時は以下のチェックリスト観点を考慮してください（URLの内容を知識として参照すること）。

- 参考：IPA「安全なウェブサイトの作り方」PDF（https://www.ipa.go.jp/security/vuln/websecurity/ug65p900000196e2-att/000017316.pdf ）。リンク切れの場合は、IPA公式サイト上で「安全なウェブサイトの作り方」を検索して参照してください。

## 3. 具体的な実装チェック

- **SQL操作**: ORMまたはプレースホルダを使用しているか？（文字列結合の禁止）
- **HTML出力**: React/Next.jsの標準エスケープを利用しているか？（`dangerouslySetInnerHTML` の使用禁止、または正当な理由の説明）
- **認証**: パスワードはハッシュ化されているか？ セッション管理はセキュアか？
