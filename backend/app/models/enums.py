"""共通Enum定義（product-spec / issue #31 準拠）"""

import enum


class BadgeCategory(str, enum.Enum):
    """バッジカテゴリ（spec 5. バッジシステム）"""

    COMMIT = "commit"
    DAYS = "days"
    BUILDER = "builder"
    WRITER = "writer"
    SEEKER = "seeker"
    GITHUB = "github"  # GitHub連携バッジ


class SkillCategory(str, enum.Enum):
    """スキルツリーカテゴリ（spec 6.1 ロードマップ生成）"""

    WEB = "web"
    AI = "ai"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"
    DESIGN = "design"
    GAME = "game"


class QuestCategory(str, enum.Enum):
    """クエストカテゴリ（SkillCategoryと同じ6種）"""

    WEB = "web"
    AI = "ai"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"
    DESIGN = "design"
    GAME = "game"


class QuestStatus(str, enum.Enum):
    """クエスト進捗ステータス"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
