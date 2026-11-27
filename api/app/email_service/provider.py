from abc import ABC
from abc import abstractmethod

from app.email_service.types.category import EmailCategory
from app.email_service.types.category import EmailCategoryCreateRequest
from app.email_service.types.category import EmailCategoryList
from app.email_service.types.draft import EmailReplyDraftRequest
from app.email_service.types.message import EmailMessage
from app.email_service.types.thread import EmailThread
from app.email_service.types.thread import EmailThreadRequest


class EmailProvider(ABC):
    """What the app needs from a mailbox, in provider-neutral types only."""

    @abstractmethod
    def get_message(self, message_id: str) -> EmailMessage: ...

    @abstractmethod
    def get_thread(self, thread_request: EmailThreadRequest) -> EmailThread: ...

    @abstractmethod
    def get_category(self, category_id: str) -> EmailCategory: ...

    @abstractmethod
    def get_categories(self) -> EmailCategoryList: ...

    @abstractmethod
    def create_category(self, category_request: EmailCategoryCreateRequest) -> EmailCategory: ...

    @abstractmethod
    def assign_category(self, message_id: str, category_id: str) -> None: ...

    @abstractmethod
    def create_draft(self, draft_request: EmailReplyDraftRequest) -> str:
        """Create a reply draft and return the provider's draft id."""
