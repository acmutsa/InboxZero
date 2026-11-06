
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class OutlookCredentials:
    user_id: str
    microsoft_account_id: str
    email: str
    access_token: str
    refresh_token: str
    expires_at: datetime


class OutlookAccountStore(Protocol):
    def save(self, account: OutlookCredentials) -> None:
        ...

    def get(
        self,
        user_id: str,
        microsoft_account_id: str,
    ) -> OutlookCredentials | None:
        ...


class InMemoryOutlookAccountStore:
    """
    For unit tests only. Not suitable for production:
    credentials remain in process memory.
    """

    def __init__(self):
        self.accounts = {}

    def save(self, account: OutlookCredentials) -> None:
        key = (account.user_id, account.microsoft_account_id)
        self.accounts[key] = account

    def get(
        self,
        user_id: str,
        microsoft_account_id: str,
    ) -> OutlookCredentials | None:
        return self.accounts.get(
            (user_id, microsoft_account_id)
        )
