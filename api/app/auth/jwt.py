import os
import jwt

from functools import lru_cache
from typing import Annotated

from fastapi import Header, HTTPException, status
from jwt import PyJWKClient

from app.models.decoded_jwt import DecodedJWT


@lru_cache
def get_clerk_jwks_client():
    jwks_url = os.getenv("CLERK_JWKS_URL")

    if not jwks_url:
        raise RuntimeError(
            "CLERK_JWKS_URL is missing from .env"
        )

    if not jwks_url.startswith("https://"):
        raise RuntimeError(
            "CLERK_JWKS_URL must use HTTPS"
        )

    return PyJWKClient(jwks_url)


def decode(
    authorization: Annotated[str | None, Header()] = None,
) -> DecodedJWT:

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header",
        )

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format",
        )

    token = parts[1]

    issuer = os.getenv("CLERK_ISSUER")
    audience = os.getenv("CLERK_AUDIENCE")

    if not issuer:
        raise HTTPException(
            status_code=500,
            detail="Clerk issuer is not configured",
        )

    try:
        signing_key = get_clerk_jwks_client().get_signing_key_from_jwt(token)

        options = {
            "require": ["exp", "iat", "nbf", "iss", "sub"],
            "verify_aud": bool(audience),
        }

        payload = jwt.decode(
            token,
            key=signing_key.key,
            algorithms=["RS256"],
            issuer=issuer,
            audience=audience if audience else None,
            options=options,
            leeway=5,
        )

        user_id = payload.get("sub")

        if not isinstance(user_id, str) or not user_id:
            raise jwt.InvalidTokenError("Missing user ID")

        return DecodedJWT(user_id=user_id)

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired Clerk token",
        )

    except (RuntimeError, ValueError, requests.RequestException):
        raise HTTPException(
            status_code=503,
            detail="Clerk verification service unavailable",
        )