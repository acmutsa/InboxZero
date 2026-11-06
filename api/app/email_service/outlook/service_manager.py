
from datetime import datetime
from typing import Callable

from app.email_service.outlook.outlook import OutlookService
from app.email_service.outlook.token_manager import OutlookTokenManager


class OutlookServiceManager:
    """
    Provides an authenticated OutlookService.

    Token persistence is delegated to a callback so
    database integration can be added separately.
    """

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
        save_tokens: Callable | None = None,
        token_manager: OutlookTokenManager | None = None,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.save_tokens = save_tokens
        self.token_manager = token_manager or OutlookTokenManager()

    def get_service(self) -> OutlookService:
        tokens = self.token_manager.get_valid_token(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )

        if tokens["refreshed"]:
            # Persist rotated tokens before using them.
            # A real integration must supply save_tokens.
            if self.save_tokens is None:
                raise RuntimeError(
                    "Token persistence is required after refresh"
                )

            self.save_tokens(
                tokens["access_token"],
                tokens["refresh_token"],
                tokens["expires_at"],
            )

            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            self.expires_at = tokens["expires_at"]

        return OutlookService(self.access_token)

