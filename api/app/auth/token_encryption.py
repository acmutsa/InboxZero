from cryptography.fernet import Fernet

from app.config import config

_fernet = Fernet(config.GOOGLE_REFRESH_TOKEN_SECRET)


def encrypt(token: str) -> str:
    return _fernet.encrypt(token.encode()).decode()


def decrypt(token: str) -> str:
    return _fernet.decrypt(token.encode()).decode()
