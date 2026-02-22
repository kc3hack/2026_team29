"""Badge サービス（バッジ付与ロジック）"""

from sqlalchemy.orm import Session

from app.crud import badge as crud_badge
from app.crud import quest_progress as crud_quest_progress
from app.models.enums import BadgeCategory, QuestStatus
from app.models.badge import Badge
from app.schemas.badge import BadgeCreate


def award_github_badge(db: Session, user_id: int) -> Badge | None:
    """GitHub OAuth認証成功時にGitHub連携バッジを付与する。
    
    Returns:
        Badge | None: 新たに付与されたバッジ、または既に持っている場合は None
    """
    # 既存のGitHubバッジを確認
    existing_badges = crud_badge.get_badges_by_user(db, user_id)
    github_badges = [
        b for b in existing_badges if b.category == BadgeCategory.GITHUB.value
    ]
    
    # 既にGitHubバッジを持っている場合はスキップ
    if github_badges:
        return None
    
    # 新しいバッジを付与
    try:
        badge_in = BadgeCreate(
            user_id=user_id,
            category=BadgeCategory.GITHUB,
            tier=1,
        )
        return crud_badge.award_badge(db, badge_in)
    except ValueError:
        # 既に存在する場合はスキップ
        return None


def award_builder_badge_if_eligible(db: Session, user_id: int) -> Badge | None:
    """ユーザーのクエスト完了数に基づいてBUILDERバッジを付与する。
    
    バッジティア：
    - tier 1: 1個完了
    - tier 2: 5個完了
    - tier 3: 10個完了
    - tier 4: 20個完了
    - tier 5: 50個完了
    
    Returns:
        Badge | None: 新たに付与されたバッジ、または既に持っている場合は None
    """
    # ユーザーの完了クエスト数を取得
    all_progress = crud_quest_progress.get_quest_progress_by_user(db, user_id)
    completed_count = sum(
        1 for p in all_progress if p.status == QuestStatus.COMPLETED.value
    )
    
    # 完了数に基づくティア判定
    tier_thresholds = [
        (50, 5),
        (20, 4),
        (10, 3),
        (5, 2),
        (1, 1),
    ]
    
    target_tier = None
    for threshold, tier in tier_thresholds:
        if completed_count >= threshold:
            target_tier = tier
            break
    
    if target_tier is None:
        return None
    
    # 既存のBUILDERバッジを取得
    existing_badges = crud_badge.get_badges_by_user(db, user_id)
    builder_badges = [
        b for b in existing_badges if b.category == BadgeCategory.BUILDER.value
    ]
    
    # 既に同じティア以上のバッジを持っている場合はスキップ
    if builder_badges:
        max_tier = max(b.tier for b in builder_badges)
        if max_tier >= target_tier:
            return None
    
    # 新しいバッジを付与
    try:
        badge_in = BadgeCreate(
            user_id=user_id,
            category=BadgeCategory.BUILDER,
            tier=target_tier,
        )
        return crud_badge.award_badge(db, badge_in)
    except ValueError:
        # 既に存在する場合はスキップ
        return None
