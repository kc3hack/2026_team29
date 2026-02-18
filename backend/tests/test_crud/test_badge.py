import pytest

from app.crud.badge import award_badge, get_badges_by_user
from app.crud.user import create_user
from app.models.enums import BadgeCategory
from app.schemas.badge import BadgeCreate
from app.schemas.user import UserCreate


def test_award_badge(db):
    user = create_user(db, UserCreate(username="badge_user"))
    badge_in = BadgeCreate(
        user_id=user.id,
        category=BadgeCategory.COMMIT,
        tier=1,
    )
    badge = award_badge(db, badge_in)

    assert badge.id is not None
    assert badge.user_id == user.id
    assert badge.category == BadgeCategory.COMMIT
    assert badge.tier == 1
    assert badge.earned_at is not None


def test_get_badges_by_user(db):
    user = create_user(db, UserCreate(username="badge_list_user"))
    award_badge(db, BadgeCreate(user_id=user.id, category=BadgeCategory.COMMIT, tier=1))
    award_badge(db, BadgeCreate(user_id=user.id, category=BadgeCategory.DAYS, tier=2))

    badges = get_badges_by_user(db, user.id)
    assert len(badges) == 2
    categories = {b.category for b in badges}
    assert BadgeCategory.COMMIT in categories
    assert BadgeCategory.DAYS in categories


def test_get_badges_by_user_empty(db):
    user = create_user(db, UserCreate(username="no_badge_user"))
    badges = get_badges_by_user(db, user.id)
    assert badges == []


def test_award_duplicate_badge_rejected(db):
    """同じuser_id, category, tierの組み合わせは重複不可"""
    user = create_user(db, UserCreate(username="dup_badge_user"))
    badge_in = BadgeCreate(user_id=user.id, category=BadgeCategory.BUILDER, tier=1)
    award_badge(db, badge_in)

    with pytest.raises(Exception):
        award_badge(db, badge_in)
