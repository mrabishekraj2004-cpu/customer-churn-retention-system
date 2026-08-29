from unittest.mock import Mock

import pytest
from fastapi import HTTPException, Request

from src.security import rate_limit


def make_request(
    client_host: str,
) -> Request:
    request = Mock(spec=Request)
    request.client = Mock()
    request.client.host = client_host

    return request


def test_login_rate_limit_rejects_attempt_over_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rate_limit.time,
        "monotonic",
        lambda: 100.0,
    )

    request = make_request("192.0.2.10")

    for _ in range(
        rate_limit.settings.login_rate_limit_attempts
    ):
        rate_limit.enforce_login_rate_limit(
            request
        )

    with pytest.raises(HTTPException) as exc_info:
        rate_limit.enforce_login_rate_limit(
            request
        )

    assert exc_info.value.status_code == 429
    assert exc_info.value.detail == (
        "Too many login attempts."
    )
    assert exc_info.value.headers == {
        "Retry-After": "60"
    }


def test_login_rate_limit_allows_request_after_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_time = 100.0

    monkeypatch.setattr(
        rate_limit.time,
        "monotonic",
        lambda: current_time,
    )

    request = make_request("192.0.2.20")

    for _ in range(
        rate_limit.settings.login_rate_limit_attempts
    ):
        rate_limit.enforce_login_rate_limit(
            request
        )

    current_time = 161.0

    rate_limit.enforce_login_rate_limit(
        request
    )


def test_login_rate_limit_tracks_clients_independently(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rate_limit.time,
        "monotonic",
        lambda: 100.0,
    )

    first_client = make_request("192.0.2.30")
    second_client = make_request("192.0.2.31")

    for _ in range(
        rate_limit.settings.login_rate_limit_attempts
    ):
        rate_limit.enforce_login_rate_limit(
            first_client
        )

    rate_limit.enforce_login_rate_limit(
        second_client
    )

    with pytest.raises(HTTPException) as exc_info:
        rate_limit.enforce_login_rate_limit(
            first_client
        )

    assert exc_info.value.status_code == 429


def test_login_rate_limit_reset_clears_attempts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rate_limit.time,
        "monotonic",
        lambda: 100.0,
    )

    request = make_request("192.0.2.40")

    for _ in range(
        rate_limit.settings.login_rate_limit_attempts
    ):
        rate_limit.enforce_login_rate_limit(
            request
        )

    rate_limit.reset_login_rate_limit()

    rate_limit.enforce_login_rate_limit(
        request
    )
