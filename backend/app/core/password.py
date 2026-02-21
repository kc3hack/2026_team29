"""パスワードハッシュ化ユーティリティ (ID入力ログイン用, ADR 017)

PBKDF2-HMAC-SHA256 (Python 標準ライブラリ hashlib) を使用する。
- 外部依存なし: passlib/bcrypt の互換性問題を回避
- OWASP 推奨: PBKDF2-SHA256、iterations=600_000 (2024年推奨値)
- ストレージ形式: "<hex_salt>$<hex_hash>"（どちらも 64 文字）
- timing-safe 比較: secrets.compare_digest
"""

import hashlib
import logging
import secrets

logger = logging.getLogger(__name__)

_ITERATIONS = 600_000
_ALGORITHM = "sha256"
_SALT_BYTES = 32   # 256 bit


def hash_password(plain: str) -> str:
    """平文パスワードを PBKDF2-HMAC-SHA256 でハッシュ化して返す。

    返り値は "<hex_salt>$<hex_digest>" 形式。
    salt はリクエストごとに CSPRNG で生成する。
    """
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        _ALGORITHM, plain.encode("utf-8"), salt, _ITERATIONS
    )
    return f"{salt.hex()}${digest.hex()}"


def verify_password(plain: str, stored: str) -> bool:
    """平文パスワードと保存済みハッシュを比較する。

    timing-safe な secrets.compare_digest を使用しタイミング攻撃を防ぐ。
    フォーマット不正の場合は False を返す（例外は送出しない）。
    """
    try:
        salt_hex, stored_hex = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        candidate = hashlib.pbkdf2_hmac(
            _ALGORITHM, plain.encode("utf-8"), salt, _ITERATIONS
        )
        return secrets.compare_digest(candidate.hex(), stored_hex)
    except (ValueError, AttributeError):
        # フォーマット不正（split失敗 / fromhex失敗）は想定内の失敗として False を返す
        return False
    except Exception:
        # 予期しない例外（メモリエラー等）はログに記録して False を返す
        logger.warning("verify_password: unexpected exception", exc_info=True)
        return False
