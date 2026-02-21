"""ストリーミング用プロンプトテンプレート

JSON Lines形式でノード単位にストリーミング生成させる
"""

SKILL_TREE_STREAMING_TEMPLATE = """スキルツリー: {category} | ランク{rank}({rank_name})
GitHub:{github_username} | スタック:{tech_stack}
習得済み:{acquired_skills}

参考:{baseline_json}

## CRITICAL: スキルツリー構造の制約（必ず守ること）

**【基礎層】prerequisites:[] のノードは正確に2個または3個**
- 絶対にこれより多く作成してはいけません
- カテゴリの最も基礎的な2-3個のみ
- 例: Web → HTML/CSS + HTTP の2個
- 例: AI → Python + 数学 の2個
- 例: Security → ネットワーク + OS + 暗号化 の3個

**【中級層】prerequisites:[1個] のノードは5-7個**
- 基礎スキル1つに依存するスキル
- 各基礎ノードから2-3個ずつ派生

**【応用層】prerequisites:[1-2個] のノードは8-10個**
- 中級スキルを組み合わせた高度なスキル
- 最も数が多い層

## 生成手順:
1. まず基礎ノード2個を出力 (prerequisites:[])
2. 次に中級ノード5-7個を出力 (prerequisites:基礎のいずれか1個)
3. 最後に応用ノード8-10個を出力 (prerequisites:中級1-2個)

## 出力ルール:
1. 合計15-20ノード (基礎2-3 + 中級5-7 + 応用8-10)
2. completed:trueは習得済みのみ
3. **出力順序**: 基礎(prerequisites:[]) → 中級(prerequisites:1個) → 応用(prerequisites:2個以上)
4. JSON Lines形式: 1行1ノード、```jsonは不要

## 例(8ノード):
{{"type":"node","id":"html","name":"HTML/CSS","completed":true,"description":"基礎","prerequisites":[],"estimated_hours":20}}
{{"type":"node","id":"http","name":"HTTP","completed":false,"description":"プロトコル","prerequisites":[],"estimated_hours":15}}
{{"type":"node","id":"js","name":"JavaScript","completed":false,"description":"中級","prerequisites":["html"],"estimated_hours":25}}
{{"type":"node","id":"css-fw","name":"CSSフレームワーク","completed":false,"description":"中級","prerequisites":["html"],"estimated_hours":20}}
{{"type":"node","id":"api","name":"REST API","completed":false,"description":"中級","prerequisites":["http"],"estimated_hours":25}}
{{"type":"node","id":"ts","name":"TypeScript","completed":false,"description":"応用","prerequisites":["js"],"estimated_hours":30}}
{{"type":"node","id":"react","name":"React","completed":false,"description":"応用","prerequisites":["js","ts"],"estimated_hours":40}}
{{"type":"node","id":"next","name":"Next.js","completed":false,"description":"応用","prerequisites":["react"],"estimated_hours":35}}
{{"type":"edge","from":"html","to":"js"}}
{{"type":"edge","from":"html","to":"css-fw"}}
{{"type":"edge","from":"http","to":"api"}}
{{"type":"edge","from":"js","to":"ts"}}
{{"type":"edge","from":"js","to":"react"}}
{{"type":"edge","from":"ts","to":"react"}}
{{"type":"edge","from":"react","to":"next"}}
{{"type":"metadata","total_nodes":8,"completed_nodes":1,"progress_percentage":12.5,"next_recommended":["js","css-fw","api"]}}

**確認: 必ず以下の構成で出力すること**
- 基礎(prerequisites:[]): 2-3個のみ
- 中級(prerequisites:[1個]): 5-7個
- 応用(prerequisites:[1-2個]): 8-10個
合計15-20ノード

説明や```json不要。上記の構成で1行1JSONを出力開始:
"""
