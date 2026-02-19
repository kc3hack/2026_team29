from app.crud.profile import create_profile, get_profile_by_user_id, update_profile
from app.crud.user import create_user
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.user import UserCreate
import pytest

from app.crud.skill_tree import update_skill_tree
from app.crud.quest_progress import complete_quest
from app.models.enums import SkillCategory


def test_create_profile(db):
    user = create_user(db, UserCreate(username="profile_user"))
    profile_in = ProfileCreate(
        user_id=user.id,
        github_username="octocat",
        qiita_id="qiita_user",
    )
    profile = create_profile(db, profile_in)

    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.github_username == "octocat"
    assert profile.qiita_id == "qiita_user"
    assert profile.connpass_id is None
    assert profile.portfolio_url is None


def test_get_profile_by_user_id(db):
    user = create_user(db, UserCreate(username="get_profile_user"))
    create_profile(db, ProfileCreate(user_id=user.id, github_username="gh_user"))

    found = get_profile_by_user_id(db, user.id)
    assert found is not None
    assert found.github_username == "gh_user"


def test_get_profile_by_user_id_not_found(db):
    result = get_profile_by_user_id(db, 999)
    assert result is None


def test_update_profile(db):
    user = create_user(db, UserCreate(username="update_profile_user"))
    profile = create_profile(db, ProfileCreate(user_id=user.id))

    updated = update_profile(
        db,
        profile.id,
        ProfileUpdate(
            github_username="new_gh", portfolio_url="https://example.com/portfolio"
        ),
    )
    assert updated.github_username == "new_gh"
    assert updated.portfolio_url == "https://example.com/portfolio"


def test_update_profile_not_found(db):
    with pytest.raises(ValueError, match="Profile with id=999 not found"):
        update_profile(db, 999, ProfileUpdate(github_username="test"))


def test_update_skill_tree_not_found(db):
    with pytest.raises(ValueError, match="SkillTree for user_id=999.*not found"):
        update_skill_tree(db, user_id=999, category=SkillCategory.WEB, tree_data={})


def test_complete_quest_not_found(db):
    with pytest.raises(
        ValueError, match="QuestProgress for user_id=999, quest_id=888 not found"
    ):
        complete_quest(db, user_id=999, quest_id=888)
