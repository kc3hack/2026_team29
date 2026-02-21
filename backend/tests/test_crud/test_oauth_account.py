from datetime import datetime, timezone

import pytest

from app.core.encryption import decrypt_token
from app.crud.oauth_account import (
    create_oauth_account,
    get_by_provider_user_id,
    get_oauth_account_by_user_provider,
    update_oauth_tokens,
)
from app.crud.user import create_user
from app.schemas.oauth_account import OAuthAccountCreate, OAuthTokenUpdate
from app.schemas.user import UserCreate


# ---------------------------------------------------------------------------
# 作成 (Create)
# ---------------------------------------------------------------------------


def test_create_oauth_account(db):
    """OAuthアカウントが正常に作成される"""
    user = create_user(db, UserCreate(username="oauth_user"))
    oauth_in = OAuthAccountCreate(
        user_id=user.id,
        provider="github",
        provider_user_id="12345",
        access_token="ghp_test_token",
    )
    account = create_oauth_account(db, oauth_in)

    assert account.id is not None
    assert account.user_id == user.id
    assert account.provider == "github"
    assert account.provider_user_id == "12345"


def test_create_oauth_account_access_token_encrypted(db):
    """access_tokenが暗号化されてDBに保存される（平文と一致しない）"""
    user = create_user(db, UserCreate(username="oauth_enc_user"))
    plaintext = "ghp_plaintext_token_abc123"
    account = create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="enc_test",
            access_token=plaintext,
        ),
    )

    assert account.encrypted_access_token != plaintext
    assert account.encrypted_access_token is not None


def test_create_oauth_account_access_token_decryptable(db):
    """暗号化されたaccess_tokenを復号すると元の平文が得られる"""
    user = create_user(db, UserCreate(username="oauth_dec_user"))
    plaintext = "ghp_roundtrip_token_xyz789"
    account = create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="dec_test",
            access_token=plaintext,
        ),
    )

    decrypted = decrypt_token(account.encrypted_access_token)
    assert decrypted == plaintext


def test_create_oauth_account_refresh_token_encrypted(db):
    """refresh_tokenも暗号化されてDBに保存される"""
    user = create_user(db, UserCreate(username="oauth_refresh_enc_user"))
    refresh_plaintext = "ghr_refresh_secret_123"
    account = create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="ref_test",
            access_token="ghp_access",
            refresh_token=refresh_plaintext,
        ),
    )

    assert account.encrypted_refresh_token != refresh_plaintext
    decrypted = decrypt_token(account.encrypted_refresh_token)
    assert decrypted == refresh_plaintext


def test_create_oauth_account_with_expires_at(db):
    """expires_atが正しく保存される"""
    user = create_user(db, UserCreate(username="oauth_expires_user"))
    expires = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    account = create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="exp_test",
            access_token="ghp_token",
            expires_at=expires,
        ),
    )

    assert account.expires_at is not None


def test_create_oauth_account_without_optional_fields(db):
    """refresh_token, expires_atが未指定でもNullで作成可能"""
    user = create_user(db, UserCreate(username="oauth_minimal_user"))
    account = create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="min_test",
            access_token="ghp_token",
        ),
    )

    assert account.encrypted_refresh_token is None
    assert account.expires_at is None


# ---------------------------------------------------------------------------
# 取得 (Read)
# ---------------------------------------------------------------------------


def test_get_oauth_account_by_user_provider(db):
    """user_id + providerで正しくOAuthアカウントを取得できる"""
    user = create_user(db, UserCreate(username="oauth_get_user"))
    create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="67890",
            access_token="ghp_find_me",
        ),
    )

    found = get_oauth_account_by_user_provider(db, user.id, "github")
    assert found is not None
    assert found.provider_user_id == "67890"


def test_get_oauth_account_not_found(db):
    """存在しないuser_id/providerでNoneが返る"""
    result = get_oauth_account_by_user_provider(db, 999, "github")
    assert result is None


def test_get_oauth_account_wrong_provider(db):
    """同一ユーザーでもproviderが異なればNoneが返る"""
    user = create_user(db, UserCreate(username="oauth_wrong_provider_user"))
    create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="wp_test",
            access_token="ghp_token",
        ),
    )

    result = get_oauth_account_by_user_provider(db, user.id, "google")
    assert result is None


