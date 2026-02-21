"""ストリーミング用プロンプトテンプレート

JSON Lines形式でノード単位にストリーミング生成させる
"""

SKILL_TREE_STREAMING_TEMPLATE = """スキルツリー: {category} | ランク{rank}({rank_name})
GitHub:{github_username} | スタック:{tech_stack}
習得済み:{acquired_skills}

参考:{baseline_json}

## CRITICAL: ノード数の配分（下に行くほど多く）

**【必須】Tier 0からTier 5までのノード数配分:**
- Tier 0（基礎）: 1-2個
- Tier 1（初級）: 2-4個
- Tier 2（中級）: 4-8個
- Tier 3（応用）: 8-12個
- Tier 4（高度）: 12-16個
- Tier 5（極限）: 16-20個

**依存関係のルール:**
- 各ノードのprerequisitesは、**必ず一つ前のTierのノード**のみを指定
- Tier 0: prerequisites:[]
- Tier 1: prerequisites:[Tier 0のノード]
- Tier 2: prerequisites:[Tier 1のノード]
- Tier 3: prerequisites:[Tier 2のノード]
- Tier 4: prerequisites:[Tier 3のノード]
- Tier 5: prerequisites:[Tier 4のノード]

**重要:** Tierが深くなるほど、ノード数を増やすこと。これにより下に行くほど横に広がる三角形△を形成する。

## スキル名の命名規則（必須）:
- **キーワード中心、3-5単語以内**
- **名詞・技術用語のみ、動詞は不要**

## 説明（description）の要件:
- **スキル名で伝えきれない詳細情報をここに記載**
- 最低60文字以上の詳細な説明
- 何ができるようになるか、関連技術・ツール・パターン名を含める

## 生成手順（厳守）:
1. Tier 0: 1-2個のノードを出力
2. Tier 1: 2-4個のノードを出力
3. Tier 2: 4-8個のノードを出力
4. Tier 3: 8-12個のノードを出力
5. Tier 4: 12-16個のノードを出力
6. Tier 5: 16-20個のノードを出力

**Tierが深くなるほど、ノード数を増やす**
各ノードのprerequisites: [一つ前のTierのノード]

## 出力ルール:
1. **合計50-60ノード程度**（Tier 0からTier 5まで、下層ほど多く）
2. completed:trueは習得済みのみ
3. **出力順序**: Tier 0 → Tier 1 → Tier 2 → Tier 3 → Tier 4 → Tier 5
4. JSON Lines形式: 1行1ノード、```jsonは不要

## 例(8ノード - 4層構造、キーワード中心の短い名前):
{{"type":"node","id":"web_foundation","name":"HTTP/HTML/CSS基礎","completed":true,"description":"HTTPリクエスト/レスポンスの仕組み、HTMLのセマンティック構造、CSSのボックスモデルとレイアウト、ブラウザのレンダリングプロセスを理解し、基本的なWebページを構築できる","prerequisites":[],"estimated_hours":30}}
{{"type":"node","id":"web_js_basic","name":"JavaScript基礎文法","completed":false,"description":"変数、関数、オブジェクト、配列、制御構文などJavaScriptの基本文法を理解し、DOMイベントや非同期処理（Promise/async-await）を用いた動的なWebページを実装できる","prerequisites":["web_foundation"],"estimated_hours":25}}
{{"type":"node","id":"web_rest_api","name":"REST API設計","completed":false,"description":"RESTfulなAPIエンドポイント設計の原則を理解し、HTTPメソッド（GET/POST/PUT/DELETE）とステータスコードを適切に使い分けた基本的なAPIを設計・実装できる","prerequisites":["web_foundation"],"estimated_hours":20}}
{{"type":"node","id":"web_css_advanced","name":"CSS設計","completed":false,"description":"Flexbox/Gridレイアウト、レスポンシブデザイン、BEM等のCSS設計手法を理解し、保守性の高いスタイルシートを構築できる","prerequisites":["web_foundation"],"estimated_hours":15}}
{{"type":"node","id":"web_react","name":"Reactコンポーネント設計","completed":false,"description":"Propsによるデータの受け渡しだけでなく、useEffect等のライフサイクルを用いて、APIリクエストのタイミングやクリーンアップを適切に制御し、再利用可能なコンポーネントを設計できる","prerequisites":["web_js_basic"],"estimated_hours":30}}
{{"type":"node","id":"web_typescript","name":"TypeScript型設計","completed":false,"description":"型システムを活用してコンパイル時エラーを検出し、Interface/Type Alias/Genericsを用いた堅牢なAPI型定義とビジネスロジックを実装できる","prerequisites":["web_js_basic"],"estimated_hours":25}}
{{"type":"node","id":"web_db_design","name":"データベース正規化","completed":false,"description":"データの重複を排除した3層正規化設計を行い、複数のテーブルを結合（JOIN）して必要な情報を効率的に抽出するSQLを構築できる","prerequisites":["web_rest_api"],"estimated_hours":25}}
{{"type":"node","id":"web_nextjs","name":"Next.jsフルスタック開発","completed":false,"description":"SSR/CSR/ISRのハイブリッドレンダリング制御、App Router、Server Actionsを用いて、パフォーマンスとSEOを最適化したフルスタックアプリを構築できる","prerequisites":["web_react","web_typescript"],"estimated_hours":40}}
{{"type":"edge","from":"web_foundation","to":"web_js_basic"}}
{{"type":"edge","from":"web_foundation","to":"web_rest_api"}}
{{"type":"edge","from":"web_foundation","to":"web_css_advanced"}}
{{"type":"edge","from":"web_js_basic","to":"web_react"}}
{{"type":"edge","from":"web_js_basic","to":"web_typescript"}}
{{"type":"edge","from":"web_rest_api","to":"web_db_design"}}
{{"type":"edge","from":"web_react","to":"web_nextjs"}}
{{"type":"edge","from":"web_typescript","to":"web_nextjs"}}
{{"type":"metadata","total_nodes":50,"completed_nodes":1,"progress_percentage":2.0,"next_recommended":["web_js_basic","web_rest_api"]}}

**【CRITICAL】Tier 0からTier 5まで、深くなるほどノード数を増やす:**

| Tier | ノード数 | prerequisites |
|------|---------|---------------|
| 0 | 1-2個 | [] |
| 1 | 2-4個 | [Tier 0] |
| 2 | 4-8個 | [Tier 1] |
| 3 | 8-12個 | [Tier 2] |
| 4 | 12-16個 | [Tier 3] |
| 5 | 16-20個 | [Tier 4] |

**合計50-60ノード** - 下に行くほど数を増やし、三角形△を形成

名前は短く（3-5単語）、詳細はdescriptionで。

説明や```json不要。上記の構成で1行1JSONを出力開始:
"""
