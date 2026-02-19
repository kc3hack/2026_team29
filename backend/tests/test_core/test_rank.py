from app.core.rank import calculate_rank, update_user_exp
from app.crud.user import create_user
from app.schemas.user import UserCreate


def test_calculate_rank_zero_exp():
    """経験値0はランク0"""
    assert calculate_rank(0) == 0


def test_calculate_rank_boundaries():
    """ランク境界値が正しく計算される"""
    rank_at_0 = calculate_rank(0)
    rank_at_100 = calculate_rank(100)
    rank_at_1000 = calculate_rank(1000)

    assert rank_at_0 <= rank_at_100 <= rank_at_1000


def test_calculate_rank_range():
    """ランクは0-9の範囲内（種子〜世界樹の10段階）"""
    for exp in [0, 50, 100, 500, 1000, 5000, 10000, 100000]:
        rank = calculate_rank(exp)
        assert 0 <= rank <= 9, f"exp={exp} -> rank={rank} is out of range"


def test_calculate_rank_monotonic():
    """経験値が増えればランクは単調非減少"""
    prev_rank = calculate_rank(0)
    for exp in range(0, 10001, 100):
        current_rank = calculate_rank(exp)
        assert current_rank >= prev_rank
        prev_rank = current_rank


def test_update_user_exp(db):
    """経験値加算とランク再計算が正しく動作する"""
    user_in = UserCreate(username="rank_test_user")
    user = create_user(db, user_in)

    assert user.exp == 0
    assert user.rank == 0

    updated = update_user_exp(db, user.id, 500)
    assert updated.exp == 500
    assert updated.rank == calculate_rank(500)


def test_update_user_exp_accumulates(db):
    """経験値が累積加算される"""
    user_in = UserCreate(username="exp_accum_user")
    user = create_user(db, user_in)

    update_user_exp(db, user.id, 100)
    updated = update_user_exp(db, user.id, 200)

    assert updated.exp == 300
    assert updated.rank == calculate_rank(300)
