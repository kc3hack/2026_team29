"""ストリーミング用プロンプトテンプレート

JSON Lines形式でノード単位にストリーミング生成させる
"""

SKILL_TREE_STREAMING_TEMPLATE = """スキルツリー: {category} | ランク{rank}({rank_name})
GitHub:{github_username} | スタック:{tech_stack}
習得済み:{acquired_skills}

参考:{baseline_json}

## CRITICAL: ノード数の配分（下に行くほど多く）

**【必須】Tier 0からTier 5までのノード数配分（厳格に遵守）:**
- Tier 0（基礎）: 1-2個 ← 最上層、最小
- Tier 1（初級）: 2-4個
- Tier 2（中級）: 4-8個
- Tier 3（応用）: 8-12個
- Tier 4（高度）: 12-16個
- Tier 5（極限）: 16-20個 ← 最下層、最大

**三角形△構造の形成:**
上に行くほど狭く、下に行くほど広い逆三角形を形成。
各Tierで**指定範囲内でできるだけ多くのノード**を生成すること。

**依存関係のルール:**
- 各ノードのprerequisitesは、**必ず一つ前のTierのノード**のみを指定
- Tier 0: prerequisites:[]
- Tier 1: prerequisites:[Tier 0のノード]
- Tier 2: prerequisites:[Tier 1のノード]
- Tier 3: prerequisites:[Tier 2のノード]
- Tier 4: prerequisites:[Tier 3のノード]
- Tier 5: prerequisites:[Tier 4のノード]

**重要:** Tierが深くなるほど、ノード数を増やすこと。これにより下に行くほど横に広がる三角形△を形成する。

**【絶対厳守】 9, 10...などの階層は絶対に生成しないでください。**

## スキル名の命名規則（必須）:
- **キーワード中心、3-5単語以内**
- **名詞・技術用語のみ、動詞は不要**

## 説明（desc）の要件:
- **スキル名で伝えきれない詳細情報を簡潔に記載**
- 30文字以内の簡潔な説明
- 何ができるようになるかのポイントのみ

## 生成手順（厳守）:
1. Tier 0: 1-2個のノードを出力（少なく）
2. Tier 1: 2-4個のノードを出力
3. Tier 2: 4-8個のノードを出力（範囲内でできるだけ多く）
4. Tier 3: 8-12個のノードを出力（範囲内でできるだけ多く）
5. Tier 4: 12-16個のノードを出力（範囲内でできるだけ多く）
6. Tier 5: 16-20個のノードを出力（最も多く）

**CRITICAL: 下層（Tier 3-5）ほど、指定範囲の上限に近い数を生成**
各ノードのprerequisites: [一つ前のTierのノード]

## 出力ルール:
1. **合計50-60ノード程度**（Tier 0からTier 5まで、下層ほど多く）
2. completed:trueは習得済みのみ
3. **出力順序**: Tier 0 → Tier 1 → Tier 2 → Tier 3 → Tier 4 → Tier 5 （ここで終了）
4. JSON Lines形式: 1行1ノード、```jsonは不要
5. **【重要】Tier 6以上の階層は絶対に生成しないでください。Tier 5で必ず停止してください。**

## 例(3ノード - フォーマット参考のみ):
{{"type":"node","id":"web_foundation","name":"HTTP/HTML/CSS基礎","completed":true,"desc":"HTTPとHTMLの仕組み理解","prerequisites":[],"hours":30}}
{{"type":"node","id":"web_js_basic","name":"JavaScript基礎","completed":false,"desc":"変数・関数・非同期処理の実装","prerequisites":["web_foundation"],"hours":25}}
{{"type":"node","id":"web_react","name":"React設計","completed":false,"desc":"Component設計とHooks活用","prerequisites":["web_js_basic"],"hours":30}}
{{"type":"edge","from":"web_foundation","to":"web_js_basic"}}
{{"type":"edge","from":"web_js_basic","to":"web_react"}}
{{"type":"metadata","total_nodes":50,"completed_nodes":1,"progress_percentage":2.0,"next_recommended":["web_js_basic"]}}

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

**【絶対禁止】Tier 6, 7, 8, 9, 10...などの階層を生成することは絶対に禁止です。Tier 5が最終階層です。**

名前は短く（3-5単語）、詳細はdescで（30文字以内）。

説明や```json不要。上記の構成で1行1JSONを出力開始:
"""
