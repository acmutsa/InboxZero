
import time
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.email_service.outlook.router import (
    auth_outlook_router,
    pending_logins,
    get_connection_service,
)


def make_client(service):
    app = FastAPI()
    app.include_router(auth_outlook_router)

    app.dependency_overrides[get_connection_service] = (
        lambda: service
    )

    return TestClient(app)


def test_callback_connects_account():
    pending_logins.clear()

    service = Mock()
    service.connect.return_value = {
        "status": "success",
        "email": "test@example.com",
        "microsoft_account_id": "microsoft-123",
    }

    pending_logins["valid-state"] = {
        "user_id": "user-123",
        "created_at": time.time(),
    }

    client = make_client(service)

    response = client.get(
        "/auth/outlook/callback",
        params={
            "code": "authorization-code",
            "state": "valid-state",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["email"] == "test@example.com"

    service.connect.assert_called_once_with(
        user_id="user-123",
        code="authorization-code",
    )

    assert "valid-state" not in pending_logins


def test_callback_rejects_invalid_state():
    pending_logins.clear()

    service = Mock()
    client = make_client(service)

    response = client.get(
        "/auth/outlook/callback",
        params={
            "code": "authorization-code",
            "state": "invalid-state",
        },
    )

    assert response.status_code == 400
    service.connect.assert_not_called()


def test_callback_rejects_expired_state():
    pending_logins.clear()

    service = Mock()

    pending_logins["expired-state"] = {
        "user_id": "user-123",
        "created_at": time.time() - 700,
    }

    client = make_client(service)

    response = client.get(
        "/auth/outlook/callback",
        params={
            "code": "authorization-code",
            "state": "expired-state",
        },
    )

    assert response.status_code == 400
    service.connect.assert_not_called()


def test_callback_rejects_reused_state():
    pending_logins.clear()

    service = Mock()
    service.connect.return_value = {
        "status": "success",
        "email": "test@example.com",
    }

    pending_logins["one-time-state"] = {
        "user_id": "user-123",
        "created_at": time.time(),
    }

    client = make_client(service)

    params = {
        "code": "authorization-code",
        "state": "one-time-state",
    }

    first_response = client.get(
        "/auth/outlook/callback",
        params=params,
    )

    second_response = client.get(
        "/auth/outlook/callback",
        params=params,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    service.connect.assert_called_once()
