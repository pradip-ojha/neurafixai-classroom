from datetime import timedelta
from uuid import uuid4

from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_opaque_token,
    hash_password,
    hash_token,
    verify_password,
)


def test_password_hashing_uses_non_reversible_hash() -> None:
    password = "Correct Horse Battery 2026!"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_opaque_token_hash_is_stable_and_does_not_store_raw_token() -> None:
    token = generate_opaque_token()

    token_hash = hash_token(token)

    assert token_hash == hash_token(token)
    assert token_hash != token
    assert len(token_hash) == 64


def test_access_token_contains_required_security_claims() -> None:
    user_id = uuid4()
    institution_id = uuid4()
    session_id = uuid4()

    token = create_access_token(
        user_id=user_id,
        institution_id=institution_id,
        session_id=session_id,
        expires_delta=timedelta(minutes=5),
    )
    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["institution_id"] == str(institution_id)
    assert payload["session_id"] == str(session_id)
    assert payload["type"] == "access"
    assert "jti" in payload
    assert "exp" in payload

