"""Unit tests for `lucifex.core.errors`."""

from __future__ import annotations

import pytest

from lucifex.core.errors import (
    AuthenticationError,
    AuthError,
    AuthorizationError,
    ConflictError,
    DomainError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

pytestmark = pytest.mark.unit


_CONCRETE_SUBCLASSES = [
    NotFoundError,
    ConflictError,
    ValidationError,
    AuthError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
]


def test_domain_error_is_exception() -> None:
    assert issubclass(DomainError, Exception)


def test_domain_error_default_init() -> None:
    err = DomainError()

    assert err.message == ""
    assert err.code is None
    assert dict(err.details) == {}
    assert str(err) == ""


def test_domain_error_with_message_and_code() -> None:
    err = DomainError("boom", code="custom_code", details={"hint": "value"})

    assert err.message == "boom"
    assert err.code == "custom_code"
    assert dict(err.details) == {"hint": "value"}
    assert str(err) == "boom"


def test_details_is_defensively_copied() -> None:
    source = {"id": "abc"}
    err = DomainError("nope", details=source)

    source["id"] = "MUTATED"

    assert dict(err.details) == {"id": "abc"}


def test_details_is_read_only() -> None:
    err = DomainError("nope", details={"id": "abc"})

    with pytest.raises(TypeError):
        err.details["id"] = "MUTATED"  # type: ignore[index]


def test_details_defaults_to_empty_mapping() -> None:
    err = DomainError("x")

    assert len(err.details) == 0
    assert dict(err.details) == {}


@pytest.mark.parametrize(
    ("cls", "expected_code"),
    [
        (NotFoundError, "not_found"),
        (ConflictError, "conflict"),
        (ValidationError, "validation_error"),
        (AuthError, "auth_error"),
        (AuthenticationError, "authentication_failed"),
        (AuthorizationError, "authorization_failed"),
        (RateLimitError, "rate_limited"),
    ],
)
def test_subclass_default_code_applied(cls: type[DomainError], expected_code: str) -> None:
    assert cls("msg").code == expected_code


def test_subclass_explicit_code_overrides_default() -> None:
    err = NotFoundError("missing", code="user_not_found")

    assert err.code == "user_not_found"


@pytest.mark.parametrize("cls", _CONCRETE_SUBCLASSES)
def test_all_subclasses_catchable_as_domain_error(cls: type[DomainError]) -> None:
    with pytest.raises(DomainError):
        raise cls("x")


def test_authentication_and_authorization_are_auth_errors() -> None:
    assert issubclass(AuthenticationError, AuthError)
    assert issubclass(AuthorizationError, AuthError)
    assert issubclass(AuthError, DomainError)


def test_repr_contains_class_name_code_and_details() -> None:
    err = NotFoundError("missing user", details={"id": "u-1"})
    rendered = repr(err)

    assert "NotFoundError" in rendered
    assert "missing user" in rendered
    assert "not_found" in rendered
    assert "u-1" in rendered
