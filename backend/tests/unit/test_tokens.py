"""Unit tests for `lucifex.auth.tokens`."""

from __future__ import annotations

import re

import pytest

from lucifex.auth.tokens import (
    SESSION_TOKEN_BYTES,
    constant_time_compare,
    generate_session_token,
    hash_session_token,
)

pytestmark = pytest.mark.unit

# `secrets.token_urlsafe` uses the URL-safe base64 alphabet without padding.
_URLSAFE_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def test_session_token_bytes_constant() -> None:
    """Sanity check: 32 bytes = 256 bits."""
    assert SESSION_TOKEN_BYTES == 32


def test_generate_session_token_is_urlsafe() -> None:
    token = generate_session_token()
    assert _URLSAFE_RE.match(token), f"non-urlsafe characters in {token!r}"


def test_generate_session_token_has_expected_length() -> None:
    """`token_urlsafe(32)` produces ~43 characters (no padding)."""
    token = generate_session_token()
    # Allow a small range to accommodate any future tuning of the constant.
    assert 40 <= len(token) <= 64


def test_generate_session_token_is_unique() -> None:
    """Two consecutive calls produce different tokens (probabilistic)."""
    a = generate_session_token()
    b = generate_session_token()
    assert a != b


def test_hash_session_token_is_deterministic() -> None:
    token = "fixed-token-value"
    assert hash_session_token(token) == hash_session_token(token)


def test_hash_session_token_differs_for_different_inputs() -> None:
    assert hash_session_token("token-a") != hash_session_token("token-b")


def test_hash_session_token_is_64_char_hex() -> None:
    h = hash_session_token("any input")
    assert len(h) == 64
    assert re.match(r"^[0-9a-f]{64}$", h)


def test_constant_time_compare_equal_strings_true() -> None:
    assert constant_time_compare("abc123", "abc123") is True


def test_constant_time_compare_unequal_strings_false() -> None:
    assert constant_time_compare("abc123", "abc124") is False


def test_constant_time_compare_different_lengths_false() -> None:
    assert constant_time_compare("short", "longer-string") is False
