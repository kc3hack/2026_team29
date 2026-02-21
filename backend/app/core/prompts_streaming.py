"""ストリーミング用プロンプトテンプレート

JSON Lines形式でノード単位にストリーミング生成させる
"""

SKILL_TREE_STREAMING_TEMPLATE = """スキルツリー: {category} | ランク{rank}({rank_name})
GitHub:{github_username} | スタック:{tech_stack}
習得済み:{acquired_skills}

参考:{baseline_json}

要件:
1. 15-20ノード(基礎8-10 + 応用7-10)
2. completed:trueは習得済みのみ
3. prerequisitesを正確に
4. **出力順序(重要)**: 基礎→中級→応用の順で出力
   - 前提スキルがないノード(prerequisites:[])を最初に出力
   - 次に前提スキルが1-2個のノードを出力
   - 最後に前提スキルが3個以上の高度なノードを出力
   - 依存関係を満たす順序で出力すること

## 出力形式: JSON Lines (1行1ノード、難易度順)
**必ず基礎スキル→応用スキルの順で1行1JSONを出力**してください。```json は不要です。

例(正しい順序):
{{"type":"node","id":"html-css","name":"HTML/CSS基礎","completed":true,"description":"Webページの構造とスタイリング","prerequisites":[],"estimated_hours":20}}
{{"type":"node","id":"javascript","name":"JavaScript基礎","completed":false,"description":"Webの動的な動作を実装","prerequisites":["html-css"],"estimated_hours":30}}
{{"type":"node","id":"react","name":"React","completed":false,"description":"UIライブラリ","prerequisites":["html-css","javascript"],"estimated_hours":40}}
{{"type":"edge","from":"html-css","to":"javascript"}}
{{"type":"edge","from":"javascript","to":"react"}}
{{"type":"metadata","total_nodes":15,"completed_nodes":5,"progress_percentage":33.3,"next_recommended":["javascript","typescript","react"]}}

**基礎から順に1行1JSONで出力**。説明不要。出力開始:
"""
