"""Grades スキーマ - 成績・統計情報"""

from pydantic import BaseModel


class HighestRank(BaseModel):
    """最高ランク情報"""

    rank: int  # 0-9
    category: str  # 'web' | 'ai' | 'security' | 'infrastructure' | 'game' | 'design'
    category_name: str  # 表示用名称（例: "Web/App"）
    rank_name: str  # ランク名（例: "林", "森", "世界樹"）
    color: str  # 背景色（例: "#55aaff"）


class GradeStats(BaseModel):
    """成績統計情報"""

    consecutive_days: int  # 連続記録日数
    completed_quests: int  # 修了したクエスト数
    highest_rank: HighestRank  # 最高ランク情報
