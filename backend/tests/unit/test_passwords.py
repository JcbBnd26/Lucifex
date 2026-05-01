"""Unit tests for `lucifex.auth.passwords`."""

from __future__ import annotations

import pytest

from lucifex.auth.passwords import hash_password, needs_rehash, verify_password

pytestmark = pytest.mark.unit


def test_hash_password_returns_argon2id_string() -> None:
    h = hash_password("correct horse battery staple")
    assert h.startswith("$argon2id$")


def test_hash_password_is_nondeterministic() -> None:
    """Same plaintext, two distinct hashes (random salt per call)."""
    h1 = hash_password("hunter2")
    h2 = hash_password("hunter2")
    assert h1 != h2


def test_verify_password_accepts_correct() -> None:
    plaintext = "correct horse battery staple"
    h = hash_password(plaintext)
    assert verify_password(plaintext, h) is True


def test_verify_password_rejects_wrong() -> None:
    h = hash_password("correct horse battery staple")
    assert verify_password("wrong password", h) is False


def test_verify_password_rejects_garbage_hash() -> None:
    """A malformed hash is treated as a verification failure, not raised."""
    assert verify_password("anything", "not-a-valid-hash") is False
    assert verify_password("anything", "") is False


def test_needs_rehash_false_for_fresh_hash() -> None:
    """A hash freshly produced with current defaults does not need rehashing."""
    h = hash_password("anything")
    assert needs_rehash(h) is False
