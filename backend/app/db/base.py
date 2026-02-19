from app.db.base_class import Base
from app.models.badge import Badge
from app.models.oauth_account import OAuthAccount
from app.models.profile import Profile
from app.models.quest import Quest
from app.models.quest_progress import QuestProgress
from app.models.skill_tree import SkillTree
from app.models.user import User

__all__ = [
    "Base",
    "Badge",
    "OAuthAccount",
    "Profile",
    "Quest",
    "QuestProgress",
    "SkillTree",
    "User",
]
