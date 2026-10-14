import secrets
import time
import jwt

from typing import Any

from fastapi import HTTPException
from fastapi import status

from app.models.decoded_google_state import DecodedGoogleState

from app.config import config


def encode(user_id: str, gmail: str) -> str:

    payload: dict[str, Any] = {
        "sub": user_id,
        "gmail": gmail,
        "purpose": "gmail_connect",
        "jti": secrets.token_urlsafe(16),
        "iat": int(time.time()),
        "exp": int(time.time()) + config.GOOGLE_STATE_EXPIRE_SECONDS,
    }

    token = jwt.encode(
        payload, 
        key=config.GOOGLE_STATE_SECRET, 
        algorithm=config.ALGORITHM
    )

    return token


def decode(
    state: str, user_id: str
) -> DecodedGoogleState:

    try:
        payload: dict[str, Any] = jwt.decode(
            state,
            key=config.GOOGLE_STATE_SECRET,
            algorithms=[config.ALGORITHM],
            options={"require": ["sub", "gmail", "purpose", "jti", "iat", "exp"]},
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Gmail connection link expired. Please try connecting again.",
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state",
        )

    if payload["purpose"] != "gmail_connect":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state",
        )

    if payload["sub"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="State does not belong to this user",
        )

    return DecodedGoogleState(**payload)