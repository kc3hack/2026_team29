"""Fernet対称暗号化によるトークン保護ユーティリティ"""

from cryptography.fernet import Fernet

from app.core.config import settings

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    """Fernetインスタンスを遅延初期化して返す。

    ENCRYPTION_KEYが未設定の場合はValueErrorを送出する。
    """
    global _fernet  # noqa: PLW0603
    if _fernet is None:
        key = settings.ENCRYPTION_KEY
        if not key:
            raise ValueError(
                "ENCRYPTION_KEY is not set. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        _fernet = Fernet(key.encode())
    return _fernet


def encrypt_token(plaintext: str) -> str:
    """平文トークンを暗号化して返す。"""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """暗号化されたトークンを復号して返す。"""
    f = _get_fernet()
    return f.decrypt(ciphertext.encode()).decode()


def reset_fernet() -> None:
    """Fernetインスタンスをリセットする（テスト用）。"""
    global _fernet  # noqa: PLW0603
    _fernet = None
