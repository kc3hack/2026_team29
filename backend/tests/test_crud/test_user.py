from app.crud.user import create_user, get_user, get_user_by_username
from app.schemas.user import UserCreate


def test_create_user(db):
    user_in = UserCreate(username="REID")
    user = create_user(db, user_in)

    assert user.id is not None
    assert user.username == "REID"
    assert user.level == 1
    assert user.exp == 0


def test_get_user(db):
    user_in = UserCreate(username="TAKUMI")
    created = create_user(db, user_in)

    found = get_user(db, created.id)
    assert found is not None
    assert found.username == "TAKUMI"


def test_get_user_not_found(db):
    result = get_user(db, 999)
    assert result is None


def test_get_user_by_username(db):
    user_in = UserCreate(username="MAX")
    create_user(db, user_in)

    found = get_user_by_username(db, "MAX")
    assert found is not None
    assert found.username == "MAX"


def test_get_user_by_username_not_found(db):
    result = get_user_by_username(db, "nonexistent")
    assert result is None