# ---------------------------------------------------------------------------
# get_by_provider_user_id (W-3: GitHub OAuthコールバックでの既存ユーザー照合の核心関数)
# ---------------------------------------------------------------------------


def test_get_by_provider_user_id_found(db):
    """プロバイダー + provider_user_id で正しく OAuthAccount を取得できる"""
    user = create_user(db, UserCreate(username="oauth_gbupi_user"))
    create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="gh_12345",
            access_token="ghp_token",
        ),
    )

    found = get_by_provider_user_id(db, "github", "gh_12345")
    assert found is not None
    assert found.provider_user_id == "gh_12345"
    assert found.user_id == user.id


def test_get_by_provider_user_id_not_found(db):
    """存在しない provider_user_id は None を返す"""
    result = get_by_provider_user_id(db, "github", "nonexistent_id")
    assert result is None


def test_get_by_provider_user_id_provider_mismatch(db):
    """同じ provider_user_id でも provider が異なる場合は None を返す"""
    user = create_user(db, UserCreate(username="oauth_provider_mismatch_user"))
    create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="pm_12345",
            access_token="ghp_token",
        ),
    )

    # 別プロバイダー(同じ ID)で検索 → ヒットしないことを確認
    result = get_by_provider_user_id(db, "google", "pm_12345")
    assert result is None


# ---------------------------------------------------------------------------
# 更新 (Update)
# ---------------------------------------------------------------------------


def test_update_oauth_tokens_access_token(db):
    """access_tokenの更新で暗号文が変わり、復号すると新しい平文が得られる"""
    user = create_user(db, UserCreate(username="oauth_update_user"))
    account = create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="upd_test",
            access_token="ghp_old_token",
        ),
    )
    old_encrypted = account.encrypted_access_token

    updated = update_oauth_tokens(
        db,
        account.id,
        OAuthTokenUpdate(access_token="ghp_new_token"),
    )

    assert updated.encrypted_access_token != old_encrypted
    assert decrypt_token(updated.encrypted_access_token) == "ghp_new_token"


def test_update_oauth_tokens_refresh_token(db):
    """refresh_tokenの更新で暗号化された値が正しく保存される"""
    user = create_user(db, UserCreate(username="oauth_update_refresh_user"))
    account = create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="upd_ref_test",
            access_token="ghp_token",
        ),
    )

    updated = update_oauth_tokens(
        db,
        account.id,
        OAuthTokenUpdate(refresh_token="ghr_new_refresh"),
    )

    assert updated.encrypted_refresh_token is not None
    assert decrypt_token(updated.encrypted_refresh_token) == "ghr_new_refresh"


def test_update_oauth_tokens_expires_at(db):
    """expires_atの更新が反映される"""
    user = create_user(db, UserCreate(username="oauth_update_expires_user"))
    account = create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=user.id,
            provider="github",
            provider_user_id="upd_exp_test",
            access_token="ghp_token",
        ),
    )
    new_expires = datetime(2027, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

    updated = update_oauth_tokens(
        db,
        account.id,
        OAuthTokenUpdate(expires_at=new_expires),
    )

    assert updated.expires_at is not None


# ---------------------------------------------------------------------------
# 制約 (Constraints)
# ---------------------------------------------------------------------------


def test_create_duplicate_user_provider_rejected(db):
    """同一user_id + providerの組み合わせはUNIQUE制約で拒否される"""
    user = create_user(db, UserCreate(username="oauth_dup_user"))
    oauth_in = OAuthAccountCreate(
        user_id=user.id,
        provider="github",
        provider_user_id="dup_test_1",
        access_token="ghp_token_1",
    )
    create_oauth_account(db, oauth_in)

    duplicate = OAuthAccountCreate(
        user_id=user.id,
        provider="github",
        provider_user_id="dup_test_2",
        access_token="ghp_token_2",
    )
    with pytest.raises(Exception):
        create_oauth_account(db, duplicate)


# MVP段階ではGitHubのみ対応のため、複数プロバイダのテストはスキップ
# def test_create_same_user_different_providers_allowed(db):
#     """同一ユーザーでも異なるproviderならOAuthアカウント作成可能"""
#     # 将来Google等を追加する際に有効化
