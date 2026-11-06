from unittest.mock import Mock

# The Gmail API message JSON from earlier
FAKE_GMAIL_MESSAGE = {
    "id": "18c2f4a9b7e3d1f0",
    "threadId": "18c2f4a9b7e3d1f0",
    "labelIds": ["INBOX", "UNREAD", "IMPORTANT", "CATEGORY_PERSONAL"],
    "snippet": "Hi Alex, just following up on the proposal we discussed...",
    "historyId": "987654",
    "internalDate": "1730678400000",
    "sizeEstimate": 15234,
    "payload": {
        "partId": "",
        "mimeType": "multipart/mixed",
        "filename": "",
        "headers": [
            {"name": "From", "value": "Jane Doe <jane.doe@example.com>"},
            {"name": "To", "value": "Alex <alex@example.com>"},
            {"name": "Cc", "value": "team@example.com"},
            {"name": "Subject", "value": "Follow-up on proposal"},
            {"name": "Date", "value": "Tue, 3 Nov 2026 14:00:00 -0600"},
            {"name": "Message-ID", "value": "<CAF123abc@mail.gmail.com>"},
            {"name": "In-Reply-To", "value": "<CAF000xyz@mail.gmail.com>"},
            {"name": "References", "value": "<CAF000xyz@mail.gmail.com>"},
        ],
        "body": {"size": 0},
        "parts": [
            {
                "partId": "0",
                "mimeType": "multipart/alternative",
                "filename": "",
                "headers": [],
                "body": {"size": 0},
                "parts": [
                    {
                        "partId": "0.0",
                        "mimeType": "text/plain",
                        "filename": "",
                        "headers": [{"name": "Content-Type", "value": "text/plain; charset=UTF-8"}],
                        "body": {"size": 312, "data": "SGkgQWxleCwganVzdCBmb2xsb3dpbmcgdXAuLi4"},
                    },
                    {
                        "partId": "0.1",
                        "mimeType": "text/html",
                        "filename": "",
                        "headers": [{"name": "Content-Type", "value": "text/html; charset=UTF-8"}],
                        "body": {"size": 845, "data": "PGRpdj5IaSBBbGV4LCBqdXN0IGZvbGxvd2luZy4uLjwvZGl2Pg"},
                    },
                ],
            },
            {
                "partId": "1",
                "mimeType": "application/pdf",
                "filename": "proposal.pdf",
                "headers": [
                    {"name": "Content-Disposition", "value": 'attachment; filename="proposal.pdf"'}
                ],
                "body": {"attachmentId": "ANGjdJ8xYz...", "size": 13800},
            },
        ],
    },
}


def get_email(service, message_id):
    """Fetch one email using the Gmail API client."""
    return service.users().messages().get(userId="me", id=message_id, format="full").execute()


def test_get_email_with_mock():
    # Fake Gmail service whose .execute() returns our JSON
    mock_service = Mock()
    mock_service.users().messages().get().execute.return_value = FAKE_GMAIL_MESSAGE

    result = get_email(mock_service, "18c2f4a9b7e3d1f0")

    assert result == FAKE_GMAIL_MESSAGE
    headers = {h["name"]: h["value"] for h in result["payload"]["headers"]}
    assert headers["Subject"] == "Follow-up on proposal"
    assert headers["From"] == "Jane Doe <jane.doe@example.com>"
    mock_service.users().messages().get.assert_called_with(
        userId="me", id="18c2f4a9b7e3d1f0", format="full"
    )

def make_mock_service(message=FAKE_GMAIL_MESSAGE):
    """Return a fake Gmail service whose .execute() returns `message`."""
    service = Mock()
    service.users().messages().get().execute.return_value = message
    return service

import base64


def decode_base64url(data):
    """Turn Gmail's base64url string into readable text."""
    padded = data + "=" * (-len(data) % 4)   # Gmail strips the '=' padding
    return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")


def get_body(message, mime_type="text/plain"):
    """Find and decode the body of a Gmail message.

    mime_type: "text/plain" for plain text, "text/html" for HTML.
    Returns None if the email has no part of that type.
    """
    def search(part):
        if part.get("mimeType") == mime_type and part.get("body", {}).get("data"):
            return decode_base64url(part["body"]["data"])
        for child in part.get("parts", []) or []:
            found = search(child)
            if found:
                return found
        return None

    return search(message.get("payload", {}))