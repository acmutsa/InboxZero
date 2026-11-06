
import os

from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()


def get_cipher() -> Fernet:
    key = os.getenv("OUTLOOK_TOKEN_ENCRYPTION_KEY")

    if not key:
        raise RuntimeError(
            "OUTLOOK_TOKEN_ENCRYPTION_KEY is missing"
        )

    return Fernet(key.encode())


def encrypt_token(token: str) -> str:
    if not token:
        raise ValueError("Token cannot be empty")

    return get_cipher().encrypt(
        token.encode("utf-8")
    ).decode("utf-8")


def decrypt_token(encrypted_token: str) -> str:
    try:
        return get_cipher().decrypt(
            encrypted_token.encode("utf-8")
        ).decode("utf-8")

    except InvalidToken as error:
        raise ValueError(
            "Unable to decrypt Outlook token"
        ) from error
