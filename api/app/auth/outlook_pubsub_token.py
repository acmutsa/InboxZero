import hashlib
import hmac
import uuid

from app.config import config


def encode(account_id: uuid.UUID) -> str:
    message = f"outlook-notification:{account_id.hex}".encode()
    signature = hmac.new(config.OUTLOOK_STATE_SECRET.encode(), message, hashlib.sha256).hexdigest()
    return f"{account_id.hex}.{signature}"


def decode(client_state: str) -> uuid.UUID | None:
    try:
        account_id = uuid.UUID(client_state.partition(".")[0])

    except ValueError:
        return None

    is_genuine = hmac.compare_digest(encode(account_id).encode(), client_state.encode())
    return account_id if is_genuine else None
