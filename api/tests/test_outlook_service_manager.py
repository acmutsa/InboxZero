
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from app.email_service.outlook.service_manager import (
    OutlookServiceManager,
)


def test_valid_token_creates_service():
    manager = OutlookServiceManager(
        access_token="valid-token",
        refresh_token="refresh-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
        token_manager=Mock(),
    )

    manager.token_manager.get_valid_token.return_value = {
        "access_token": "valid-token",
        "refresh_token": "refresh-token",
        "expires_at": manager.expires_at,
        "refreshed": False,
    }

    with patch(
        "app.email_service.outlook.service_manager.OutlookService"
    ) as service_class:
        manager.get_service()
        service_class.assert_called_once_with("valid-token")


def test_expired_token_refreshes_and_saves():
    save_tokens = Mock()
    token_manager = Mock()
    new_expiration = datetime.now(timezone.utc) + timedelta(hours=1)

    token_manager.get_valid_token.return_value = {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
        "expires_at": new_expiration,
        "refreshed": True,
    }

    manager = OutlookServiceManager(
        access_token="old-access-token",
        refresh_token="old-refresh-token",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        save_tokens=save_tokens,
        token_manager=token_manager,
    )

    with patch(
        "app.email_service.outlook.service_manager.OutlookService"
    ) as service_class:
        manager.get_service()
        service_class.assert_called_once_with("new-access-token")

    save_tokens.assert_called_once_with(
        "new-access-token",
        "new-refresh-token",
        new_expiration,
    )


def test_refresh_requires_persistence():
    token_manager = Mock()
    token_manager.get_valid_token.return_value = {
        "access_token": "new-token",
        "refresh_token": "new-refresh-token",
        "expires_at": datetime.now(timezone.utc),
        "refreshed": True,
    }

    manager = OutlookServiceManager(
        access_token="old-token",
        refresh_token="old-refresh-token",
        expires_at=datetime.now(timezone.utc),
        token_manager=token_manager,
    )

    with pytest.raises(RuntimeError, match="Token persistence"):
        manager.get_service()
