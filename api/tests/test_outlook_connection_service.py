
from unittest.mock import Mock

import pytest

from app.email_service.outlook.account_store import (
    InMemoryOutlookAccountStore,
)
from app.email_service.outlook.connection_service import (
    OutlookConnectionService,
)


def test_connect_saves_account():
    store = InMemoryOutlookAccountStore()
    oauth = Mock()

    oauth.exchange_code.return_value = {
        "access_token": "access-123",
        "refresh_token": "refresh-123",
        "expires_in": 3600,
    }

    oauth.get_account_profile.return_value = {
        "microsoft_account_id": "microsoft-123",
        "email": "test@example.com",
    }

    service = OutlookConnectionService(store, oauth)

    result = service.connect("user-123", "authorization-code")

    account = store.get("user-123", "microsoft-123")

    assert result["status"] == "success"
    assert result["email"] == "test@example.com"
    assert account is not None
    assert account.access_token == "access-123"
    assert account.refresh_token == "refresh-123"

    oauth.exchange_code.assert_called_once_with(
        "authorization-code"
    )


def test_connect_rejects_missing_refresh_token():
    store = InMemoryOutlookAccountStore()
    oauth = Mock()

    oauth.exchange_code.return_value = {
        "access_token": "access-123",
    }

    service = OutlookConnectionService(store, oauth)

    with pytest.raises(RuntimeError):
        service.connect("user-123", "authorization-code")


def test_connect_requires_user_and_code():
    store = InMemoryOutlookAccountStore()
    oauth = Mock()
    service = OutlookConnectionService(store, oauth)

    with pytest.raises(ValueError):
        service.connect("", "authorization-code")

    with pytest.raises(ValueError):
        service.connect("user-123", "")
