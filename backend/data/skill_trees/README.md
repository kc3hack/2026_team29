# スキルツリーデータ格納ディレクトリ

このディレクトリには、各カテゴリのスキルツリー構造をJSONで定義します。

## Phase 2（現在）: モック実装

`backend/app/services/mock_ai_service.py` 内のPython辞書で固定データを返却。

## Phase 3（予定）: AI実装への移行

このディレクトリのJSONファイルを：

1. **ベースラインデータ**として使用
2. LLMがユーザーの学習履歴に基づいてカスタマイズ
3. `completed`フラグをGitHub/Qiita分析で動的に設定

## ファイル命名規則

- `web.json` - Web開発スキルツリー
- `ai.json` - AI/機械学習スキルツリー
- `security.json` - セキュリティスキルツリー
- `infrastructure.json` - インフラ/DevOpsスキルツリー
- `design.json` - UI/UXデザインスキルツリー
- `game.json` - ゲーム開発スキルツリー

## JSON構造（スキーマ）

```json
{
  "nodes": [
    {
      "id": "unique-skill-id",
      "name": "スキル名",
      "completed": false,
      "description": "スキルの説明",
      "prerequisites": ["前提スキルID"],
      "estimated_hours": 30
    }
  ],
  "edges": [
    {
      "from": "prerequisite-skill-id",
      "to": "dependent-skill-id"
    }
  ],
  "metadata": {
    "total_nodes": 10,
    "completed_nodes": 0,
    "progress_percentage": 0.0,
    "next_recommended": ["skill-id-1", "skill-id-2"]
  }
}
```

## 使用方法（Phase 3実装時）

```python
import json
from pathlib import Path

def load_skill_tree_template(category: str) -> dict:
    file_path = Path(__file__).parent.parent.parent / "data" / "skill_trees" / f"{category}.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
```
