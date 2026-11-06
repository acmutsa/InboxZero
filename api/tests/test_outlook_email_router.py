
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.email_service.outlook.email_router import (
    outlook_email_router,
    get_outlook_service,
)


def create_test_client(service):
    app = FastAPI()
    app.include_router(outlook_email_router)

    app.dependency_overrides[get_outlook_service] = lambda: service

    return TestClient(app)


def test_get_profile():
    service = Mock()
    service.get_profile.return_value = {
        "email": "test@example.com"
    }

    client = create_test_client(service)
    response = client.get("/api/outlook/profile")

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_get_messages():
    service = Mock()
    service.get_messages.return_value = {
        "value": [{"id": "message-1"}]
    }

    client = create_test_client(service)
    response = client.get("/api/outlook/messages")

    assert response.status_code == 200
    assert response.json()["value"][0]["id"] == "message-1"


def test_get_message():
    service = Mock()
    service.get_message.return_value = {
        "id": "message-1",
        "subject": "Hello",
    }

    client = create_test_client(service)
    response = client.get("/api/outlook/messages/message-1")

    assert response.status_code == 200
    assert response.json()["subject"] == "Hello"


def test_get_drafts():
    service = Mock()
    service.get_drafts.return_value = {
        "value": [{"id": "draft-1"}]
    }

    client = create_test_client(service)
    response = client.get("/api/outlook/drafts")

    assert response.status_code == 200
    assert response.json()["value"][0]["id"] == "draft-1"


def test_get_draft():
    service = Mock()
    service.get_draft.return_value = {
        "id": "draft-1"
    }

    client = create_test_client(service)
    response = client.get("/api/outlook/drafts/draft-1")

    assert response.status_code == 200
    assert response.json()["id"] == "draft-1"


def test_unconfigured_dependency_returns_503():
    app = FastAPI()
    app.include_router(outlook_email_router)
    client = TestClient(app)

    response = client.get("/api/outlook/messages")

    assert response.status_code == 503


def test_create_draft():
    service = Mock()
    service.create_draft.return_value = {"id": "draft-123"}

    client = create_test_client(service)

    response = client.post(
        "/api/outlook/drafts",
        json={
            "message": {
                "subject": "Test draft",
                "body": {
                    "contentType": "Text",
                    "content": "Hello from InboxZero"
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": "test@example.com"
                        }
                    }
                ]
            }
        },
    )

    assert response.status_code == 201, response.text
    service.create_draft.assert_called_once()


def test_send_message():
    service = Mock()
    client = create_test_client(service)

    response = client.post(
        "/api/outlook/messages/send",
        json={
            "subject": "Test message",
            "body": {
                "contentType": "Text",
                "content": "Hello from InboxZero"
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": "test@example.com"
                    }
                }
            ]
        },
    )

    assert response.status_code == 204, response.text
    service.send_message.assert_called_once()

def test_get_categories():
    service = Mock()
    service.get_labels.return_value = {
        "labels": [{"id": "category-1", "name": "Important"}]
    }

    client = create_test_client(service)
    response = client.get("/api/outlook/categories")

    assert response.status_code == 200
    service.get_labels.assert_called_once()


def test_unconfigured_send_is_blocked():
    app = FastAPI()
    app.include_router(outlook_email_router)

    client = TestClient(app)

    response = client.post(
        "/api/outlook/drafts/draft-123/send"
    )

    assert response.status_code == 503
def test_send_draft():
    service = Mock()
    client = create_test_client(service)

    response = client.post(
        "/api/outlook/drafts/draft-123/send"
    )

    assert response.status_code == 204
    service.send_draft.assert_called_once_with("draft-123")
def test_modify_message():
    service = Mock()
    service.modify_message.return_value = {
        "id": "message-123",
        "isRead": True,
    }

    client = create_test_client(service)

    response = client.patch(
        "/api/outlook/messages/message-123",
        json={"isRead": True},
    )

    assert response.status_code == 200, response.text
    service.modify_message.assert_called_once()


def test_create_category():
    service = Mock()
    service.create_label.return_value = {
        "id": "category-123",
        "name": "InboxZero-Test",
    }

    client = create_test_client(service)

    response = client.post(
        "/api/outlook/categories",
        json={"name": "InboxZero-Test"},
    )

    assert response.status_code == 201, response.text
    service.create_label.assert_called_once()