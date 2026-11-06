
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from app.email_service.outlook.token_manager import (
    OutlookTokenManager,
)


def test_valid_token_does_not_refresh():
    oauth = Mock()
    manager = OutlookTokenManager(oauth=oauth)

    expires_at = datetime.now(timezone.utc) + timedelta(
        hours=2
    )

    result = manager.get_valid_token(
        access_token="valid-access-token",
        refresh_token="refresh-token",
        expires_at=expires_at,
    )

    assert result["access_token"] == "valid-access-token"
    assert result["refreshed"] is False

    oauth.refresh_access_token.assert_not_called()


def test_expired_token_refreshes():
    oauth = Mock()

    oauth.refresh_access_token.return_value = {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
        "expires_in": 3600,
    }

    manager = OutlookTokenManager(oauth=oauth)

    expires_at = datetime.now(timezone.utc) - timedelta(
        minutes=10
    )

    result = manager.get_valid_token(
        access_token="expired-access-token",
        refresh_token="old-refresh-token",
        expires_at=expires_at,
    )

    assert result["access_token"] == "new-access-token"
    assert result["refresh_token"] == "new-refresh-token"
    assert result["refreshed"] is True

    oauth.refresh_access_token.assert_called_once_with(
        "old-refresh-token"
    )


def test_refresh_keeps_old_refresh_token_if_not_rotated():
    oauth = Mock()

    oauth.refresh_access_token.return_value = {
        "access_token": "new-access-token",
        "expires_in": 3600,
    }

    manager = OutlookTokenManager(oauth=oauth)

    result = manager.refresh("existing-refresh-token")

    assert result["refresh_token"] == "existing-refresh-token"


def test_refresh_rejects_missing_access_token():
    oauth = Mock()

    oauth.refresh_access_token.return_value = {
        "error": "invalid_grant"
    }

    manager = OutlookTokenManager(oauth=oauth)

    with pytest.raises(RuntimeError):
        manager.refresh("invalid-refresh-token")
