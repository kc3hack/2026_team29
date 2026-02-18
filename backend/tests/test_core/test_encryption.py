from app.core.encryption import encrypt_token, decrypt_token


def test_encrypt_decrypt_roundtrip():
    """暗号化→復号で元のトークンが復元される"""
    original = "ghp_abc123def456"
    encrypted = encrypt_token(original)

    assert encrypted != original
    assert decrypt_token(encrypted) == original


def test_encrypt_produces_different_ciphertext():
    """同じ平文でも毎回異なる暗号文が生成される（Fernetの仕様）"""
    token = "ghp_abc123def456"
    enc1 = encrypt_token(token)
    enc2 = encrypt_token(token)

    assert enc1 != enc2
    assert decrypt_token(enc1) == token
    assert decrypt_token(enc2) == token


def test_encrypt_empty_string():
    """空文字列でも暗号化・復号できる"""
    encrypted = encrypt_token("")
    assert decrypt_token(encrypted) == ""
