from typing import Annotated, Any
import jwt
from src.models.decoded_jwt import DecodedJWT
from fastapi import Header, HTTPException, status
from src.config import config


def decode(
    authorization: Annotated[str | None, Header()] = None,
) -> DecodedJWT:

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header",
        )

    try:
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise ValueError("Invalid header format")

        token = parts[1]

        payload: dict[str, Any] = jwt.decode(
            token,
            key=config.SECRET_KEY,
            algorithms=[config.ALGORITHM],
            audience=config.get_audience_list,
            options={"require": ["exp", "iat", "sub", "aud"], "verify_exp": True},
        )

        user_id = payload.get("sub")

        if not isinstance(user_id, str):
            raise ValueError("JWT claim 'sub' must be a string")

        return {"user_id": user_id}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token claims",
        )

    except (IndexError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
        )